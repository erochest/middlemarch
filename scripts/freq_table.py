#!/usr/bin/env python3


"""Generate frequency tables for all levels of chunking."""


import csv
import glob
import os

from sklearn.feature_extraction.text import CountVectorizer

import split_text


def read_corpus(dirname):
    """Read in a corpus and yield each document as a string."""
    for filename in glob.glob(os.path.join(dirname, '*.txt')):
        with open(filename) as fin:
            yield (filename, fin.read().replace('_', ' '))


def file_to_loc(filename):
    """Extracts the location from a filename."""
    return '.'.join(p.lstrip('0') for p in filename.split('.')[0].split('-')[1:])


def main():
    for dirname in split_text.CHUNKS:
        files = []
        content = []
        for filename, text in read_corpus(dirname):
            files.append(filename)
            content.append(text)

        counts = CountVectorizer()
        freqs = counts.fit_transform(content).toarray()

        output = dirname + '-freq.csv'
        print('{} => {}'.format(dirname, output))
        with open(output, 'w') as fout:
            writer = csv.writer(fout)
            headers = ['token'] + [file_to_loc(filename) for filename in files]
            writer.writerow(headers)
            writer.writerows(
                [name] + list(freqs[:, i])
                for i, name in enumerate(counts.get_feature_names())
                )


if __name__ == '__main__':
    main()
