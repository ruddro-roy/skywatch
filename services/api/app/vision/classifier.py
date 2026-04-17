"""
skywatch CV weather classifier.

MVP: Heuristic classifier using HSV color analysis and Sobel edge density.
No model download required — works out of the box.

v0.2+: EfficientNet-B0 fine-tuned on weather datasets (commented below).
v0.2+: CLIP zero-shot fallback (commented below).

Classes (5): clear, cloudy, fog, rain, snow
"""

import io
import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Type alias
# ─────────────────────────────────────────────

ConditionTuple = Tuple[str, float, str]
# (label, confidence 0–1, method name)

CLASSES = ["clear", "cloudy", "fog", "rain", "snow"]

# ─────────────────────────────────────────────
# Heuristic thresholds
# (tuned empirically — adjust per deployment environment)
# ─────────────────────────────────────────────

_H_BLUE_LOW, _H_BLUE_HIGH = 90, 130   # HSV hue range for sky blue
_H_GREY_LOW, _H_GREY_HIGH = 0, 180    # Grey = low saturation regardless of hue

# Snow: very bright + very low saturation
_SNOW_VALUE_MIN = 0.75
_SNOW_SAT_MAX = 0.15

# Fog: moderate brightness + very low saturation
_FOG_VALUE_MIN = 0.55
_FOG_SAT_MAX = 0.12

# Clear: high value + moderate saturation (sky visible)
_CLEAR_VALUE_MIN = 0.6
_CLEAR_SAT_MIN = 0.15

# Rain: low value OR high edge density
_RAIN_VALUE_MAX = 0.45
_RAIN_EDGE_MIN = 0.12  # Sobel edge density threshold for rain texture


