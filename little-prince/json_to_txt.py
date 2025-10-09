#!/usr/bin/env python3
"""
Convert sentences from JSON to plain text format (one sentence per line).
"""

import json
from pathlib import Path


def main():
    # Setup paths
    script_dir = Path(__file__).parent
    json_path = script_dir / "sentences.json"
    txt_path = script_dir / "sentences.txt"
    
    print(f"Reading JSON file: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sentences = data['sentences']
    print(f"Found {len(sentences)} sentences")
    
    print(f"Writing text file: {txt_path}")
    with open(txt_path, 'w', encoding='utf-8') as f:
        # Write each sentence on its own line
        for item in sentences:
            f.write(item['text'] + '\n')
    
    print(f"Done! Created {txt_path}")


if __name__ == "__main__":
    main()

