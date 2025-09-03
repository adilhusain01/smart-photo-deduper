#!/usr/bin/env python3
"""
Image Duplicate Remover
Finds and removes duplicate images based on perceptual hashing, keeping the highest quality version.
Now supports moving duplicates to a separate folder instead of deleting them.
"""

import os
import shutil
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict
import argparse

# Try to import and register HEIC support
HEIC_SUPPORT = False
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    pass

def get_image_info(filepath):
    """Get image information including file size, dimensions, and perceptual hash."""
    try:
        # Handle HEIC files specifically
        if filepath.lower().endswith(('.heic', '.heif')) and not HEIC_SUPPORT:
            print(f"Skipping {filepath}: HEIC support not installed")
            return None
            
        with Image.open(filepath) as img:
            # Convert HEIC to RGB if needed for better hash consistency
            if img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
                
            # Calculate perceptual hash (detects similar images even with different compression)
            phash = str(imagehash.phash(img))
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Get image dimensions
            width, height = img.size
            pixel_count = width * height
            
            return {
                'path': filepath,
                'phash': phash,
                'file_size': file_size,
                'dimensions': (width, height),
                'pixel_count': pixel_count
            }
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def find_duplicates(folder_path, similarity_threshold=5):
    """
    Find duplicate images in a folder.
    similarity_threshold: Lower values = more strict matching (0-10 range)
    """
    print(f"Scanning folder: {folder_path}")
    
    # Supported image extensions - NOW INCLUDING HEIC/HEIF
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
    
    # Get all image files
    image_files = []
    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            image_files.append(os.path.join(folder_path, filename))
    
    print(f"Found {len(image_files)} image files")
    
    # Process all images
    image_info = []
    for i, filepath in enumerate(image_files, 1):
        print(f"Processing {i}/{len(image_files)}: {os.path.basename(filepath)}")
        info = get_image_info(filepath)
        if info:
            image_info.append(info)
    
    # Group similar images
    duplicate_groups = []
    processed = set()
    
    for i, img1 in enumerate(image_info):
        if img1['path'] in processed:
            continue
            
        group = [img1]
        processed.add(img1['path'])
        
        # Compare with remaining images
        for j, img2 in enumerate(image_info[i+1:], i+1):
            if img2['path'] in processed:
                continue
                
            # Calculate hash difference
            hash1 = imagehash.hex_to_hash(img1['phash'])
            hash2 = imagehash.hex_to_hash(img2['phash'])
            difference = hash1 - hash2
            
            if difference <= similarity_threshold:
                group.append(img2)
                processed.add(img2['path'])
        
        if len(group) > 1:
            duplicate_groups.append(group)
    
    return duplicate_groups

def select_best_image(group):
    """
    Select the best image from a group of duplicates.
    Priority: 1. Highest resolution, 2. Largest file size
    """
    best = max(group, key=lambda x: (x['pixel_count'], x['file_size']))
    return best

def create_duplicates_folder(base_path):
    """Create a 'Duplicates' folder in the base path if it doesn't exist."""
    duplicates_folder = os.path.join(base_path, "Duplicates")
    if not os.path.exists(duplicates_folder):
        os.makedirs(duplicates_folder)
        print(f"Created folder: {duplicates_folder}")
    return duplicates_folder

def handle_duplicate_filename(target_path):
    """Handle filename conflicts when moving files to duplicates folder."""
    if not os.path.exists(target_path):
        return target_path
    
    # If file exists, add a number suffix
    base, ext = os.path.splitext(target_path)
    counter = 1
    
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    
    return f"{base}_{counter}{ext}"