class WeatherClassifier:
    """
    Weather condition classifier.

    MVP uses a heuristic approach (HSV + edge density).
    Drop-in replacement planned for v0.2 using EfficientNet-B0.
    """

    def __init__(self) -> None:
        self._model: Optional[object] = None  # Placeholder for neural model
        self._method = "heuristic"
        self._try_load_model()

    def _try_load_model(self) -> None:
        """
        Attempt to load a neural network classifier.

        Tries:
        1. EfficientNet-B0 with a local checkpoint (MODEL_PATH env var)
        2. CLIP zero-shot via open_clip

        Falls back to heuristic if neither is available.
        """
        # ── Attempt 1: EfficientNet-B0 fine-tuned checkpoint ──────────────
        # TODO (v0.2): Uncomment and implement after training
        #
        # import os
        # checkpoint_path = os.environ.get("WEATHER_MODEL_PATH", "")
        # if checkpoint_path and os.path.exists(checkpoint_path):
        #     try:
        #         import torch
        #         import torchvision.models as models
        #
        #         model = models.efficientnet_b0(weights=None)
        #         # Replace classifier head for 5 classes
        #         in_features = model.classifier[1].in_features
        #         model.classifier = torch.nn.Sequential(
        #             torch.nn.Dropout(p=0.2, inplace=True),
        #             torch.nn.Linear(in_features, 256),
        #             torch.nn.ReLU(),
        #             torch.nn.Linear(256, 5),
        #         )
        #         state = torch.load(checkpoint_path, map_location="cpu")
        #         model.load_state_dict(state)
        #         model.eval()
        #         self._model = model
        #         self._method = "efficientnet"
        #         logger.info("Loaded EfficientNet-B0 weather classifier from %s", checkpoint_path)
        #         return
        #     except Exception as exc:
        #         logger.warning("Failed to load EfficientNet checkpoint: %s", exc)

        # ── Attempt 2: CLIP zero-shot ──────────────────────────────────────
        # TODO (v0.2): Uncomment after installing open_clip_torch
        #
        # try:
        #     import open_clip
        #     clip_model, _, preprocess = open_clip.create_model_and_transforms(
        #         "ViT-B-32", pretrained="openai"
        #     )
        #     tokenizer = open_clip.get_tokenizer("ViT-B-32")
        #     clip_model.eval()
        #     self._model = {
        #         "model": clip_model,
        #         "preprocess": preprocess,
        #         "tokenizer": tokenizer,
        #     }
        #     self._method = "clip"
        #     logger.info("Loaded CLIP zero-shot weather classifier")
        #     return
        # except ImportError:
        #     logger.debug("open_clip not installed — CLIP classifier unavailable")
        # except Exception as exc:
        #     logger.warning("Failed to initialise CLIP classifier: %s", exc)

        # ── Fallback: Heuristic ────────────────────────────────────────────
        logger.info("Using heuristic CV classifier (HSV + Sobel edge density)")
        self._method = "heuristic"

    def classify(self, image_bytes: bytes) -> ConditionTuple:
        """
        Classify weather conditions from an image.

        Args:
            image_bytes: Raw JPEG/PNG image bytes.

        Returns:
            Tuple of (label, confidence, method).
            label is one of: clear, cloudy, fog, rain, snow
            confidence is 0.0–1.0
            method is: heuristic, efficientnet, or clip
        """
        if self._method == "efficientnet" and self._model is not None:
            return self._classify_efficientnet(image_bytes)
        if self._method == "clip" and self._model is not None:
            return self._classify_clip(image_bytes)
        return self._classify_heuristic(image_bytes)

    def _classify_heuristic(self, image_bytes: bytes) -> ConditionTuple:
        """
        Heuristic classifier using HSV color statistics and Sobel edge density.

        Pipeline:
        1. Load image and resize to 224×224
        2. Convert to HSV colour space
        3. Compute mean and std of H, S, V channels
        4. Compute edge density via Sobel gradient approximation
        5. Apply rule-based classification

        Heuristic rules (empirically tuned):
        - Snow:   high V (brightness) + very low S (desaturation)
        - Fog:    moderate-high V + very low S + low edge density
        - Clear:  high V + moderate S + (blue hue present)
        - Rain:   low V OR high edge density (rain streak texture)
        - Cloudy: moderate V + low-moderate S (grey sky)
        """
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            logger.debug("Failed to open image: %s", exc)
            return ("unknown", 0.0, "heuristic")

        # Resize to standard size for consistent statistics
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0  # Normalise to 0–1

        # Convert RGB to HSV
        h, s, v = _rgb_to_hsv_arrays(arr[:, :, 0], arr[:, :, 1], arr[:, :, 2])

        mean_s = float(np.mean(s))
        mean_v = float(np.mean(v))
        std_v = float(np.std(v))

        # Edge density via Sobel approximation
        edge_density = _sobel_edge_density(v)

        # ── Classification rules ──────────────────────────────────────────

        # Snow: very bright, desaturated
        if mean_v >= _SNOW_VALUE_MIN and mean_s <= _SNOW_SAT_MAX:
            confidence = _scale(mean_v, _SNOW_VALUE_MIN, 1.0) * _scale(
                _SNOW_SAT_MAX - mean_s, 0, _SNOW_SAT_MAX
            )
            return ("snow", float(min(0.95, 0.5 + confidence)), "heuristic")

        # Fog: moderately bright, very desaturated, smooth (low edge density)
        if (
            mean_v >= _FOG_VALUE_MIN
            and mean_s <= _FOG_SAT_MAX
            and edge_density < 0.05
        ):
            confidence = _scale(mean_v, _FOG_VALUE_MIN, 0.85) * (1.0 - edge_density / 0.05)
            return ("fog", float(min(0.90, 0.45 + confidence)), "heuristic")

        # Clear: bright + some saturation (sky colour present)
        if mean_v >= _CLEAR_VALUE_MIN and mean_s >= _CLEAR_SAT_MIN:
            # Check for blue-ish sky hue presence
            blue_mask = (h >= _H_BLUE_LOW) & (h <= _H_BLUE_HIGH) & (s > 0.2)
            blue_fraction = float(np.mean(blue_mask))
            confidence = _scale(mean_v, _CLEAR_VALUE_MIN, 1.0) * (
                0.5 + 0.5 * min(1.0, blue_fraction * 4)
            )
            return ("clear", float(min(0.95, 0.45 + confidence)), "heuristic")

        # Rain: dark image OR high edge density (streak texture)
        if mean_v <= _RAIN_VALUE_MAX or edge_density >= _RAIN_EDGE_MIN:
            confidence = max(
                _scale(_RAIN_VALUE_MAX - mean_v, 0, _RAIN_VALUE_MAX),
                _scale(edge_density - _RAIN_EDGE_MIN, 0, 0.3),
            )
            return ("rain", float(min(0.85, 0.4 + confidence)), "heuristic")

        # Default: cloudy (moderate brightness, moderate desaturation)
        confidence = 0.5 + 0.1 * (1.0 - abs(mean_v - 0.5) / 0.5)
        return ("cloudy", float(min(0.80, confidence)), "heuristic")

    def _classify_efficientnet(self, image_bytes: bytes) -> ConditionTuple:
        """
        EfficientNet-B0 classifier.
        TODO (v0.2): Implement after training. See scripts/train_classifier.py.
        """
        # Placeholder — falls back to heuristic until model is trained
        return self._classify_heuristic(image_bytes)

    def _classify_clip(self, image_bytes: bytes) -> ConditionTuple:
        """
        CLIP zero-shot classifier.
        TODO (v0.2): Implement after installing open_clip_torch.
        """
        # TODO (v0.2):
        # model_data = self._model
        # clip_model = model_data["model"]
        # preprocess = model_data["preprocess"]
        # tokenizer = model_data["tokenizer"]
        #
        # import torch
        # img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # image_input = preprocess(img).unsqueeze(0)
        #
        # prompts = [
        #     "a photo taken in clear sunny weather",
        #     "a photo taken in cloudy overcast weather",
        #     "a photo taken in foggy misty weather",
        #     "a photo taken in rainy wet weather",
        #     "a photo taken in snowy winter weather",
        # ]
        # text_tokens = tokenizer(prompts)
        #
        # with torch.no_grad():
        #     image_features = clip_model.encode_image(image_input)
        #     text_features = clip_model.encode_text(text_tokens)
        #     image_features /= image_features.norm(dim=-1, keepdim=True)
        #     text_features /= text_features.norm(dim=-1, keepdim=True)
        #     similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        #
        # probs = similarity[0].numpy()
        # best_idx = int(probs.argmax())
        # return (CLASSES[best_idx], float(probs[best_idx]), "clip")
        return self._classify_heuristic(image_bytes)


