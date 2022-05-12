"""
This file is intended to be called in a timer.

Depending on configuration it will add new courses to the configuration automatically and download all corresponding files.

If enabled a local nextcloud instance will be notified to update local file changes.
"""
import os
import sys

from clint import Args

from dotenv import load_dotenv

import diggicamp_cli
from diggicamp import CliException


def execute_diggicamp_cli(*params: str) -> int:
    """
    Executes the diggicamp cli using the given params
    @param params: command line params for the diggicamp cli
    @return: the status of the final execution
    """
    try:
        diggicamp_cli.exec_cli(Args(params))
        return 0
    except CliException as e:
        return e.status_code


def main():
    # load environment variables
    load_dotenv()
    USER = os.getenv('USER')
    PASS = os.getenv('PASS')
    CONFIG_LOCATION = os.getenv('CONFIG_LOCATION')
    DOWNLOAD_COURSES = os.getenv('DOWNLOAD_COURSES')
    DOWNLOAD_LOCATION = os.getenv('DOWNLOAD_LOCATION')
    REGEX = os.getenv('REGEX')
    NEXTCLOUD_HOSTNAME = os.getenv('NEXTCLOUD_HOSTNAME')
    NEXTCLOUD_SCAN_FOLDER = os.getenv('NEXTCLOUD_SCAN_FOLDER')

    # cache argv
    argv = sys.argv

    # create config if not exists
    execute_diggicamp_cli('init', '--cfg', CONFIG_LOCATION)

    # update config if exists

    # fetch
    execute_diggicamp_cli('fetch', '--cfg', CONFIG_LOCATION)

    # check if courses must be added (env) --> add courses
    if DOWNLOAD_COURSES.upper() == 'ALL':
        execute_diggicamp_cli('downloads', 'add', DOWNLOAD_LOCATION, '--all')
    elif DOWNLOAD_COURSES.upper() == 'CURRENT':
        execute_diggicamp_cli('downloads', 'add', DOWNLOAD_LOCATION, '--current')
    elif True:
        # TODO check if download courses is a list of courses and add those manually
        pass
    else:
        print('Please specify "DOWNLOAD_COURSES" in the correct format.')

    # pull
    execute_diggicamp_cli('pull', '--cfg', CONFIG_LOCATION)


if __name__ == '__main__':
    main()
