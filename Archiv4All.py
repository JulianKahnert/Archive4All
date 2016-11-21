#!/usr/bin/env python3

import configparser
from datetime import date
from datetime import datetime as dt
import glob
import os
from subprocess import Popen
import sys


class archiv_file:
    def __init__(self, file):
        # TODO: relative path to absolute path?
        self._file = os.path.expanduser(file)
        self._config = configparser.ConfigParser(allow_no_value=True)
        self._basepath = os.path.dirname(os.path.realpath(__file__))
        self._config_path = os.path.join(self._basepath, 'config.ini')
        self._config.read(self._config_path)

        self._config_tags = list(self._config['tags'].keys())

        # file attributes
        self.date = None
        self.name = None
        self.tags = None

    def write_file(self):
        # TODO: error checking would be nice
        date = self.date.strftime('%Y-%m-%d')
        name = _strnorm(self.name)
        self.tags.sort()
        tags = '_'.join(self.tags)
        ext = os.path.splitext(self._file)[-1][1:]
        filename = '{}--{}__{}.{}'.format(date, name, tags, ext)

        # create a new directory if it does not already exist
        archiv_path = os.path.expanduser(self._config['dir']['archiv_path'])
        path = '{}/{}'.format(archiv_path, self.date.year, filename)
        if not os.path.isdir(path):
            os.makedirs(path)

        # rename and move file
        print('new file:\n' + filename)
        if os.path.isfile('{}/{}'.format(path, filename)):
            raise RuntimeError('File already exists!')

        os.rename(self._file, '{}/{}'.format(path, filename))
        print('=' * 20)

    def _config_update(self, add_tag=[], delete_tag=[]):
        tags = list(self._config['tags'].keys())
        for item in add_tag:
            tags.append(add_tag)
        for item in delete_tag:
            tags.remove(item)
        tags.sort()

        self._config.remove_section('tags')
        self._config.add_section('tags')
        for cur_tag in tags:
            self._config.set('tags', cur_tag)

        with open(self._config_path, 'w') as configfile:
            self._config.write(configfile)
        self._config.read(self._config_path)


def _strnorm(sz):
    sz = sz.lower()
    sz = sz.replace(' ', '-')
    sz = sz.replace('ä','ae')
    sz = sz.replace('ö','oe')
    sz = sz.replace('ü','ue')
    sz = sz.replace('ß','ss')
    return sz

def q_and_a(file_path):
    print('current file:\n' + file_path)
    p = Popen(['open', '-a', 'safari', file_path])
    print('-' * 10)
    obj = archiv_file(file_path)

    # set year
    year = input('Year [{}]: '.format(dt.now().year))
    year = year or dt.now().year
    year = int(year)
    if year < 100:
        year += 2000

    # set month
    month = input('Month [{}]: '.format(dt.now().month))
    month = month or dt.now().month
    month = int(month)

    # set day
    day = input('Day [{}]: '.format(dt.now().day))
    day = day or dt.now().day
    day = int(day)
    obj.date = date(year, month, day)

    # set name
    obj.name = input('Name: ')
    # TODO: error if empty

    # set tags
    print('\nID: name')
    print('-' * 10)
    for cur_tag in obj._config_tags:
        print('{}: {}'.format(obj._config_tags.index(cur_tag), cur_tag))

    obj.tags = []
    while True:
        print('\ncurrent tags:')
        print(obj.tags)
        ans = input('choose tag ID or write tag: ')
        if ans == '':
            break

        if ans[0] == ':':
            obj.tags.append(ans[1:])
            obj._config_update(add_tag=ans[1:])
        else:
            obj.tags.append(obj._config_tags[int(ans)])

    obj.write_file()


if __name__ == '__main__':
    path_in = os.path.expanduser(os.path.normpath(sys.argv[1]))
    if os.path.isfile(path_in):
        q_and_a(path_in)

    else:
        extension = 'pdf'
        for file in glob.glob(path_in + '/**/*.' + extension, recursive=True):
            q_and_a(file)
