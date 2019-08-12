import argparse
import ast
import os
import collections
import subprocess
import json
import csv
import nltk
from nltk import pos_tag

nltk.download('averaged_perceptron_tagger')


class StaticAnalyzer:
    """ class for static code analyze """

    VERB_TYPE = 'VB'
    NOUN_TYPE = 'NN'

    JSON = 'json'
    CSV = 'csv'

    TOP_SIZE = 10

    def __init__(self, path):
        self.path = path

    @staticmethod
    def clone_github_repo_to_path(self, url):
        """ clone git url to path with subprocess """
        status_code = subprocess.call(['git', 'clone', url])
        return status_code

    def get_ext_filenames(self, ext='py'):
        """ return filenames endswith .py """
        filenames = []
        for dirname, dirs, files in os.walk(self.path, topdown=True):
            files = [file for file in files if file.endswith(f'.{ext}')]
            for file in files:
                filenames.append(os.path.join(dirname, file))
            if len(filenames) == 100:
                break
        return filenames

    def get_function_names(self):
        """ return define functions """
        trees = self.get_trees()
        all_func_names = flat(
            [[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]
        )
        return exclude_magic_function_names(all_func_names)

    def get_top_words_in_path(self, word_type, top_size=10):
        """ return top of all verbs in path, top 10 by default """
        all_words = self.get_all_words_in_path()
        verbs = flat([get_words_from_name(word, word_type) for word in all_words])
        return collections.Counter(verbs).most_common(top_size)

    def get_top_function_words_in_path(self, word_type, top_size=TOP_SIZE):
        """ return most common words, top 10 by default """
        functions = self.get_function_names()
        verbs = flat([get_words_from_name(function_name, word_type) for function_name in functions])
        return collections.Counter(verbs).most_common(top_size)

    def get_top_functions_names_in_path(self, top_size=TOP_SIZE):
        """ return most common names of functions, top 10 by default """
        functions = self.get_function_names()
        return collections.Counter(functions).most_common(top_size)

    def get_trees(self, with_filenames=False, with_file_content=False):
        """ return list of trees from path """
        trees = []
        filenames = self.get_ext_filenames()
        for filename in filenames:
            main_file_content = get_content_from_file(filename)
            try:
                tree = ast.parse(main_file_content)
            except SyntaxError:
                tree = None
            if with_filenames:
                if with_file_content:
                    trees.append((filename, main_file_content, tree))
                else:
                    trees.append((filename, tree))
            else:
                trees.append(tree)
        return trees

    def get_all_words_in_path(self):
        """ return list of split verbs from path """
        trees = self.get_trees()
        all_words = [f for f in flat([get_all_names(t) for t in trees])]
        words = exclude_magic_function_names(all_words)
        return flat([split_snake_case_name_to_words(word) for word in words])

    @staticmethod
    def save_report_to_file(data, name, ext):
        """ save report to file """
        if ext.lower() == JSON:
            save_to_json(dict(data), name)
        elif ext.lower() == CSV:
            save_to_csv(dict(data), name)


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def get_word_type(word):
    """ return True if word is verbose"""
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1]


def get_content_from_file(filename):
    """ read file and return content """
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        main_file_content = attempt_handler.read()
    return main_file_content


def get_all_names(tree):
    """ return names """
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_words_from_name(name, word_type):
    """ return current type words from name """
    return [word for word in split_snake_case_name_to_words(name) if get_word_type(word) == word_type]


def split_snake_case_name_to_words(name):
    """ return list of verbs from snake case name """
    return name.split('_')


def exclude_magic_function_names(func_names_list):
    """ return func names without __name__ """
    return [f for f in func_names_list if not (f.startswith('__') and f.endswith('__'))]


def save_to_json(data, file_name):
    """ save data to json file """
    with open(f'{file_name}.json', 'w') as fp:
        json.dump(data, fp)


def save_to_csv(data, file_name):
    """ save data to csv file """
    with open(f'{file_name}.csv', 'w') as f:
        w = csv.DictWriter(f, data.keys())
        w.writeheader()
        w.writerow(data)


def get_parsed_arguments():
    """ get and parse parameters from CLI """
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='path to analyzing repo')
    parser.add_argument('--remote', type=str, help='path to remote url')
    parser.add_argument('--json', type=bool, help='import report to json file')
    parser.add_argument('--csv', type=bool, help='import report to csv file')
    parser.add_argument('--console', type=bool, help='print report in console')
    parser.add_argument('--size', type=int, help='count of top words')
    parser.add_argument('--type', type=str, help='words type for search')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_parsed_arguments()
    path = args.path if args.path else os.path.curdir
    analyzer = StaticAnalyzer(path)
    top_size = analyzer.TOP_SIZE
    if args.remote:
        analyzer.clone_github_repo_to_path(args.remote)
    if args.size:
        top_size = args.size
    if args.type == 'N':
        top_func_words = analyzer.get_top_function_words_in_path(analyzer.NOUN_TYPE, top_size=top_size)
        top_words = analyzer.get_top_words_in_path(analyzer.NOUN_TYPE, top_size=top_size)
    elif args.type == 'V':
        top_func_words = analyzer.get_top_function_words_in_path(analyzer.VERB_TYPE, top_size=top_size)
        top_words = analyzer.get_top_words_in_path(analyzer.VERB_TYPE, top_size=top_size)
    else:
        exit('need a type of words in search')

    top_func_names = analyzer.get_top_functions_names_in_path(top_size=top_size)
    
    if args.json:
        analyzer.save_report_to_file(top_func_words, 'top_func_words', analyzer.JSON)
        analyzer.save_report_to_file(top_words, 'top_words', analyzer.JSON)
        analyzer.save_report_to_file(top_func_names, 'top_func_names', analyzer.JSON)
    if args.csv:
        analyzer.save_report_to_file(top_func_words, 'top_func_words', analyzer.CSV)
        analyzer.save_report_to_file(top_words, 'top_words', analyzer.CSV)
        analyzer.save_report_to_file(top_func_names, 'top_func_names', analyzer.CSV)
    if args.console:
        print('\n***** TOP FUNCTIONS WORDS *****')
        for (word, count) in top_func_words:
            print(f'{word}: {count}')
        print('\n***** TOP FUNCTIONS NAMES *****')
        for (word, count) in top_func_names:
            print(f'{word}: {count}')
        print('\n***** TOP WORDS *****')
        for (word, count) in top_words:
            print(f'{word}: {count}')
