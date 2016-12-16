#!/usr/bin/env python3

import argparse
import collections
import configparser
from datetime import date
from datetime import datetime
import glob
import json
import os
import re
from shutil import copyfile, move
from subprocess import Popen, PIPE
from tqdm import tqdm


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
    _file_extension = '.pdf'
    _date_format = '%Y-%m-%d'
    _date_sep = '--'
    _tags_sep = '__'
    _tag_sep = '_'

    file_list = []

    def __init__(self):
        self._basepath = os.path.dirname(os.path.realpath(__file__))
        self._config_path = os.path.join(self._basepath, self._config_file)

    def parse_config_file(self):
        self._config = configparser.ConfigParser(allow_no_value=True)
        self._config.read(self._config_path)

        if len(self._config.sections()) == 0:
            raise Exception('Config file is empty or does not exist.')

        input_paths = self._config['Directories'].get('input_paths')
        if input_paths is not None:
            input_paths = [os.path.expanduser(in_path) for in_path in
                           json.loads(input_paths)]

        self.file_list = self.file_list + glob_directory(input_paths,
                                                         self._file_extension)

        self.archive_path = os.path.expanduser(
                            self._config['Directories'].get('output_path'))
        if self.archive_path is None:
            raise Exception('No output path specified.')

        self._movefile = self._config['Defaults'].get('copy_or_move') == 'move'
        self._yearly_subfolder = self._config['Defaults'].getboolean('yearly_subfolder', 'False')
        self._add_mac_tags = self._config['Defaults'].getboolean('add_mac_tags', 'False')
        self._num_tags_top = self._config['Defaults'].getint('num_top_tags')
        self._open_pdf_in = self._config['Defaults'].get('open_pdf_in')

        self.gather_tags_from_archive()
        if len(self.tag_list) == 0:
            raise Exception('No tags specified.')

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

            return

        input_paths = self._args.directory_list
        self.file_list = self.file_list + glob_directory(input_paths,
                                                         self._file_extension)

        input_files = self._args.file_list
        self.file_list = self.file_list + input_files

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

        if len(self.file_list) == 0:
            raise Exception('No files have been added for processing.')

        for path in tqdm(self.file_list):
            self.q_and_a(path)

    def q_and_a(self, file_path):
        print('>>>  ' + file_path.split(os.path.dirname(file_path) + '/')[1])
        p = Popen(['open', '--background', '-a', self._open_pdf_in, file_path])
        obj = ArchiveFile(self, file_path)
        # save creation time of file as default

        # set year
        year = input('Year [{}]: '.format(obj.date.year))
        year = year or obj.date.year
        year = int(year)
        if year < 100:
            year += 2000

        # set month
        month = input('Month [{}]: '.format(obj.date.month))
        month = month or obj.date.month
        month = int(month)

        # set day
        day = input('Day [{}]: '.format(obj.date.day))
        day = day or obj.date.day
        day = int(day)
        obj.date = date(year, month, day)

        # set name
        name = input('Name [{}]: '.format(obj.name))
        obj.name = name or obj.name

        # set tags
        ## config tags
        print('\nID: name')
        print('=' * 10)
        for idx, cur_tag in enumerate(self.tag_list_config):
            print('{}: {}'.format(idx, cur_tag))

        ## top tags
        print('-' * 10)
        # order of elements not relevant!?
        tag_list_top = list(set(self.tag_list_top) - set(self.tag_list_config))
        tag_list_top.sort()
        for idx, cur_tag in enumerate(tag_list_top):
            print('{}: {}'.format(idx + len(self.tag_list_config), cur_tag))

        ## other tags
        print('-' * 10)
        tag_list_other = list(set(self.tag_list) - set(self.tag_list_config + self.tag_list_top))
        tag_list_other.sort()
        for idx, cur_tag in enumerate(tag_list_other):
            print('{}: {}'.format(idx + len(self.tag_list_config + self.tag_list_top), cur_tag))

        #TODO: tags is not empty here, if parsing was successful
        #      set them as default tags, when there is a UI to remove tags
        obj.tags = []
        while True:
            print('\ncurrent tags:')
            print(obj.tags)
            ans = input('choose tag ID or write tag: ')

            # Empty string exits the loop
            if ans == '':
                break

            # A regex match for digit-only value is interpreted as ID
            matched_numeral = re.match('^(\d+)$', ans)
            if matched_numeral is not None:
                try:
                    idx = int(matched_numeral.group(0))
                    # chosen: config tag
                    if idx < len(self.tag_list_config):
                        obj.tags.append(self.tag_list_config[idx])

                    # chosen: top tag
                    elif len(self.tag_list_config) <= idx < len(self.tag_list_config + self.tag_list_top):
                        idx -= len(self.tag_list_config)
                        obj.tags.append(tag_list_top[idx])

                    # chosen: other tag
                    else:
                        idx -= len(self.tag_list_top)
                        idx -= len(self.tag_list_config)
                        obj.tags.append(tag_list_other[idx])

                except IndexError:
                    print('No tag with that ID.')
                    continue

            # A non-match will be added as a new tag
            else:
                ans = ans.lower()
                obj.tags.append(ans)
                self.tag_list.append(ans)
                self.tag_list.sort()

        obj.write_file()

    def gather_tags_from_archive(self):
        # get all tags from archive
        all_tags = []
        for cur_file in glob_directory(self.archive_path, self._file_extension):
            _, _, file_tags = self.parse_archive_file(cur_file)
            all_tags += file_tags

        self.tag_list = list(set(all_tags))
        self.tag_list.sort()

        # get the TopX of the archive tags
        self.tag_list_top = []
        for name, _ in collections.Counter(all_tags).most_common(self._num_tags_top):
            self.tag_list_top.append(name)

        # get tags from config
        self.tag_list_config = list(self._config['Tags'].keys())

    def parse_archive_file(self, file_path):
        file_name = os.path.basename(file_path)[:-
                                                len(self._file_extension)]

        name_regex = re.match('(.*){}(.*){}(.*)'.format(self._date_sep,
                                                        self._tags_sep),
                              file_name)

        if name_regex is None:
            raise Exception('File name cannot be parsed.')
            # TODO: Turn into soft error?

        file_date = datetime.strptime(name_regex.group(1),
                                      self._date_format).date()
        file_name = name_regex.group(2)
        file_tags = name_regex.group(3).split(self._tag_sep)

        return file_date, file_name, file_tags


