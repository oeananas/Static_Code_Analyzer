# Project Name

Static code analyzer

## Installation

```bash
pip3 install -r requirements.txt
```
## Examples

```bash
python static_analyze_v2.py --remote=https://github.com/oeananas/Invaders.git --console=True --size=20 --type=V

[nltk_data] Downloading package averaged_perceptron_tagger to
[nltk_data]     /home/stanislav/nltk_data...
[nltk_data]   Package averaged_perceptron_tagger is already up-to-
[nltk_data]       date!
Клонирование в «Invaders»…
remote: Enumerating objects: 83, done.
remote: Total 83 (delta 0), reused 0 (delta 0), pack-reused 83
Распаковка объектов: 100% (83/83), готово.

***** TOP FUNCTIONS WORDS *****
get: 25
save: 6
run: 1
initialize: 1

***** TOP FUNCTIONS NAMES *****
update: 3
flat: 2
get_word_type: 2
get_content_from_file: 2
get_all_names: 2
get_words_from_name: 2
split_snake_case_name_to_words: 2
exclude_magic_function_names: 2
save_to_json: 2
save_to_csv: 2
clone_github_repo_to_path: 2
get_ext_filenames: 2
get_function_names: 2
get_top_words_in_path: 2
get_top_function_words_in_path: 2
get_top_functions_names_in_path: 2
get_trees: 2
get_all_words_in_path: 2
save_report_to_file: 2
blitme: 2

***** TOP WORDS *****
get: 13
save: 4
run: 1

```


