#!/usr/bin/env python3


from collections import namedtuple
from itertools import groupby
import os


TEXT = 'pg145.txt'
FULL = 'full'
BOOKS = 'books'
CHAPTERS = 'chapters'
PARAS = 'paragraphs'


Location = namedtuple('Location', ('book', 'chapter', 'para'))


def format_loc(loc):
    return '.'.join(str(part) for part in loc if part is not None)


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
    lines = read_book(TEXT)
    located = list(locate_lines(lines))

    for dirname in (FULL, BOOKS, CHAPTERS, PARAS):
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    write_full(located, FULL)

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
