#!/usr/bin/env python3


"""Dump out all the KWICS for, like, everything. """


from collections import defaultdict, namedtuple
from itertools import groupby
import operator
import os
import re

from split_text import FULL, TEXT, read_book, locate_lines
# , file_to_loc, file_to_loc_str, loc_resolution, focus_fn, format_loc, unzip


CONTEXT = 30
OUTPUT_DIR = 'kwics'
STOP_FILE = 'english.stopwords'


def normalize(text):
    """Normalize whitespace."""
    return ' '.join(text.split())


def tokenize(text):
    """Tokenizes the text and iterate over the tokens and spans."""
    return [((m.start(0), m.end(0)), m.group(0).lower())
            for m in re.finditer(r'\w+', text.replace('_', ' '))]


class KWIC(namedtuple('KWIC', ('loc', 'prefix', 'token', 'postfix'))):
    """One keyword in context."""
    __slots__ = ()

    def __str__(self):
        return '[{!s:>9}] {:>30} {} {:<30}'.format(
            self.loc, self.prefix, self.token, self.postfix,
            )


def main():
    """Generate all the KWICs. Quickly."""
    lines = read_book(os.path.join(FULL, TEXT))
    located = locate_lines(lines)

    index = defaultdict(list)

    with open(STOP_FILE) as fin:
        stopwords = set(token for _, token in tokenize(fin.read()))

    for loc, para_pairs in groupby(located, operator.itemgetter(0)):
        para = normalize(' '.join(line for _, line in para_pairs))
        tokens = tokenize(para)

        for (i, ((start, end), token)) in enumerate(tokens):
            if token in stopwords:
                continue

            h = i - 1
            prefix = ''
            while h >= 0 and len(prefix) < CONTEXT:
                (pre_start, _), _ = tokens[h]
                if start - pre_start > CONTEXT:
                    break
                prefix = para[pre_start:start].strip()
                h -= 1

            j = i + 1
            suffix = ''
            while j < len(tokens) and len(suffix) < CONTEXT:
                (_, post_end), _ = tokens[j]
                if post_end - end > CONTEXT:
                    break
                suffix = para[end:post_end].strip()
                j += 1

            index[token].append(KWIC(loc, prefix, token, suffix))

    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for word, kwics in index.items():
        with open(os.path.join(OUTPUT_DIR, word + '.txt'), 'w') as fout:
            fout.write(word + '\n' + ('=' * len(word)) + '\n\n')
            # kwics.sort(key=operator.attrgetter('loc'))
            for kwic in kwics:
                fout.write(str(kwic) + '\n')
            fout.write('\n')


if __name__ == '__main__':
    main()
