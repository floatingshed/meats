#!/usr/bin/env python

import os
import sqlite3
import sys

def get_alien_files__pipe():
    for line in os.popen('svn st --no-ignore'):
        if not line.strip():
            continue
        st, filename = line.split(None, 1)
        if st in 'I?':
            yield filename.strip()

def get_alien_files__entries(top='.'):
    from os.path import join, isdir, exists, islink
    entries_file = join(top, '.svn/entries')
    if not exists(entries_file):
        sys.stderr.write('Entries file not found in: '+top)
        return
    # print 'Entering', top
    entries = open(entries_file).read().split('\x0c\n')
    versioned = set(entry.split('\n', 1)[0] for entry in entries[1:-1])
    present = set(os.listdir(top)) - set(['.svn'])
    if top == '.':
        top = ''
    for non_versioned in present - versioned:
        candidate = join(top, non_versioned)
        if isdir(candidate) and not islink(candidate) and exists(join(candidate, '.svn')):
            # caveat: this is an external working copy
            continue
        yield candidate
    for entry in versioned:
        maybe_subdir = join(top, entry)
        if isdir(maybe_subdir):
            for alien in get_alien_files__entries(maybe_subdir):
                yield alien

def _get_alien_files(versioned, top='', externals=set()):
    """Return files not in versioned set."""
    from os.path import join, exists, isdir, islink
    present = filter(lambda x: x != '.svn', os.listdir(top if top else '.'))
    for filename in present:
        full_path = join(top, filename)
        if full_path in externals:
            # would need another list of versioned, just skip it:
            continue
        if full_path not in versioned:
            yield full_path
        elif isdir(full_path) and not islink(full_path):
            for alien in _get_alien_files(versioned, full_path, externals):
                yield alien
    
def get_alien_files__db(wc_root=''):
    wcdb_file = os.path.join(wc_root, '.svn', 'wc.db')
    if not os.path.exists(wcdb_file):
        sys.stderr.write('Database file wanted, but not found.')
        return []
    conn = sqlite3.connect(wcdb_file)
    c = conn.cursor()
    c.execute('select local_relpath from nodes')
    versioned = set(t[0] for t in c.fetchall())
    c.execute('select local_relpath from externals')
    externals = set(t[0] for t in c.fetchall())
    # print 'Warning - externals:', externals
    conn.close()
    return _get_alien_files(versioned, externals=externals)

def test():
    # print 'pipe:', sorted(get_alien_files__pipe())[:10]
    # print 'entries:', sorted(get_alien_files__entries())[:10]
    entries = set(get_alien_files__entries())
    pipe = set(get_alien_files__pipe())
    print 'Not in pipe:', entries-pipe
    print 'Not in entrie:', pipe-entries

def get_alien_files(top='.'):
    entries = os.path.join(top, '.svn', 'entries')
    if os.path.exists(entries) and int(open(entries).readline().strip()) <= 10:
        return get_alien_files__entries()
    return get_alien_files__db()

for filename in get_alien_files():
    print filename

