#!/usr/bin/env python3

import argparse
import configparser
import glob
import os
from subprocess import PIPE, Popen


def name2tags(file):
    # list all files (not just pdf files)
    file = file.split(os.path.dirname(file) + '/')[1]   # filename
    file = file.split('__')[1]                          # tags + ext
    file = file.split('.')[0]                           # tags
    return file.split('_')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Commandline tool to manipulate tags in archiv. You will find the path to the archiv in your "config.ini"!')

    parser.add_argument('-c', '--config',
                        dest='config',
                        action='store_true',
                        help='update tags: Archiv => config.ini')

    parser.add_argument('-mt', '--mac-tags',
                        dest='mac_tags',
                        action='store_true',
                        help='update macOS tags: Archiv => macOS Finder tags')

    args = parser.parse_args()

    basepath = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(basepath, 'config.ini')

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_path)
    archiv_path = os.path.expanduser(config['Directories']['output_path'])

    if args.config:
        # get all tags
        tag_list = []
        for cur_file in glob.glob(archiv_path + '/**/*.*', recursive=True):
            tag_list += name2tags(cur_file)
        tag_list = list(set(tag_list))
        tag_list.sort()

        # renew tags in config.ini
        config.remove_section('Tags')
        config.add_section('Tags')
        print('All tags in archiv:\n' + '-'*20)
        for cur_tag in tag_list:
            print('{}: {}'.format(tag_list.index(cur_tag), cur_tag))
            config.set('Tags', cur_tag)

        # write new config.ini
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    if args.mac_tags:
        # store number of deleted and added tags
        num_del_tags = 0
        num_add_tags = 0

        for cur_file in glob.glob(archiv_path + '/**/*.*', recursive=True):
            p = Popen(['tag', '--list', '--garrulous', '--no-name', cur_file], stdout=PIPE)
            attr_tags = p.stdout.read().decode("utf-8")[:-1]
            attr_tags = set(attr_tags.split('\n'))
            name_tags = set(name2tags(cur_file))

            # delete tags from attr
            for attr in attr_tags - name_tags:
                Popen(['tag', '--remove', attr, cur_file])
                num_del_tags += 1

            # add tags to attr
            for attr in name_tags - attr_tags:
                Popen(['tag', '--add', attr, cur_file])
                num_add_tags += 1

        print('tags:\n\t{} added\n\t{} deleted'.format(num_add_tags, num_del_tags))