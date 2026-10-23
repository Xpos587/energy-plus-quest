"""Reproduce only the review KV; never writes public assets or aliases."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
original = Image.open(root / 'F0093-original.png').convert('RGB')
corrected = Image.open(root.parent / 'choice-wide-refined.png').convert('RGB')
corrected = corrected.resize((450, 245), Image.Resampling.LANCZOS)
mask = Image.open(root / 'aircraft-shadow-mask.png').convert('L')
original.paste(corrected, (850, 15), mask)
original.save(root / 'F0093-helicopter-corrected.png')
original.crop((850, 15, 1300, 260)).save(root / 'detail-review-100pct.png')
