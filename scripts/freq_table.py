#!/usr/bin/env python3


"""Generate frequency tables for all levels of chunking."""


import csv
import os

from sklearn.feature_extraction.text import CountVectorizer

from split_text import CHUNKS, file_to_loc, corpus_files_contents


def main():
    for dirname in CHUNKS:
        files, content = corpus_files_contents(dirname)

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
