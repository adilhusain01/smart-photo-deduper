#!/usr/bin/env python3
"""
Memory-Optimized Image Duplicate Remover
Optimized for processing large datasets (10k+ images) with minimal RAM usage.
Uses streaming processing, efficient data structures, and batch operations.
"""

import os
import shutil
import gc
from PIL import Image
import imagehash
from collections import defaultdict
import argparse
import sqlite3
import tempfile
from contextlib import contextmanager
import heapq
from typing import Dict, List, Tuple, Optional, Iterator
import json

# Try to import and register HEIC support
HEIC_SUPPORT = False
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    pass

class ImageProcessor:
    """Memory-efficient image processor using streaming and temporary database."""
    
    def __init__(self, similarity_threshold: int = 5, batch_size: int = 100):
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
        self.temp_db = None
    
    @contextmanager
    def temp_database(self):
        """Create temporary SQLite database for storing image metadata."""
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(db_fd)
            self.temp_db = sqlite3.connect(db_path)
            self.temp_db.execute('''
                CREATE TABLE images (
                    id INTEGER PRIMARY KEY,
                    path TEXT UNIQUE,
                    phash TEXT,
                    file_size INTEGER,
                    width INTEGER,
                    height INTEGER,
                    pixel_count INTEGER
                )
            ''')
            self.temp_db.execute('CREATE INDEX idx_phash ON images(phash)')
            yield self.temp_db
        finally:
            if self.temp_db:
                self.temp_db.close()
            try:
                os.unlink(db_path)
            except:
                pass
    
    def get_image_files(self, folder_path: str) -> Iterator[str]:
        """Generator that yields image file paths."""
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in self.supported_extensions):
                yield os.path.join(folder_path, filename)
    
    def process_image_batch(self, image_paths: List[str]) -> List[Dict]:
        """Process a batch of images and return their metadata."""
        batch_results = []
        
        for filepath in image_paths:
            try:
                # Handle HEIC files specifically
                if filepath.lower().endswith(('.heic', '.heif')) and not HEIC_SUPPORT:
                    print(f"Skipping {filepath}: HEIC support not installed")
                    continue
                
                with Image.open(filepath) as img:
                    # Convert to RGB if needed
                    if img.mode not in ['RGB', 'L']:
                        img = img.convert('RGB')
                    
                    # Calculate perceptual hash
                    phash = str(imagehash.phash(img))
                    
                    # Get file info
                    file_size = os.path.getsize(filepath)
                    width, height = img.size
                    pixel_count = width * height
                    
                    batch_results.append({
                        'path': filepath,
                        'phash': phash,
                        'file_size': file_size,
                        'width': width,
                        'height': height,
                        'pixel_count': pixel_count
                    })
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
        
        return batch_results
    
    def store_batch_in_db(self, batch_data: List[Dict]):
        """Store batch data in temporary database."""
        if not self.temp_db:
            return
        
        data_tuples = [
            (item['path'], item['phash'], item['file_size'], 
             item['width'], item['height'], item['pixel_count'])
            for item in batch_data
        ]
        
        self.temp_db.executemany(
            'INSERT OR IGNORE INTO images (path, phash, file_size, width, height, pixel_count) VALUES (?, ?, ?, ?, ?, ?)',
            data_tuples
        )
        self.temp_db.commit()
    
    def find_duplicates_optimized(self, folder_path: str) -> List[List[Dict]]:
        """Memory-efficient duplicate detection using temporary database."""
        print(f"Scanning folder: {folder_path}")
        
        with self.temp_database() as db:
            # Process images in batches
            image_files = list(self.get_image_files(folder_path))
            total_files = len(image_files)
            print(f"Found {total_files} image files")
            
            # Process in batches to control memory usage
            for i in range(0, total_files, self.batch_size):
                batch = image_files[i:i + self.batch_size]
                print(f"Processing batch {i//self.batch_size + 1}/{(total_files + self.batch_size - 1)//self.batch_size}")
                
                batch_data = self.process_image_batch(batch)
                self.store_batch_in_db(batch_data)
                
                # Force garbage collection after each batch
                gc.collect()
            
            # Find duplicates using efficient hash-based grouping
            return self._find_hash_groups()
    
    def _find_hash_groups(self) -> List[List[Dict]]:
        """Find duplicate groups using hash similarity with optimized algorithm."""
        duplicate_groups = []
        processed_hashes = set()
        
        # Get all unique hashes
        cursor = self.temp_db.execute('SELECT DISTINCT phash FROM images')
        all_hashes = [row[0] for row in cursor.fetchall()]
        
        print(f"Comparing {len(all_hashes)} unique hashes...")
        
        for i, hash1 in enumerate(all_hashes):
            if hash1 in processed_hashes:
                continue
            
            # Get all images with this hash
            cursor = self.temp_db.execute(
                'SELECT path, phash, file_size, width, height, pixel_count FROM images WHERE phash = ?',
                (hash1,)
            )
            group = [dict(zip(['path', 'phash', 'file_size', 'width', 'height', 'pixel_count'], row))
                    for row in cursor.fetchall()]
            
            processed_hashes.add(hash1)
            
            # Find similar hashes using optimized comparison
            hash1_obj = imagehash.hex_to_hash(hash1)
            
            for j, hash2 in enumerate(all_hashes[i+1:], i+1):
                if hash2 in processed_hashes:
                    continue
                
                hash2_obj = imagehash.hex_to_hash(hash2)
                if hash1_obj - hash2_obj <= self.similarity_threshold:
                    # Add images with similar hash to group
                    cursor = self.temp_db.execute(
                        'SELECT path, phash, file_size, width, height, pixel_count FROM images WHERE phash = ?',
                        (hash2,)
                    )
                    similar_images = [dict(zip(['path', 'phash', 'file_size', 'width', 'height', 'pixel_count'], row))
                                     for row in cursor.fetchall()]
                    group.extend(similar_images)
                    processed_hashes.add(hash2)
            
            # Add pixel_count for compatibility
            for img in group:
                img['pixel_count'] = img['width'] * img['height']
                img['dimensions'] = (img['width'], img['height'])
            
            if len(group) > 1:
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def select_best_image(self, group: List[Dict]) -> Dict:
        """Select the best image using a priority queue approach."""
        # Use negative values for max heap behavior
        heap = []
        for img in group:
            priority = (-img['pixel_count'], -img['file_size'], img['path'])
            heapq.heappush(heap, (priority, img))
        
        return heapq.heappop(heap)[1]

