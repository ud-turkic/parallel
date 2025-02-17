import argparse, nltk
from pathlib import Path

def get_conllu(file_path, lang, sent_type):
    with file_path.open() as f:
        sentences = f.read().splitlines()
    conllu_str = ''
    for i, sentence in enumerate(sentences):
        sent_id = f'{sent_type}-{lang}-{i+1}' if sent_type else f'{lang}-{i+1}'
        conllu_str += f'# sent_id = {sent_id}\n'
        conllu_str += f'# text = {sentence}\n'
        tokens = nltk.word_tokenize(sentence)
        for j, token in enumerate(tokens):
            conllu_str += f'{j+1}\t{token}\t_\t_\t_\t_\t_\t_\t_\t_\n'
        conllu_str += '\n'
    return conllu_str

def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse text files of sentences')
    parser.add_argument('-i1', '--input1', type=Path, required=True, help='Path to the first text file of 20 Cairo sentences')
    parser.add_argument('-i2', '--input2', type=Path, required=True, help='Path to the second text file with 20 UDTW23 sentences')
    parser.add_argument('-i3', '--input3', type=Path, required=True, help='Path to the third text file with 88 sentences')
    return parser.parse_args()

def main():
    nltk.download('punkt_tab')

    args = parse_arguments()
    file1_path, file2_path, file3_path = args.input1, args.input2, args.input3
    conllu_str = get_conllu(file1_path, 'tr', 'cairo')
    conllu_str += get_conllu(file2_path, 'tr', 'udtw23')
    conllu_str += get_conllu(file3_path, 'tr', '')

    with open('tr_tuecl-ud-test.conllu', 'w', encoding='utf-8') as f:
        f.write(conllu_str)

if __name__ == '__main__':
    main()