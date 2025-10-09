#!/usr/bin/env python3
"""
Extract sentences from The Little Prince epub file.
Uses nltk for sentence segmentation and saves to JSON.
"""

import json
import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import nltk
from pathlib import Path

def extract_text_from_epub(epub_path):
    """Extract text content from epub file in reading order, preserving paragraphs."""
    book = epub.read_epub(epub_path)
    paragraphs = []
    
    # Use the spine to get items in reading order
    spine_items = []
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if item:
            spine_items.append(item)
    
    print(f"Found {len(spine_items)} items in reading order (spine)")
    
    for i, item in enumerate(spine_items):
        # Parse HTML content
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        
        # Extract text, removing script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract paragraphs separately to preserve structure
        # Look for common block-level elements
        for element in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = element.get_text().strip()
            if text:
                paragraphs.append(text)
        
        # Show first item for debugging
        if i < 3 and paragraphs:
            preview = paragraphs[-1][:100] if paragraphs else ""
            print(f"  Item {i}: {preview}...")
    
    print(f"Extracted {len(paragraphs)} paragraphs total")
    return paragraphs

def split_into_sentences(paragraphs):
    """Split paragraphs into sentences using nltk, respecting paragraph boundaries."""
    all_sentences = []
    chapter_pattern = re.compile(r'^Chapter [IVXLCDM]+\s+')
    
    for para in paragraphs:
        # Tokenize each paragraph separately
        sentences = nltk.sent_tokenize(para)
        for sent in sentences:
            sentence_text = sent.strip()
            if sentence_text:
                # Remove "Chapter X" prefix if present
                sentence_text = chapter_pattern.sub('', sentence_text)
                if sentence_text:  # Only add if there's text remaining after removal
                    all_sentences.append(sentence_text)
    
    return all_sentences

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    epub_path = script_dir / "The Little Prince, Katherine Woods.epub"
    output_path = script_dir / "sentences.json"
    
    # Download nltk data if needed
    print("Setting up nltk...")
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        print("Downloading nltk punkt_tab tokenizer...")
        nltk.download('punkt_tab')
    
    print(f"Reading epub file: {epub_path}")
    paragraphs = extract_text_from_epub(epub_path)
    
    print("Splitting paragraphs into sentences...")
    sentences = split_into_sentences(paragraphs)
    print(f"Total sentences extracted: {len(sentences)}")
    
    # Find the first sentence that starts with "Once when I was" (beginning of Chapter I)
    start_idx = 0
    for i, sent in enumerate(sentences):
        if "Once when I was six years old" in sent:
            start_idx = i
            print(f"Starting from sentence {i + 1} (Chapter I)")
            break
    
    # Keep only sentences from Chapter I onwards
    sentences = sentences[start_idx:]
    print(f"Sentences after removing front matter: {len(sentences)}")
    
    # Create output data structure
    output_data = {
        "book": "The Little Prince",
        "translator": "Katherine Woods",
        "total_sentences": len(sentences),
        "sentences": [
            {
                "id": i + 1,
                "text": sentence
            }
            for i, sentence in enumerate(sentences)
        ]
    }
    
    # Save to JSON
    print(f"Saving to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("Done!")
    print(f"\nFirst 5 sentences:")
    for i, sent in enumerate(sentences[:5], 1):
        print(f"{i}. {sent}")

if __name__ == "__main__":
    main()

