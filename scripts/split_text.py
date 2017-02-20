#!/usr/bin/env python3


from collections import namedtuple
import glob
from itertools import groupby
import os


TEXT = 'pg145.txt'
FULL = 'full'
BOOKS = 'books'
CHAPTERS = 'chapters'
PARAS = 'paragraphs'
CHUNKS = (FULL, BOOKS, CHAPTERS, PARAS)


Location = namedtuple('Location', ('book', 'chapter', 'para'))


def read_corpus(dirname):
    """Read in a corpus and yield each document as a string."""
    for filename in glob.glob(os.path.join(dirname, '*.txt')):
        with open(filename) as fin:
            yield (filename, fin.read().replace('_', ' '))


def file_to_loc(filename):
    """Extracts the location from a filename.

    >>> file_to_loc('full/pg145.txt')
    Location(book=None, chapter=None, para=None)
    >>> file_to_loc('books/book-03.txt')
    Location(book=3, chapter=None, para=None)
    >>> file_to_loc('chapters/chapter-07-02.txt')
    Location(book=7, chapter=2, para=None)
    >>> file_to_loc('paragraphs/paragraph-04-05-0029.txt')
    Location(book=4, chapter=5, para=29)
    """
    parts = filename.split('.')[0].split('-')[1:]
    return read_loc('.'.join(parts)) if parts else Location(None, None, None)


def file_to_loc_str(filename):
    """Extracts the location from a filename as a string."""
    return format_loc(file_to_loc(filename))


def corpus_files_contents(dirname):
    """Return a tuple listing the files in the corpus in the first element and
    the contents of the corpus in the second."""
    return unzip(read_corpus(dirname))


def unzip(pairs):
    """Take an iterator of pairs and returns a pair of lists."""
    firsts = []
    seconds = []
    for a, b in iter(pairs):
        firsts.append(a)
        seconds.append(b)
    return (firsts, seconds)


def format_loc(loc):
    return '.'.join(str(part) for part in loc if part is not None)


def read_loc(loc_str):
    args = ([int(part) for part in loc_str.split('.')] + ([None] * 3))[:3]
    return Location._make(args)


def loc_resolution(loc):
    """Return the number of levels that this Location represents."""
    if loc.chapter is None:
        return 1
    elif loc.para is None:
        return 2
    else:
        return 3


def focus_fn(resolution):
    """Return a function that slices a Location to the given resolution."""
    focus = resolution - 1
    return lambda loc: loc[:focus]


def book_start(line):
    """Does this line start a book?"""
    return (line.startswith('PRELUDE') or
            line.startswith('FINALE') or
            line.startswith('BOOK '))


def chapter_start(line):
    """Does this line start a chapter?"""
    return line.startswith('CHAPTER ')


def paragraph_start(line):
    """Does this line start a paragraph?"""
    return not line.strip()


def write_full(lines, full_dir):
    """Write the lines to a file with their locations."""
    with open(os.path.join(full_dir, 'full.txt'), 'w') as fout:
        current = None
        for loc, line in lines:
            if loc != current:
                current = loc
                fout.write('[{}] '.format(format_loc(loc)))
            fout.write(line)


def write_book(lines, book_dir):
    """Write the lines of a book to a file. """
    if lines:
        book = lines[0][0].book
        filename = os.path.join(book_dir, 'book-%02d.txt' % (book,))
        with open(filename, 'w') as fout:
            fout.writelines(line for _, line in lines)


def write_chapter(lines, chapter_dir):
    """Write the lines of a chapter to a file. """
    if lines:
        first = lines[0][0]
        book = first.book
        chapter = first.chapter
        filename = os.path.join(chapter_dir,
                                'chapter-%02d-%02d.txt' % (book, chapter))
        with open(filename, 'w') as fout:
            fout.writelines(line for _, line in lines)


def write_paragraph(lines, paragraph_dir):
    """Write the lines of a paragraph to a file. """
    if lines:
        first = lines[0][0]
        book = first.book
        chapter = first.chapter
        para = first.para
        filename = os.path.join(
            paragraph_dir,
            'paragraph-%02d-%02d-%04d.txt' % (book, chapter, para),
            )
        with open(filename, 'w') as fout:
            fout.writelines(line for _, line in lines)


def read_book(filename):
    """Read the file and return the lines. """
    with open(filename) as fin:
        return list(fin)


def locate_lines(lines):
    """Iterate over the lines and return location, line pairs. """
    book = 1
    chapter = para = None
    loc = None
    blank_line = False

    for line in lines:
        if book_start(line):
            book += 1
            chapter = para = None
            blank_line = True
            loc = Location(book, chapter, para)
        elif chapter_start(line):
            chapter = 1 if chapter is None else chapter + 1
            para = None
            blank_line = True
            loc = Location(book, chapter, para)
        elif paragraph_start(line):
            blank_line = True
        elif blank_line and line.strip():
            para = 1 if para is None else para + 1
            loc = Location(book, chapter, para)
            blank_line = False
        elif line.strip():
            blank_line = False

        if loc is not None:
            yield (loc, line)


def main():
    lines = read_book(os.path.join(FULL, TEXT))
    located = list(locate_lines(lines))

    for dirname in (FULL, BOOKS, CHAPTERS, PARAS):
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    write_full(located, '.')

    for bn, book_lines in groupby(located, key=lambda p: p[0].book):
        if bn is None:
            continue
        book_lines = list(book_lines)
        write_book(book_lines, BOOKS)

        for cn, chapter_lines in groupby(book_lines, key=lambda p: p[0].chapter):
            if cn is None:
                continue
            chapter_lines = list(chapter_lines)
            write_chapter(chapter_lines, CHAPTERS)

            for pn, para_lines in groupby(chapter_lines, key=lambda p: p[0].para):
                if pn is None:
                    continue
                para_lines = list(para_lines)
                write_paragraph(para_lines, PARAS)


if __name__ == '__main__':
    main()
