from conllu.conllu import Treebank
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='List sentences in a CoNLL-U file.')
    parser.add_argument('conllu_file', type=str, help='Path to the CoNLL-U file')
    parser.add_argument('--output', type=str, default=None, help='Path to the output file')
    return parser.parse_args()

def main():
    args = get_args()
    conllu_file = args.conllu_file
    output_file = args.output

    treebank = Treebank(name='parallel')
    treebank.load_conllu(conllu_file, data_type='file')
    sentences = treebank.sentences

    if output_file:
        with open(output_file, 'w') as f:
            f.write('# Sentence list\n\n')
            for sentence_id, sentence in sentences.items():
                f.write(f'- `{sentence_id}`: {sentence.text}\n')
        print(f'Sentences saved to {output_file}')

if __name__ == '__main__':
    main()