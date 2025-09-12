import sys
import os
from pathlib import Path

# Add src to path to import our modules
sys.path.insert(0, os.path.dirname(__file__))

from svg_packager import parse_svg_meta

def run_final_test():
    print("--- Running Final Parser Test ---")
    output_dir = Path(__file__).resolve().parent.parent / 'output'
    svg_projects_dir = output_dir / 'svg_projects'

    if not svg_projects_dir.exists():
        print(f"Error: Directory not found: {svg_projects_dir}")
        return

    svg_files = list(svg_projects_dir.glob('*.svg'))
    print(f"Found {len(svg_files)} SVG files to process.")

    all_metadata = []
    for svg_file in svg_files:
        print(f"\n--- Processing: {svg_file.name} ---")
        try:
            svg_content = svg_file.read_text(encoding='utf-8')
            print(f"  - Read {len(svg_content)} bytes.")
            meta = parse_svg_meta(svg_content)
            if meta:
                print(f"  - SUCCESS: Parsed metadata. Title: {meta.get('title')}")
                all_metadata.append(meta)
            else:
                print(f"  - FAILED: No metadata found.")
        except Exception as e:
            print(f"  - ERROR: {e}")

    print(f"\n--- Test Complete: {len(all_metadata)} metadata objects found ---")

if __name__ == "__main__":
    run_final_test()
