from pathlib import Path
import os, re

def main():
    script_dir = Path(__file__).parent
    conllu_files = list(script_dir.glob('*.conllu'))
    language_pattern = re.compile(r'(\w+)_.+\.conllu')
    languages = set()
    for file in conllu_files:
        language = language_pattern.match(file.name).group(1)
        languages.add(language)
    if len(languages) > 1:
        print('Multiple languages detected in the directory.')
        return

    tools_dir = script_dir / 'tools'
    validation_script_path = tools_dir / 'validate.py'
    data_dir = tools_dir / 'data'
    if not tools_dir.exists() or not validation_script_path.exists() or not data_dir.exists():
        os.system(f'git clone https://github.com/UniversalDependencies/tools.git')
    else:
        os.system(f'cd {tools_dir} && git pull')
    os.chdir(script_dir)
    
    validation_command = f'python {validation_script_path} --lang {language} --max-err 0 {' '.join([str(file) for file in conllu_files])} &> validation.log'
    os.system(validation_command)

if __name__ == '__main__':
    main()