class DuplicateRemover:
    """Main class for duplicate removal operations."""
    
    def __init__(self, processor: ImageProcessor):
        self.processor = processor
    
    def create_duplicates_folder(self, base_path: str) -> str:
        """Create a 'Duplicates' folder in the base path if it doesn't exist."""
        duplicates_folder = os.path.join(base_path, "Duplicates")
        if not os.path.exists(duplicates_folder):
            os.makedirs(duplicates_folder)
            print(f"Created folder: {duplicates_folder}")
        return duplicates_folder
    
    def handle_duplicate_filename(self, target_path: str) -> str:
        """Handle filename conflicts when moving files to duplicates folder."""
        if not os.path.exists(target_path):
            return target_path
        
        base, ext = os.path.splitext(target_path)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def remove_duplicates(self, folder_path: str, dry_run: bool = True, 
                         move_to_duplicates: bool = False) -> None:
        """Remove duplicate images with memory optimization."""
        duplicate_groups = self.processor.find_duplicates_optimized(folder_path)
        
        if not duplicate_groups:
            print("No duplicates found!")
            return
        
        print(f"\nFound {len(duplicate_groups)} groups of duplicates:")
        
        # Create duplicates folder if needed
        duplicates_folder = None
        if move_to_duplicates and not dry_run:
            duplicates_folder = self.create_duplicates_folder(folder_path)
        
        total_files_to_process = 0
        total_space_saved = 0
        action_word = "MOVE" if move_to_duplicates else "DELETE"
        
        # Process groups one at a time to minimize memory usage
        for i, group in enumerate(duplicate_groups, 1):
            print(f"\nGroup {i} ({len(group)} duplicates):")
            
            # Select best image
            best_image = self.processor.select_best_image(group)
            
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
                                filename = os.path.basename(img['path'])
                                target_path = os.path.join(duplicates_folder, filename)
                                target_path = self.handle_duplicate_filename(target_path)
                                
                                shutil.move(img['path'], target_path)
                                print(f"    Moved: {filename} -> Duplicates/{os.path.basename(target_path)}")
                            else:
                                os.remove(img['path'])
                                print(f"    Deleted: {os.path.basename(img['path'])}")
                        except Exception as e:
                            action = "moving" if move_to_duplicates else "deleting"
                            print(f"    Error {action} {img['path']}: {e}")
            
            # Clear group from memory after processing
            group.clear()
        
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
    parser = argparse.ArgumentParser(description='Memory-optimized duplicate image remover')
    parser.add_argument('folder', help='Path to folder containing images')
    
    # Create mutually exclusive group for action options
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--execute', action='store_true', 
                             help='Actually delete duplicate files (default is dry-run)')
    action_group.add_argument('--move-duplicates', action='store_true',
                             help='Move duplicates to "Duplicates" folder instead of deleting them')
    
    parser.add_argument('--similarity', type=int, default=5, 
                       help='Similarity threshold (0-10, lower = more strict)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of images to process in each batch (default: 100)')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        return
    
    print("Memory-Optimized Image Duplicate Remover")
    print("=" * 40)
    
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
    
    print(f"Batch size: {args.batch_size} images per batch")
    print()
    
    # Create processor and remover instances
    processor = ImageProcessor(similarity_threshold=args.similarity, batch_size=args.batch_size)
    remover = DuplicateRemover(processor)
    
    # Process duplicates
    remover.remove_duplicates(args.folder, dry_run=dry_run, move_to_duplicates=move_to_duplicates)

if __name__ == "__main__":
    main()