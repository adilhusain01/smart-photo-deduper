# Photo Duplicate Organizer

A Python script that intelligently finds and organizes duplicate photos based on visual similarity, keeping the highest quality version in place while moving duplicates to a separate folder. Perfect for cleaning up photo collections with different file sizes, formats, and names of the same image.

## Features

- **Smart Detection**: Uses perceptual hashing to identify visually similar images regardless of file size, compression, or format
- **Quality Priority**: Automatically keeps the highest resolution version, or largest file size if resolution is the same
- **Multi-Format Support**: Handles JPEG, PNG, BMP, TIFF, WebP, and HEIC/HEIF (iPhone photos)
- **Two Safe Operation Modes**: 
  - **Preview mode** (default): Safe dry-run to see what would be processed
  - **Organize mode**: Move duplicates to a separate "Duplicates" folder for review
  - **Delete mode**: Permanently remove duplicates (for advanced users)
- **Smart Conflict Resolution**: Handles filename conflicts when moving files
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

**Suggested filename**: `photo_duplicate_organizer.py` (more descriptive)

## Usage

### Basic Usage (Recommended for New Users)

```bash
# Step 1: Preview what would be organized (completely safe)
python duplicate_remover.py /path/to/your/photos

# Step 2: Organize duplicates into "Duplicates" folder (recommended)
python duplicate_remover.py /path/to/your/photos --move-duplicates

# Advanced: Permanently delete duplicates (use with caution)
python duplicate_remover.py /path/to/your/photos --execute
```

### Advanced Options

```bash
# Adjust similarity threshold (0-10, lower = more strict)
python duplicate_remover.py /path/to/photos --similarity 3 --move-duplicates

# More lenient matching (good for different formats/compression)
python duplicate_remover.py /path/to/photos --similarity 8 --move-duplicates

# Very strict matching
python duplicate_remover.py /path/to/photos --similarity 1 --move-duplicates
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `folder` | Path to folder containing images | Required |
| `--execute` | Actually delete duplicate files | False (dry-run) |
| `--move-duplicates` | Move duplicates to "Duplicates" folder | False (dry-run) |
| `--similarity` | Similarity threshold (0-10, lower = more strict) | 5 |

**Note**: `--execute` and `--move-duplicates` are mutually exclusive - you can only use one at a time.

## Operation Modes

### 1. Preview Mode (Default)
- **Command**: `python duplicate_remover.py /path/to/photos`
- **Action**: Shows what would be processed without making any changes
- **Safety**: 100% safe - no files are modified
- **Use**: Perfect for first-time runs to see what duplicates exist

### 2. Organize Mode (Recommended for Everyone)
- **Command**: `python duplicate_remover.py /path/to/photos --move-duplicates`
- **Action**: Moves duplicate files to a "Duplicates" subfolder
- **Safety**: Very safe - you can review and restore files easily
- **Benefits**: 
  - Original files stay in place
  - Duplicates are organized in a separate folder
  - Easy to review before permanent deletion
  - Handles filename conflicts automatically
  - **Perfect for beginners and everyday use**

### 3. Delete Mode (Advanced Users Only)
- **Command**: `python duplicate_remover.py /path/to/photos --execute`
- **Action**: Permanently deletes duplicate files
- **Safety**: ⚠️ **USE WITH EXTREME CAUTION** - files are permanently removed
- **Use**: Only when you're 100% confident about the duplicates
- **Recommendation**: Always use organize mode first, then delete the "Duplicates" folder manually after review

## How It Works

1. **Scans** the specified folder for image files
2. **Analyzes** each image using perceptual hashing (pHash)
3. **Groups** visually similar images together
4. **Selects** the best quality image from each group:
   - Highest resolution (pixel count)
   - If resolution is same, largest file size
5. **Reports** what will be processed and space savings
6. **Processes** duplicates according to chosen mode

## Supported Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **BMP** (.bmp)
- **TIFF** (.tiff)
- **WebP** (.webp)
- **HEIC/HEIF** (.heic, .heif) - iPhone photos (requires pillow-heif)

## Example Output

### Preview Mode
```
Photo Duplicate Organizer
==============================
✓ HEIC/HEIF support enabled
Mode: Dry run (preview only)

Scanning folder: /Users/john/Photos
Found 127 image files
Processing batch 1/2
Processing batch 2/2

Found 12 groups of duplicates:

Group 1 (3 duplicates):
  [KEEP] vacation_sunset_4032x3024.heic - 4032x3024 - 3.2MB
  [MOVE] vacation_sunset_2048x1536.jpg - 2048x1536 - 1.8MB
  [MOVE] vacation_sunset_small.jpg - 1024x768 - 0.5MB

Summary:
Files to organize: 23
Space to organize: 45.67 MB

