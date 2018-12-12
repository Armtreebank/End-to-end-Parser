import os
import sys
import io
import random

import fire
from sklearn.externals import joblib

from COMBO import src
from COMBO.src.utils import ConllLoader, ConllSaver
from Tokenizer.tokenizer import Tokenizer


class TextToConll(object):
    @staticmethod
    def parse(input_text):
        tokenized_text = Tokenizer(input_text).segmentation().tokenization().output()
        res = ''
        for sentence in tokenized_text:
            res += '# {}\n'.format(sentence['segment'])
            for item in sentence['tokens']:
                res += "{}\t{}	_	_	_	_	_	_	_	_\n".format(item[0], item[1])
            res += '\n'
        return res

    def parse_file(self, input_file_path, output_file_path):
        with io.open(input_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        res = self.parse(text)
        with io.open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(res)


class Predictor(object):
    def __init__(self, model=None, model_path=None, input_converter=None, loader=None, saver=None):
        sys.modules['src'] = src
        self.model = model or joblib.load(model_path)
        self.input_converter = input_converter or TextToConll()
        self.loader = loader or ConllLoader()
        self.saver = saver or ConllSaver()

    def predict(self, input_file_path, output_file_path):
        conllu_format_file_path = input_file_path + '.conllu'
        self.input_converter.parse_file(input_file_path=input_file_path, output_file_path=conllu_format_file_path)
        test_data = self.loader.load(conllu_format_file_path)
        os.remove(conllu_format_file_path)

        predictions = self.model.predict(test_data)
        self.saver.save(output_file_path, predictions)

    def predict_raw(self, input_text):
        filename = 'tmp_' + str(random.randint(0, 10000000000))
        input_file = filename + '.in'
        output_file = filename + '.out'
        with io.open(input_file, 'w', encoding='utf-8') as f:
            f.write(input_text)

        self.predict(input_file, output_file)
        with io.open(output_file, 'r', encoding='utf-8') as f:
            raw_result = f.read()

        os.remove(input_file)
        os.remove(output_file)

        '''
        {
            'words': [
                {'text': 'This', 'tag': 'VERB'},
                {'text': 'is', 'tag': 'NOUN'},
                {'text': 'CSS', 'tag': 'PROPN'},
                {'text': 'sentence', 'tag': 'CCONJ'}],
            'arcs': [
                {'start': 0, 'end': 1, 'label': 'nsubj', 'dir': 'left'},
                {'start': 2, 'end': 3, 'label': 'det', 'dir': 'left'},
                {'start': 1, 'end': 3, 'label': 'attr', 'dir': 'right'}]
        };
        '''
        start = 0
        res = {'words': [], 'arcs': []}
        for line in raw_result.split('\n'):
            if line.startswith('#'):
                start = len(res['words'])
                continue
            parts = line.split('\t')
            if len(parts) == 0 or len(parts) == 1:
                continue

            res['words'].append({'text': parts[1], 'tag': parts[3]})

            start_i = int(parts[0])
            end_i = int(parts[6])
            if end_i == 0:
                continue

            [small, big] = sorted((start_i, end_i))
            res['arcs'].append({'start': start + small - 1,
                                'end': start + big - 1,
                                'label': parts[7],
                                'dir': 'right' if small == start_i else 'left'})
        return res


def main(model_path, input_path=None, input_text=None, output_path=None):
    model = Predictor(model_path=model_path)

    if input_path and output_path:
        model.predict(input_file_path=input_path, output_file_path=output_path)
    elif input_text:
        res = model.predict_raw(input_text=input_text)
        print(res)
    else:
        raise ValueError('You need to specify either input_path/output_path or input_text')


if __name__ == '__main__':
    fire.Fire(main)