class ArchiveFile:
    def __init__(self, toolkit, file_in):
        # TODO: relative path to absolute path?
        self._file = file_in
        self._toolkit = toolkit
        self._basepath = os.path.dirname(os.path.realpath(__file__))

        # try to parse data from filename
        try:
            self.date, self.name, self.tags = self._toolkit.parse_archive_file(file_in)
        except Exception:
            self.date = datetime.fromtimestamp(os.path.getctime(self._file))
            self.name = ''
            self.tags = []

    def write_file(self):
        # TODO: error checking would be nice
        date = self.date.strftime(self._toolkit._date_format)
        name = _strnorm(self.name)
        self.tags.sort()
        tags = self._toolkit._tag_sep.join(self.tags)
        ext = os.path.splitext(self._file)[-1]
        filename = '{}{}{}{}{}{}'.format(date,
                                         self._toolkit._date_sep,
                                         name,
                                         self._toolkit._tags_sep,
                                         tags,
                                         ext)

        # archive files in yearly subfolders
        if self._toolkit._yearly_subfolder:
            year_dir = self.date.strftime('%Y')
        else:
            year_dir = ''

        # create a new directory if it does not already exist
        target_path = os.path.join(self._toolkit.archive_path,
                                   year_dir)
        target_file = os.path.join(self._toolkit.archive_path,
                                   year_dir, filename)

        if not os.path.isdir(target_path):
            os.makedirs(target_path)

        # rename and move/copy file
        if os.path.isfile(target_file):
            raise RuntimeError('File already exists!')

        if self._toolkit._movefile:
            move(self._file, target_file)
        else:
            copyfile(self._file, target_file)

        if self._toolkit._add_mac_tags:
            update_mac_tags(target_file)

def update_mac_tags(file_path):
    p = Popen(['tag', '--list', '--garrulous', '--no-name', file_path], stdout=PIPE)
    file_tags = p.stdout.read().decode("utf-8")[:-1]
    file_tags = set(file_tags.split('\n'))
    name_tags = set(name2tags(file_path))

    # delete tags from attr
    for attr in file_tags - name_tags:
        Popen(['tag', '--remove', attr, file_path])

    # add tags to attr
    for attr in name_tags - file_tags:
        Popen(['tag', '--add', attr, file_path])

def name2tags(file):
    # list all files (not just pdf files)
    file = file.split(os.path.dirname(file) + '/')[1]   # filename
    file = file.split('__')[1]                          # tags + ext
    file = file.split('.')[0]                           # tags
    return file.split('_')

def _strnorm(sz):
    sz = sz.lower()
    sz = sz.replace(' ', '-')
    sz = sz.replace('ä', 'ae')
    sz = sz.replace('ö', 'oe')
    sz = sz.replace('ü', 'ue')
    sz = sz.replace('ß', 'ss')
    return sz


def glob_directory(path_or_paths, file_extension):

    if type(path_or_paths) is str:
        path_or_paths = [path_or_paths]

    file_list = []
    for path in path_or_paths:
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise Exception('Path does not exist')

        file_list = file_list + glob.glob(os.path.join(path,
                                                       '**',
                                                       '*' +
                                                       file_extension),
                                          recursive=True)

    return file_list


if __name__ == '__main__':

    at = ArchiveToolkit()
    at.main()