def remove_duplicates(folder_path, dry_run=True, move_to_duplicates=False, similarity_threshold=5):
    """
    Remove duplicate images, keeping the highest quality version.
    Can either delete duplicates or move them to a 'Duplicates' folder.
    """
    duplicate_groups = find_duplicates(folder_path, similarity_threshold)
    
    if not duplicate_groups:
        print("No duplicates found!")
        return
    
    print(f"\nFound {len(duplicate_groups)} groups of duplicates:")
    
    # Create duplicates folder if needed
    duplicates_folder = None
    if move_to_duplicates and not dry_run:
        duplicates_folder = create_duplicates_folder(folder_path)
    
    total_files_to_process = 0
    total_space_saved = 0
    action_word = "MOVE" if move_to_duplicates else "DELETE"
    
    for i, group in enumerate(duplicate_groups, 1):
        print(f"\nGroup {i} ({len(group)} duplicates):")
        
        # Select best image
        best_image = select_best_image(group)
        
        for img in group:
            status = "KEEP" if img == best_image else action_word
            size_mb = img['file_size'] / (1024 * 1024)
            print(f"  [{status}] {os.path.basename(img['path'])} - {img['dimensions'][0]}x{img['dimensions'][1]} - {size_mb:.2f}MB")
            
            if img != best_image:
                total_files_to_process += 1
                total_space_saved += img['file_size']
        
        # Process duplicates (if not dry run)
        if not dry_run:
            for img in group:
                if img != best_image:
                    try:
                        if move_to_duplicates:
                            # Move to duplicates folder
                            filename = os.path.basename(img['path'])
                            target_path = os.path.join(duplicates_folder, filename)
                            
                            # Handle filename conflicts
                            target_path = handle_duplicate_filename(target_path)
                            
                            shutil.move(img['path'], target_path)
                            print(f"    Moved: {filename} -> Duplicates/{os.path.basename(target_path)}")
                        else:
                            # Delete the file
                            os.remove(img['path'])
                            print(f"    Deleted: {os.path.basename(img['path'])}")
                    except Exception as e:
                        action = "moving" if move_to_duplicates else "deleting"
                        print(f"    Error {action} {img['path']}: {e}")
    
    space_saved_mb = total_space_saved / (1024 * 1024)
    print(f"\nSummary:")
    if move_to_duplicates:
        print(f"Files to move to Duplicates folder: {total_files_to_process}")
        print(f"Space to organize: {space_saved_mb:.2f} MB")
    else:
        print(f"Files to delete: {total_files_to_process}")
        print(f"Space to save: {space_saved_mb:.2f} MB")
    
    if dry_run:
        print("\n*** DRY RUN MODE - No files were actually processed ***")
        if move_to_duplicates:
            print("Run with --move-duplicates to move duplicates to 'Duplicates' folder")
        else:
            print("Run with --execute to actually remove the duplicates")
            print("Or use --move-duplicates to move them to 'Duplicates' folder instead")

def main():
    parser = argparse.ArgumentParser(description='Remove duplicate images from a folder')
    parser.add_argument('folder', help='Path to folder containing images')
    
    # Create mutually exclusive group for action options
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--execute', action='store_true', 
                             help='Actually delete duplicate files (default is dry-run)')
    action_group.add_argument('--move-duplicates', action='store_true',
                             help='Move duplicates to "Duplicates" folder instead of deleting them')
    
    parser.add_argument('--similarity', type=int, default=5, 
                       help='Similarity threshold (0-10, lower = more strict)')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        return
    
    print("Image Duplicate Remover")
    print("=" * 30)
    
    # Show HEIC support status
    if HEIC_SUPPORT:
        print("✓ HEIC/HEIF support enabled")
    else:
        print("⚠ HEIC/HEIF support not available. Install pillow-heif for HEIC support:")
        print("  pip install pillow-heif")
    
    # Determine mode
    if args.move_duplicates:
        print("Mode: Move duplicates to 'Duplicates' folder")
        dry_run = False
        move_to_duplicates = True
    elif args.execute:
        print("Mode: Delete duplicates")
        dry_run = False
        move_to_duplicates = False
    else:
        print("Mode: Dry run (preview only)")
        dry_run = True
        move_to_duplicates = False
    
    print()
    
    remove_duplicates(args.folder, dry_run=dry_run, move_to_duplicates=move_to_duplicates, 
                     similarity_threshold=args.similarity)

if __name__ == "__main__":
    main()