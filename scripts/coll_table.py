#!/usr/bin/env python3


"""Generate frequency tables of collocate."""


from collections import defaultdict
import csv

from sklearn.feature_extraction.text import CountVectorizer

from split_text import CHUNKS, corpus_files_contents, file_to_loc


def collocates(items, spread=3, bidir=True):
    """Takes a list of items and yields pairs of items that are spread apart.

    >>> list(collocates(range(10), 3, False))
    [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (3, 6), (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (5, 8), (6, 7), (6, 8), (6, 9), (7, 8), (7, 9), (8, 9)]
    """
    maximum = len(items)
    deltas = range(1, spread + 1)

    for i, x in enumerate(items):
        for d in deltas:
            j = i + d

            if j >= maximum:
                break

            y = items[j]
            yield (x, y)
            if bidir:
                yield (y, x)


def main():
    for dirname in CHUNKS:
        files, content = corpus_files_contents(dirname)
        headers = ['token'] + [file_to_loc(filename) for filename in files]

        counts = CountVectorizer()
        tokenizer = counts.build_analyzer()

        paired = []
        for text in content:
            tokens = tokenizer(text)
            cols = ' '.join('_'.join(pair) for pair in collocates(tokens))
            paired.append(cols)

        freqs = counts.fit_transform(paired).toarray()

        index = defaultdict(list)
        for i, word in enumerate(counts.get_feature_names()):
            index[word[0]].append((i, word))

        for letter, indexes in index.items():
            output = '{}-{}-colls.csv'.format(dirname, letter)
            print('{} => {}'.format(dirname, output))
            with open(output, 'w') as fout:
                writer = csv.writer(fout)
                writer.writerow(headers)
                writer.writerows(
                    [word] + list(freqs[:, i])
                    for i, word in indexes
                    )


if __name__ == '__main__':
    main()
