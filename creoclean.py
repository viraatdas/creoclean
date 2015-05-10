#!/usr/bin/env python3
# file: creoclean.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-05-07 18:29:17 +0200
# Last modified: 2015-05-10 13:06:53 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to creoclean.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Cleans up Creo versioned files in the named diratories or in the current
working directory.  Removes all versions except the last one, and renames that
to version 1."""

import argparse
import logging
import os
import re
import sys

__version__ = '0.3.0'


def main(argv):
    """
    Entry point for creoclean.

    Arguments:
        argv: command line arguments
    """
    dr = "dry run; show what would be done but don't delete files"
    opts = argparse.ArgumentParser(prog='creoclean', description=__doc__)
    opts.add_argument('-d', dest='dry_run', action="store_true", help=dr)
    opts.add_argument('-v', '--version', action='version',
                      version=__version__)
    opts.add_argument('--log', default='warning',
                      choices=['debug', 'info', 'warning', 'error'],
                      help="logging level (defaults to 'warning')")
    opts.add_argument("dirs", metavar='dir', nargs='*', default=[],
                      help="one or more directories to process")
    args = opts.parse_args(argv)
    lfmt = '%(levelname)s: %(message)s'
    if args.dry_run:
        logging.basicConfig(level='INFO', format=lfmt)
        logging.info('DRY RUN, no files will be deleted or renamed')
    else:
        logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                            format=lfmt)
    if not args.dirs:
        args.dirs = ['.']
    for directory in [d for d in args.dirs if os.path.isdir(d)]:
        logging.info("cleaning in '{}'".format(directory))
        cleandir(directory, args.dry_run)


def cleandir(path, dry_run):
    """Clean up Creo files in the named directory

    Arguments:
        path: The path of the directory to clean.
        dry_run: Boolean to indicate a dry run.
    """
    filenames = [e for e in os.listdir(path) if
                 os.path.isfile(os.path.join(path, e))]
    logging.info('found {} files'.format(len(filenames)))
    splits = [re.split('^(.*)\.([^\.]{3})\.([0-9]+)$', fn) for fn in filenames]
    splits = [s[1:-1] for s in splits if len(s) == 5]
    exts = sorted(set([s[1] for s in splits]))
    for ext in exts:
        data = [s for s in splits if s[1] == ext]
        cnt = len(data)
        if cnt < 2:
            logging.info("not enough '{}' files; skipping".format(ext))
            continue
        logging.info("found {} '{}' files".format(cnt, ext))
        names = set(p[0] for p in data)
        logging.info("found {} unique '{}' file names".format(len(names), ext))
        for nm in names:
            numbers = [int(p[2]) for p in data if p[0] == nm]
            if len(numbers) > 1:
                numbers.sort()
                for n in numbers[:-1]:
                    fn = "{}.{}.{}".format(nm, ext, n)
                    logging.info("removing '{}'".format(fn))
                    if not dry_run:
                        os.remove(fn)
            oldfn = "{}.{}.{}".format(nm, ext, numbers[-1])
            newfn = "{}.{}.{}".format(nm, ext, 1)
            if oldfn != newfn:
                logging.info("renaming '{}' to '{}'".format(oldfn, newfn))
                if not dry_run:
                    os.rename(oldfn, newfn)


if __name__ == '__main__':
    main(sys.argv[1:])
