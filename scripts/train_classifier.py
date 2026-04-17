#!/usr/bin/env python3
"""
skywatch weather image classifier training script.

Trains an EfficientNet-B0 model to classify webcam images into 5 weather conditions:
clear, cloudy, fog, rain, snow

This script is a reference implementation — it is NOT required to run the MVP.
The API falls back to the heuristic classifier (HSV + Sobel) without a trained model.

Usage:
    python scripts/train_classifier.py \
        --data-dir ./data/weather_images \
        --output-dir ./models \
        --epochs 30 \
        --batch-size 32

Data preparation:
    Organise images in this structure:
    data/weather_images/
    ├── train/
    │   ├── clear/     (FWID sun/, FWID clear/, MWD shine/)
    │   ├── cloudy/    (FWID overcast/, FWID cloudy/, MWD cloudy/)
    │   ├── fog/       (FWID haze/, FWID fog/)
    │   ├── rain/      (FWID rain/, FWID shower/, MWD rain/)
    │   └── snow/      (FWID snow/, FWID sleet/)
    └── val/
        ├── clear/
        ├── cloudy/
        ├── fog/
        ├── rain/
        └── snow/

Datasets:
    FWID (Flickr Weather Image Dataset):
        URL: https://github.com/wzgwzg/FWID
        License: CC BY-NC 4.0
        Classes: 10 (requires remapping — see CLASS_MAP below)

    Kaggle Weather Recognition:
        URL: https://www.kaggle.com/datasets/jehanbhathena/weather-dataset
        License: CC0
        Download: kaggle datasets download -d jehanbhathena/weather-dataset

    MWD (Multi-class Weather Dataset):
        URL: https://www.kaggle.com/datasets/pratik2901/multiclass-weather-dataset
        License: CC BY 4.0

Requirements (install separately — not in requirements.txt by default):
    pip install torch torchvision tqdm tensorboard

After training, activate the model:
    export WEATHER_MODEL_PATH=/path/to/models/weather_classifier_efficientnet_b0.pt
    # Then restart the API server
"""

import argparse
import os
import time
from pathlib import Path

# ─────────────────────────────────────────────
# Class mapping from dataset labels to our 5 classes
# ─────────────────────────────────────────────

CLASS_MAP = {
    # FWID classes
    "sun": "clear",
    "clear": "clear",
    "sunrise": "clear",
    "shine": "clear",
    "haze": "fog",
    "fog": "fog",
    "mist": "fog",
    "overcast": "cloudy",
    "cloudy": "cloudy",
    "cloud": "cloudy",
    "rain": "rain",
    "shower": "rain",
    "rainy": "rain",
    "snow": "snow",
    "sleet": "snow",
    "snowy": "snow",
    "frost": "snow",
}

CLASSES = ["clear", "cloudy", "fog", "rain", "snow"]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train EfficientNet-B0 weather classifier",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data/weather_images"),
        help="Path to dataset directory (train/ and val/ subdirs)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./models"),
        help="Output directory for checkpoints",
    )
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument(
        "--freeze-backbone",
        action="store_true",
        help="Freeze backbone weights (faster training, lower accuracy)",
    )
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Training device",
    )
    return parser.parse_args()


def train(args: argparse.Namespace) -> None:
    """Main training function."""
    # ── Imports (deferred to avoid ImportError if torch not installed) ────
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.optim.lr_scheduler import CosineAnnealingLR
        from torch.utils.data import DataLoader
        from torchvision import datasets, models, transforms
        from tqdm import tqdm
    except ImportError as e:
        print(f"Error: Required package not installed: {e}")
        print("Install with: pip install torch torchvision tqdm")
        return

    # ── Device ────────────────────────────────────────────────────────────
    if args.device == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        device = torch.device(args.device)

    print(f"Training on device: {device}")

    # ── Data transforms ───────────────────────────────────────────────────
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # ── Datasets ─────────────────────────────────────────────────────────
    train_dir = args.data_dir / "train"
    val_dir = args.data_dir / "val"

    if not train_dir.exists():
        print(f"Error: Training data not found at {train_dir}")
        print("See module docstring for data preparation instructions.")
        return

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Classes: {train_dataset.classes}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    # ── Model ─────────────────────────────────────────────────────────────
    from torchvision.models import EfficientNet_B0_Weights
    model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)

    if args.freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False
        print("Backbone frozen — training head only")

    # Replace classifier head
    in_features = model.classifier[1].in_features  # 1280
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Linear(256, len(CLASSES)),
    )

    model = model.to(device)

    # ── Training setup ────────────────────────────────────────────────────
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    best_val_acc = 0.0
    patience = 5
    patience_counter = 0

    # ── Training loop ─────────────────────────────────────────────────────
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            train_correct += predicted.eq(labels).sum().item()
            train_total += labels.size(0)

        scheduler.step()

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_correct += predicted.eq(labels).sum().item()
                val_total += labels.size(0)

        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        avg_train_loss = train_loss / train_total
        avg_val_loss = val_loss / val_total

        print(
            f"Epoch {epoch:3d}/{args.epochs} | "
            f"Train Loss: {avg_train_loss:.4f} Acc: {train_acc:.3f} | "
            f"Val Loss: {avg_val_loss:.4f} Acc: {val_acc:.3f}"
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            checkpoint_path = args.output_dir / "weather_classifier_efficientnet_b0.pt"
            torch.save(model.state_dict(), checkpoint_path)
            print(f"  ✓ New best model saved to {checkpoint_path} (val_acc={val_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch} (no improvement for {patience} epochs)")
                break

    print(f"\nTraining complete. Best validation accuracy: {best_val_acc:.4f}")
    print(f"Model saved to: {args.output_dir / 'weather_classifier_efficientnet_b0.pt'}")
    print(f"\nTo activate: export WEATHER_MODEL_PATH={args.output_dir / 'weather_classifier_efficientnet_b0.pt'}")


if __name__ == "__main__":
    args = parse_args()
    train(args)
