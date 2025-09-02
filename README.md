# Image Duplicate Remover

A Python script that intelligently finds and removes duplicate images based on visual similarity, keeping the highest quality version. Perfect for cleaning up photo collections with different file sizes, formats, and names of the same image.

## Features

- **Smart Detection**: Uses perceptual hashing to identify visually similar images regardless of file size, compression, or format
- **Quality Priority**: Automatically keeps the highest resolution version, or largest file size if resolution is the same
- **Multi-Format Support**: Handles JPEG, PNG, BMP, TIFF, WebP, and HEIC/HEIF (iPhone photos)
- **Safe Operation**: Dry-run mode by default - preview what will be deleted before actually removing files
- **Adjustable Sensitivity**: Customize similarity threshold for strict or lenient matching
- **Detailed Reporting**: Shows file sizes, dimensions, and space savings

## Installation

### Requirements
- Python 3.6 or higher

### Install Dependencies

```bash
# Basic installation (without HEIC support)
pip install Pillow imagehash

# Full installation (with HEIC/iPhone photo support)
pip install Pillow imagehash pillow-heif
```

### Download Script

Save the `duplicate_remover.py` script to your computer.

## Usage

### Basic Usage

```bash
# Preview what would be removed (safe mode)
python duplicate_remover.py /path/to/your/photos

# Actually remove duplicates
python duplicate_remover.py /path/to/your/photos --execute
```

### Advanced Options

```bash
# Adjust similarity threshold (0-10, lower = more strict)
python duplicate_remover.py /path/to/photos --similarity 3

# More lenient matching (good for different formats/compression)
python duplicate_remover.py /path/to/photos --similarity 8

# Combine options
python duplicate_remover.py /path/to/photos --similarity 5 --execute
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `folder` | Path to folder containing images | Required |
| `--execute` | Actually delete files (default is dry-run) | False |
| `--similarity` | Similarity threshold (0-10, lower = more strict) | 5 |

## How It Works

1. **Scans** the specified folder for image files
2. **Analyzes** each image using perceptual hashing (pHash)
3. **Groups** visually similar images together
4. **Selects** the best quality image from each group:
   - Highest resolution (pixel count)
   - If resolution is same, largest file size
5. **Reports** what will be removed and space saved
6. **Removes** duplicates (only if `--execute` is used)

## Supported Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **BMP** (.bmp)
- **TIFF** (.tiff)
- **WebP** (.webp)
- **HEIC/HEIF** (.heic, .heif) - iPhone photos (requires pillow-heif)

## Example Output

```
Image Duplicate Remover
==============================
Scanning folder: /Users/john/Photos
Found 127 image files
Processing 1/127: IMG_1234.jpg
Processing 2/127: IMG_1234_edited.png
...

Found 12 groups of duplicates:

Group 1 (3 duplicates):
  [KEEP] vacation_sunset_4032x3024.heic - 4032x3024 - 3.2MB
  [REMOVE] vacation_sunset_2048x1536.jpg - 2048x1536 - 1.8MB
  [REMOVE] vacation_sunset_small.jpg - 1024x768 - 0.5MB

Group 2 (2 duplicates):
  [KEEP] family_photo_original.png - 3000x2000 - 4.1MB
  [REMOVE] family_photo_compressed.jpg - 3000x2000 - 2.3MB

...

Summary:
Files to remove: 23
Space to save: 45.67 MB

*** DRY RUN MODE - No files were actually deleted ***
Run with --execute to actually remove the duplicates
```

## Use Cases

### Perfect For

- **iPhone Photo Libraries**: Compare HEIC originals with shared JPEG copies
- **Edited Photos**: Keep originals, remove lower-quality exports
- **Downloaded Images**: Remove duplicate downloads in different sizes
- **Social Media**: Clean up photos saved at different resolutions
- **Backup Cleanup**: Merge photo collections from different sources

### Example Scenarios

1. **Same photo, different sizes**: `IMG_1234.jpg` (3.2MB), `IMG_1234_small.jpg` (800KB)
2. **Same photo, different formats**: `sunset.heic` (iPhone), `sunset.jpg` (shared copy)
3. **Same photo, different names**: `vacation_01.jpg`, `beach_day.jpg`, `IMG_5678.jpg`
4. **Edited versions**: `portrait.raw` (original), `portrait_edited.jpg` (processed)

## Safety Features

- **Dry-run by default**: Never deletes anything unless you use `--execute`
- **Error handling**: Skips corrupted files without crashing
- **Detailed preview**: Shows exactly what will be kept and removed
- **Quality preservation**: Always keeps the highest quality version

## Similarity Threshold Guide

| Value | Description | Use Case |
|-------|-------------|----------|
| 0-2 | Very strict | Nearly identical images only |
| 3-5 | Moderate | Default - good balance |
| 6-8 | Lenient | Different compression/formats |
| 9-10 | Very lenient | Heavily edited versions |

## Troubleshooting

### HEIC Files Not Supported
```
HEIC/HEIF support not available. Install pillow-heif for HEIC support
```
**Solution**: `pip install pillow-heif`

### Permission Errors
Make sure you have write permissions to the folder containing the images.

### Memory Issues with Large Collections
For folders with 1000+ images, consider processing subdirectories separately.

## Contributing

Feel free to submit issues and enhancement requests! This script can be extended with additional features like:
- GUI interface
- Undo functionality
- More hash algorithms
- Video duplicate detection
- Recursive folder processing

## License

This script is provided as-is for personal use. Use at your own risk and always backup your photos before running duplicate removal operations.

## Acknowledgments

- Uses [ImageHash](https://github.com/JohannesBuchner/imagehash) for perceptual hashing
- Uses [Pillow](https://python-pillow.org/) for image processing
- Uses [pillow-heif](https://github.com/bigcat88/pillow_heif) for HEIC support