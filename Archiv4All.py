#!/usr/bin/env python3

import configparser
from datetime import date
from datetime import datetime
import glob
import os
from subprocess import Popen
import sys
from tqdm import tqdm
import argparse


# Partly inspired by https://stackoverflow.com/a/11415816/1177851
class append_readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        input_dir = os.path.expanduser(values)

        if not os.path.isdir(input_dir):
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not valid".format(input_dir))

        if os.access(input_dir, os.R_OK):
            dir_list = argparse._copy.copy(
                argparse._ensure_value(namespace, self.dest, []))
            dir_list.append(input_dir)
            setattr(namespace, self.dest, dir_list)
        else:
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not readable".format(input_dir))


class append_readable_file(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        input_files = glob.glob(os.path.expanduser(values))
        temp_list = []

        for input_file in input_files:
            print(input_file)
            if not os.path.isfile(input_file):
                raise argparse.ArgumentTypeError(
                    "readable_file:{0} is not valid".format(input_file))

            if os.access(input_file, os.R_OK):
                temp_list.append(input_file)
            else:
                raise argparse.ArgumentTypeError(
                    "readable_file:{0} is not readable".format(input_file))

            if len(temp_list) > 0:
                file_list = argparse._copy.copy(
                    argparse._ensure_value(namespace, self.dest, []))
                file_list = file_list + temp_list
                setattr(namespace, self.dest, file_list)


class ArchiveToolkit:

    _config_file = 'config.ini'
    _config_file_example = 'config.ini.example'

    def __init__(self):
        self._basepath = os.path.dirname(os.path.realpath(__file__))
        self._config_path = os.path.join(self._basepath, self._config_file)

    def parse_config_file(self):
        self._config = configparser.ConfigParser(allow_no_value=True)
        self._config.read(self._config_path)

        if len(self._config.sections()) == 0:
            raise Exception('Config file is empty or does not exist.')

    def parse_command_line(self):
        parser = argparse.ArgumentParser(description='''
            Archive4All – Toolkit for file tagging and archiving tasks.
                                         ''',
                                         fromfile_prefix_chars="@")
        parser.add_argument('-d', '--dir',
                            metavar='DIRECTORY', dest='directory_list',
                            action=append_readable_dir, default=[],
                            help='''
            Add files from the existing and readable DIRECTORY for processing.
            This option may be used multiple times, each time adding another
            directory.
                            ''')
        parser.add_argument('-f', '--file',
                            metavar='FILE', dest='file_list',
                            action=append_readable_file, default=[],
                            help='''
            Add an existing and reable FILE for processing. Just as -d/--dir
            this option may be used multiple times, each time adding another
            file. Of course it is allowed to use glob patterns (i.e.
            "path/to/*.pdf").
                            ''')
        parser.add_argument('-c', '--config',
                            metavar='CONFIGFILE', dest='config_file',
                            default=self._config_path,
                            help='''
            Change the path to the config file to wherever you want. By default
            the config.ini is loaded from the Toolkit's base directory. Both
            absolute and relative paths are allowed, with the latter of course
            being relative to the current working directory
                            ''')
        parser.add_argument('-nc', '--new-config',
                            dest='new_config',
                            action='store_true',
                            help='''
            When this option is set, the Toolkit will simply create a new
            config file in the default location an exit. A neat little shortcut
            for copying the example configuration file. In conjunction with -c/
            --config this will cause the config to be created in a non-default
            place.
                            ''')

        self._args = parser.parse_args()

        # Overwrite current config file/path
        self._config_file = os.path.basename(self._args.config_file)
        self._config_path = self._args.config_file

        # Copy example config to new location
        if self._args.new_config:
            if os.path.isfile(self._config_path):
                raise Exception('Config file already exists.')

            from shutil import copyfile
            copyfile(os.path.join(self._basepath, self._config_file_example),
                     os.path.join(self._basepath, self._config_file))

    def main(self):
        """
        Main method to run everything in ArchiveToolkit the way it's
        intended to be. When called directly (not from inside another Python
        function or shell) this function handles parsing of config, command
        line arguments, and –after that— the processing of the given files.
        """

        self.parse_command_line()
        self.parse_config_file()

        self.process_files()

    def process_files(self):
        input_list = args.directory_list + args.file_list
        if len(input_list) == 0:
            parser.print_usage()
        else:
            for path_in in tqdm(input_list):
                if os.path.isfile(path_in):
                    self.q_and_a(path_in)
                else:
                    extension = 'pdf'
                    for path_in in tqdm(glob.glob(path_in +
                                                  '/**/*.' +
                                                  extension,
                                                  recursive=True)):
                        self.q_and_a(path_in)

    def q_and_a(file_path):
        print('>>>  ' + file_path.split(os.path.dirname(file_path) + '/')[1])
        p = Popen(['open', '-a', 'safari', '--background', file_path])
        obj = ArchiveFile(file_path)
        # save creation time of file as default
        file_date = datetime.fromtimestamp(os.path.getctime(file_path))

        # set year
        year = input('Year [{}]: '.format(file_date.year))
        year = year or file_date.year
        year = int(year)
        if year < 100:
            year += 2000

        # set month
        month = input('Month [{}]: '.format(file_date.month))
        month = month or file_date.month
        month = int(month)

        # set day
        day = input('Day [{}]: '.format(file_date.day))
        day = day or file_date.day
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


class ArchiveFile:
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
        archive_path = os.path.expanduser(self._config['dir']['archive_path'])
        path = '{}/{}'.format(archive_path, self.date.year, filename)
        if not os.path.isdir(path):
            os.makedirs(path)

        # rename and move file
        if os.path.isfile('{}/{}'.format(path, filename)):
            raise RuntimeError('File already exists!')
        os.rename(self._file, '{}/{}'.format(path, filename))

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
    sz = sz.replace('ä', 'ae')
    sz = sz.replace('ö', 'oe')
    sz = sz.replace('ü', 'ue')
    sz = sz.replace('ß', 'ss')
    return sz


if __name__ == '__main__':

    at = ArchiveToolkit()
    at.main()
