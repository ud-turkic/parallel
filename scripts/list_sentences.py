from udsearch import load_local_file
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="List sentences in a CoNLL-U file.")
    parser.add_argument("conllu_file", type=str, help="Path to the CoNLL-U file")
    parser.add_argument(
        "--output", type=str, default=None, help="Path to the output file"
    )
    return parser.parse_args()


def main():
    args = get_args()
    sentences = load_local_file(args.conllu_file)

    if args.output:
        with open(args.output, "w") as f:
            f.write("# Sentence list\n\n")
            for sentence in sentences:
                f.write(f"- `{sentence.sent_id}`: {sentence.text}\n")
        print(f"Sentences saved to {args.output}")


if __name__ == "__main__":
    main()