*** DRY RUN MODE - No files were actually processed ***
Run with --move-duplicates to organize duplicates into 'Duplicates' folder
```

### Organize Mode
```
Photo Duplicate Organizer
==============================
✓ HEIC/HEIF support enabled
Mode: Move duplicates to 'Duplicates' folder

Created folder: /Users/john/Photos/Duplicates

Group 1 (3 duplicates):
  [KEEP] vacation_sunset_4032x3024.heic - 4032x3024 - 3.2MB
  [MOVE] vacation_sunset_2048x1536.jpg - 2048x1536 - 1.8MB
  [MOVE] vacation_sunset_small.jpg - 1024x768 - 0.5MB
    Moved: vacation_sunset_2048x1536.jpg -> Duplicates/vacation_sunset_2048x1536.jpg
    Moved: vacation_sunset_small.jpg -> Duplicates/vacation_sunset_small.jpg

Summary:
Files moved to Duplicates folder: 23
Space organized: 45.67 MB
```

## Use Cases

### Perfect For

- **iPhone Photo Libraries**: Compare HEIC originals with shared JPEG copies
- **Edited Photos**: Keep originals, organize lower-quality exports
- **Downloaded Images**: Organize duplicate downloads in different sizes
- **Social Media**: Clean up photos saved at different resolutions
- **Backup Cleanup**: Merge photo collections from different sources
- **Photo Organization**: Separate originals from duplicates for manual review

### Recommended Workflow (Especially for New Users)

1. **First Run**: Use preview mode to understand what duplicates exist
   ```bash
   python duplicate_remover.py /path/to/photos
   ```
   ✅ **100% Safe** - Nothing is changed

2. **Organize**: Use move mode to separate duplicates
   ```bash
   python duplicate_remover.py /path/to/photos --move-duplicates
   ```
   ✅ **Very Safe** - Files moved to "Duplicates" folder

3. **Review**: Check the "Duplicates" folder to verify the moved files
   - Browse through moved files
   - Restore any files you want to keep

4. **Clean Up**: Delete the "Duplicates" folder when satisfied
   ```bash
   # Only after you've reviewed everything!
   rm -rf /path/to/photos/Duplicates
   ```

**💡 Pro Tip**: Never use `--execute` unless you're 100% sure. The organize mode gives you full control!

### Example Scenarios

1. **Same photo, different sizes**: `IMG_1234.jpg` (3.2MB), `IMG_1234_small.jpg` (800KB)
2. **Same photo, different formats**: `sunset.heic` (iPhone), `sunset.jpg` (shared copy)
3. **Same photo, different names**: `vacation_01.jpg`, `beach_day.jpg`, `IMG_5678.jpg`
4. **Edited versions**: `portrait.raw` (original), `portrait_edited.jpg` (processed)

## Safety Features

- **Dry-run by default**: Never modifies anything unless you specify a mode
- **Move option**: Safest way to handle duplicates - easy to undo
- **Error handling**: Skips corrupted files without crashing
- **Detailed preview**: Shows exactly what will be kept and processed
- **Quality preservation**: Always keeps the highest quality version
- **Conflict resolution**: Automatically handles filename conflicts in Duplicates folder

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
⚠ HEIC/HEIF support not available. Install pillow-heif for HEIC support
```
**Solution**: `pip install pillow-heif`

### Permission Errors
Make sure you have write permissions to the folder containing the images.

### Memory Issues with Large Collections
For folders with 1000+ images, consider processing subdirectories separately.

### Filename Conflicts in Duplicates Folder
The script automatically handles this by adding number suffixes (e.g., `image_1.jpg`, `image_2.jpg`).

## Best Practices

1. **Start with Preview**: Always run in preview mode first to understand what will be processed
2. **Use Organize Mode**: Much safer than direct deletion - you can always review and restore
3. **Backup Important Photos**: Before running any organization, ensure you have backups
4. **Test with Small Folders**: Try the script on a small test folder first
5. **Adjust Similarity**: Start with default threshold (5) and adjust based on results
6. **Review Moved Files**: Always check the "Duplicates" folder before permanently deleting
7. **Avoid --execute**: Only use deletion mode if you're an advanced user and 100% confident

## Contributing

Feel free to submit issues and enhancement requests! This script can be extended with additional features like:
- GUI interface
- Undo functionality
- More hash algorithms
- Video duplicate detection
- Recursive folder processing
- Batch processing multiple folders

## License

This script is provided as-is for personal use. Use at your own risk and always backup your photos before running duplicate removal operations.

## Acknowledgments

- Uses [ImageHash](https://github.com/JohannesBuchner/imagehash) for perceptual hashing
- Uses [Pillow](https://python-pillow.org/) for image processing
- Uses [pillow-heif](https://github.com/bigcat88/pillow_heif) for HEIC support