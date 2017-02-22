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


class KWIC(namedtuple('KWIC', ('loc', 'prefix', 'token', 'suffix'))):
    """One keyword in context."""
    __slots__ = ()

    def __str__(self):
        return '[{!s:>9}] {:>30} {} {:<30}'.format(
            self.loc, self.prefix, self.token, self.suffix,
            )


def read_token_set(filename):
    """This reads the tokens from filename and returns them as a set."""
    with open(filename) as fin:
        return set(token for _, token in tokenize(fin.read()))


def get_prefix(i, tokens, para, context):
    """Return the leading context from tokens[i]."""
    start = tokens[i][0][0]
    j = i - 1
    prefix = ''

    while j >= 0 and len(prefix) < context:
        (pre_start, _), _ = tokens[j]
        if start - pre_start > context:
            break
        prefix = para[pre_start:start].strip()
        j -= 1

    return prefix


def get_suffix(i, tokens, para, context):
    """Return the trailing context from tokens[i]."""
    end = tokens[i][0][1]
    j = i + 1
    suffix = ''

    while j < len(tokens) and len(suffix) < context:
        (_, post_end), _ = tokens[j]
        if post_end - end > context:
            break
        suffix = para[end:post_end].strip()
        j += 1

    return suffix


def write_kwics(output_dir, index):
    """Write an index of KWICs to the output directory."""
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    for word, kwics in index.items():
        with open(os.path.join(output_dir, word + '.txt'), 'w') as fout:
            fout.write(word + '\n' + ('=' * len(word)) + '\n\n')
            # kwics.sort(key=operator.attrgetter('loc'))
            for kwic in kwics:
                fout.write(str(kwic) + '\n')
            fout.write('\n')


def main():
    """Generate all the KWICs. Quickly."""
    lines = read_book(os.path.join(FULL, TEXT))
    located = locate_lines(lines)
    stopwords = read_token_set(STOP_FILE)

    index = defaultdict(list)

    for loc, para_pairs in groupby(located, operator.itemgetter(0)):
        para = normalize(' '.join(line for _, line in para_pairs))
        tokens = tokenize(para)

        for (i, (_, token)) in enumerate(tokens):
            if token in stopwords:
                continue

            prefix = get_prefix(i, tokens, para, CONTEXT)
            suffix = get_suffix(i, tokens, para, CONTEXT)

            index[token].append(KWIC(loc, prefix, token, suffix))

    write_kwics(OUTPUT_DIR, index)


if __name__ == '__main__':
    main()