# ─────────────────────────────────────────────
# Numerical helpers
# ─────────────────────────────────────────────


def _rgb_to_hsv_arrays(
    r: np.ndarray, g: np.ndarray, b: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert R, G, B arrays (0–1) to H (0–180), S (0–1), V (0–1).

    Uses vectorised numpy operations for performance.
    """
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    diff = max_c - min_c

    v = max_c
    s = np.where(max_c > 0, diff / max_c, 0.0)

    # Hue calculation
    h = np.zeros_like(r)
    mask_r = (max_c == r) & (diff > 0)
    mask_g = (max_c == g) & (diff > 0)
    mask_b = (max_c == b) & (diff > 0)

    h[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r])) % 360
    h[mask_g] = 60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120
    h[mask_b] = 60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240

    return h / 2, s, v  # H in 0–180 to match OpenCV convention


def _sobel_edge_density(v: np.ndarray) -> float:
    """
    Compute normalised Sobel edge density from a value (brightness) channel.

    Higher values indicate more edges/texture — characteristic of rain streaks.
    Uses a simple Sobel approximation via array slicing (no scipy required).
    """
    # Sobel X
    sx = v[1:-1, 2:] - v[1:-1, :-2]
    # Sobel Y
    sy = v[2:, 1:-1] - v[:-2, 1:-1]

    magnitude = np.sqrt(sx ** 2 + sy ** 2)
    return float(np.mean(magnitude))


def _scale(value: float, low: float, high: float) -> float:
    """Linearly scale value from [low, high] to [0, 1], clamped."""
    if high == low:
        return 0.0
    return float(max(0.0, min(1.0, (value - low) / (high - low))))
