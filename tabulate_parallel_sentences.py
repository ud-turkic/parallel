import re
import sys
import glob
import argparse
from collections import defaultdict
import os

def extract_sentences_from_conllu(filepath):
    """Extract sentence IDs, text and English translations from a CONLLU file."""
    sentences = {}
    current_id = None
    current_text = None
    current_en = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Extract sentence ID
            if line.startswith('# sent_id = '):
                current_id = line[len('# sent_id = '):]
                current_text = None
                current_en = None
            
            # Extract text
            elif line.startswith('# text = '):
                current_text = line[len('# text = '):]
            
            # Extract English translation
            elif line.startswith('# text[en] = '):
                current_en = line[len('# text[en] = '):]
            
            # End of sentence block, store the collected information
            elif not line or line.startswith('#') or line.startswith('1\t'):
                if current_id and current_text:
                    sentences[current_id] = {
                        'text': current_text,
                        'en': current_en
                    }
    
    return sentences

def sort_sentence_ids(ids):
    """Sort sentence IDs in the specified order: cairo, udtw23, then general numbers."""
    
    def sort_key(id_str):
        # Handle cairo IDs
        if id_str.startswith('cairo-'):
            num_part = id_str[len('cairo-'):]
            # Convert any decimal numbers properly
            try:
                if '.' in num_part:
                    main, sub = num_part.split('.')
                    return (0, int(main), int(sub))
                else:
                    return (0, int(num_part), 0)
            except ValueError:
                # If conversion fails, use string comparison but keep in cairo category
                return (0, 0, 0, num_part)  # Add extra tuple element for string comparisons
        
        # Handle udtw23 IDs
        elif id_str.startswith('udtw23-'):
            num_part = id_str[len('udtw23-'):]
            # Convert any decimal numbers properly
            try:
                if '.' in num_part:
                    main, sub = num_part.split('.')
                    return (1, int(main), int(sub))
                else:
                    return (1, int(num_part), 0)
            except ValueError:
                # If conversion fails, use string comparison but keep in udtw23 category
                return (1, 0, 0, num_part)  # Add extra tuple element for string comparisons
        
        # Handle general numeric IDs
        else:
            try:
                if '.' in id_str:
                    main, sub = id_str.split('.')
                    return (2, int(main), int(sub))
                else:
                    return (2, int(id_str), 0)
            except ValueError:
                # If conversion fails, use string comparison in the general category
                return (2, 0, 0, id_str)  # Add extra tuple element for string comparisons
    
    # Ensure all IDs are strings
    string_ids = [str(id_val) for id_val in ids]
    return sorted(string_ids, key=sort_key)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Tabulate parallel sentences from multiple CONLLU treebank files.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # File arguments
    parser.add_argument('-o', '--output', help='Output file path. If not specified, output is printed to stdout.')
    
    # Language inclusion flags with file paths
    lang_group = parser.add_argument_group('language options', 'Specify which languages to include (at least one required)')
    lang_group.add_argument('--turkish', metavar='FILE', help='Path to Turkish treebank file')
    lang_group.add_argument('--azerbaijani', metavar='FILE', help='Path to Azerbaijani treebank file')
    lang_group.add_argument('--kyrgyz', metavar='FILE', help='Path to Kyrgyz treebank file')
    lang_group.add_argument('--uzbek', metavar='FILE', help='Path to Uzbek treebank file')
    
    args = parser.parse_args()
    
    # Make sure at least one language file is provided
    if not (args.turkish or args.azerbaijani or args.kyrgyz or args.uzbek):
        parser.error("At least one language treebank file must be specified")
    
    # Identify language for each file based on arguments
    language_data = {}
    all_ids = set()
    
    # Process Turkish file
    if args.turkish:
        if not os.path.exists(args.turkish):
            print(f"Warning: Turkish file '{args.turkish}' not found.")
        else:
            print(f"Processing Turkish file: {args.turkish}")
            sentences = extract_sentences_from_conllu(args.turkish)
            language_data['Turkish'] = sentences
            all_ids.update(sentences.keys())
            print(f"  Found {len(sentences)} sentences")
    
    # Process Azerbaijani file
    if args.azerbaijani:
        if not os.path.exists(args.azerbaijani):
            print(f"Warning: Azerbaijani file '{args.azerbaijani}' not found.")
        else:
            print(f"Processing Azerbaijani file: {args.azerbaijani}")
            sentences = extract_sentences_from_conllu(args.azerbaijani)
            language_data['Azerbaijani'] = sentences
            all_ids.update(sentences.keys())
            print(f"  Found {len(sentences)} sentences")
    
    # Process Kyrgyz file
    if args.kyrgyz:
        if not os.path.exists(args.kyrgyz):
            print(f"Warning: Kyrgyz file '{args.kyrgyz}' not found.")
        else:
            print(f"Processing Kyrgyz file: {args.kyrgyz}")
            sentences = extract_sentences_from_conllu(args.kyrgyz)
            language_data['Kyrgyz'] = sentences
            all_ids.update(sentences.keys())
            print(f"  Found {len(sentences)} sentences")
    
    # Process Uzbek file
    if args.uzbek:
        if not os.path.exists(args.uzbek):
            print(f"Warning: Uzbek file '{args.uzbek}' not found.")
        else:
            print(f"Processing Uzbek file: {args.uzbek}")
            sentences = extract_sentences_from_conllu(args.uzbek)
            language_data['Uzbek'] = sentences
            all_ids.update(sentences.keys())
            print(f"  Found {len(sentences)} sentences")
    
    if not language_data:
        print("No valid treebank files found.")
        return
    
    # Check if we have the Turkish file for English translations
    if 'Turkish' not in language_data:
        print("Warning: No Turkish file found. English translations might be missing.")
    
    # Sort all the sentence IDs
    sorted_ids = sort_sentence_ids(all_ids)
    
    # Check for missing sentences in Turkish
    if 'Turkish' in language_data:
        turkish_ids = set(language_data['Turkish'].keys())
        missing_in_turkish = all_ids - turkish_ids
        if missing_in_turkish:
            print("\nWarning: The following sentences are missing in the Turkish treebank:")
            for missing_id in sorted(missing_in_turkish):
                print(f"  {missing_id}")
    
    # Fixed column order: ID, English, Azerbaijani, Kyrgyz, Turkish, Uzbek
    columns = ['Sentence ID', 'English']
    
    if 'Azerbaijani' in language_data:
        columns.append('Azerbaijani')
    
    if 'Kyrgyz' in language_data:
        columns.append('Kyrgyz')
    
    if 'Turkish' in language_data:
        columns.append('Turkish')
    
    if 'Uzbek' in language_data:
        columns.append('Uzbek')
    
    # Prepare output lines
    output_lines = []
    header = "| " + " | ".join(columns) + " |"
    output_lines.append(header)
    
    # Create the separator line
    separator = "|" + "|".join(["------------"] * len(columns)) + "|"
    output_lines.append(separator)
    
    # Table rows
    for sent_id in sorted_ids:
        # Get English translation from Turkish file if available
        en_text = ""
        if 'Turkish' in language_data and sent_id in language_data['Turkish']:
            en_text = language_data['Turkish'][sent_id].get('en', "")
        
        # Start with ID and English translation
        row_data = [sent_id, en_text]
        
        # Add texts in the specified order
        if 'Azerbaijani' in language_data:
            azerbaijani_text = language_data['Azerbaijani'].get(sent_id, {}).get('text', "")
            row_data.append(azerbaijani_text)
        
        if 'Kyrgyz' in language_data:
            kyrgyz_text = language_data['Kyrgyz'].get(sent_id, {}).get('text', "")
            row_data.append(kyrgyz_text)
        
        if 'Turkish' in language_data:
            turkish_text = language_data['Turkish'].get(sent_id, {}).get('text', "")
            row_data.append(turkish_text)
        
        if 'Uzbek' in language_data:
            uzbek_text = language_data['Uzbek'].get(sent_id, {}).get('text', "")
            row_data.append(uzbek_text)
        
        # Add row
        row = "| " + " | ".join(row_data) + " |"
        output_lines.append(row)
    
    # Write to file or print to stdout
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('# Tabulated Parallel Sentences\n\n')
            for line in output_lines:
                f.write(line + '\n')
        print(f"\nMarkdown table written to {args.output}")
    else:
        print("\nGenerating markdown table...\n")
        for line in output_lines:
            print(line)
        print("\nMarkdown table generated successfully.")

if __name__ == "__main__":
    main()