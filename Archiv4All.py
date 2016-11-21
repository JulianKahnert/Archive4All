#!/usr/bin/env python3

import argparse
import configparser
from datetime import datetime, date
import os
import sys


class file:
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

    def write_file(self, OCR=False):
        # TODO: error checking would be nice
        date = self.date.strftime('%Y-%m-%d')
        name = self.name.replace(' ', '-')
        tags = '_'.join(self.tags)
        ext = os.path.splitext(self._file)[-1][1:]
        filename = '{}--{}__{}.{}'.format(date, name, tags, ext)

        archiv_path = os.path.expanduser(self._config['default']['archiv_path'])
        print('new file:' + filename)
        # print('{}{}'.format(archiv_path, filename))
        os.rename(self._file, archiv_path + filename)


def config_update(add_tags=[], delete_tag=[]):
    tags = list(obj._config['tags'].keys())
    for item in add_tags:
        tags.append(add_tags)
    for item in delete_tag:
        tags.remove(item)
    tags.sort()

    obj._config.remove_section('tags')
    obj._config.add_section('tags')
    for cur_tag in tags:
        obj._config.set('tags', cur_tag)

    with open(self._config_path, 'w') as configfile:
        obj._config.write(configfile)
    obj._config.read(self._config_path)

if __name__ == '__main__':
    obj = file(sys.argv[1])
    now = datetime.now()

    # set year
    year = input('Year [{}]: '.format(now.year))
    year = year or now.year

    # set month
    month = input('Month [{}]: '.format(now.month))
    month = month or now.month

    # set day
    day = input('Month [{}]: '.format(now.day))
    day = day or now.day

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
        ans = input('choose tag ID or write tag: ')
        if ans == '':
            break

        if ans[0] == ':':
            obj.tags.append(ans[1:])
        else:
            obj.tags.append(obj._config_tags[int(ans)])

    print('=' * 10)
    print('\n YOUR RESULTS')
    print('-' * 10)
    print(obj.date.isoformat())
    print(obj.name)
    print(obj.tags)
    print('-' * 10)

    # update config
