#!/usr/bin/env python3


"""Generate frequency tables of collocate."""


from collections import defaultdict
import csv
import itertools
import operator

from sklearn.feature_extraction.text import CountVectorizer

from split_text import (
        CHUNKS, corpus_files_contents, file_to_loc, file_to_loc_str,
        loc_resolution, focus_fn, format_loc, unzip
        )


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


def simple_output(dirname, files, index, freqs):
    """Output."""
    headers = ['token'] + [file_to_loc_str(filename) for filename in files]

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


def break_output(dirname, files, index, freqs):
    """Subdivide the output by the next to last item."""
    locs = [(i, file_to_loc(filename)) for (i, filename) in enumerate(files)]
    loc_level = max(loc_resolution(loc) for _, loc in locs)
    locs.sort(key=operator.itemgetter(1))

    focus = focus_fn(loc_level)
    group_key = lambda pair: focus(pair[1])
    for place, focused_pairs in itertools.groupby(locs, group_key):
        focused_i, focused_locs = unzip(focused_pairs)
        focused = freqs[focused_i,]

        headers = ['token'] + [format_loc(loc) for loc in focused_locs]
        for letter, indexes in index.items():
            output = '{}-{}-{}-colls.csv'.format(
                dirname,
                '.'.join(str(n) for n in place),
                letter,
                )

            print('{} ({}) => {}'.format(dirname, place, output))
            with open(output, 'w') as fout:
                writer = csv.writer(fout)
                writer.writerow(headers)
                writer.writerows(
                    [word] + list(focused[:, i])
                    for i, word in indexes
                    )


def main():
    for dirname in CHUNKS:
        files, content = corpus_files_contents(dirname)

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

        if len(files) >= 50:
            break_output(dirname, files, index, freqs)
        else:
            simple_output(dirname, files, index, freqs)


if __name__ == '__main__':
    main()
