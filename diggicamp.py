#!/usr/bin/env python3

import os

from clint.arguments import Args
from clint.textui import puts, colored

import diggicamp
from diggicamp import Diggicamp


def get_arg(name: str, default=None, optional: bool = False):
    if args.grouped.get(name) and args.grouped.get(name)[0]:
        return args.grouped.get(name)[0]
    if optional or default is not None:
        return default
    print("Expected argument \"{}\" but got nothing!".format(name))
    exit(1)


def get_bool_arg(name: str):
    return args.grouped.get(name) is not None


# Parse args flags
args = Args()
flags = set()

# remove flags from args
for flag in args.flags.all:
    if flag[:2] == '--':
        continue

    args.remove(flag)
    flags = flags.union(flag[1:])

# if verbose mode is on, print args
if 'v' in flags:
    puts(colored.blue('Grouped Arguments: ') + str(dict(args.grouped)))
    puts(colored.blue('Flags: ') + str(flags))
    print()

# get first arg
ARG0 = args.grouped.get('_')[0]

# get config file location
CFG_FILE = get_arg('--cfg', 'dgc.json')

# get number of threads
THREADS = int(get_arg('--threads', 32))

# initialize dgc variable
dgc: Diggicamp | None = None

# first, check for init
if ARG0 == 'init':
    dgc = diggicamp.new(args.grouped.get('_')[1], CFG_FILE)

    # error while initializing (config file already exists, etc)
    if not dgc:
        exit(1)

    usr = get_arg('--user')
    pw = get_arg('--pass', optional=True)

    if not pw:
        dgc.conf.add_auth('prompt', username=usr)
    else:
        dgc.conf.add_auth('plain', username=usr, password=pw)

    diggicamp.save(dgc, CFG_FILE)
    exit(0)

# if we are not in init mode, try to read the config file
if os.path.isfile(CFG_FILE):
    dgc = diggicamp.d_open(CFG_FILE)
    dgc.verbose = 'v' in flags
elif ARG0 and ARG0 != 'help':
    print("Diggicamp is not configured! Run\n\n    dgc init <url> --user <user> --pass <password>\n\nto initialize a new config")
    exit(1)

if 'dgc' not in globals():
    print("An unexpected error occurred. Please check for any mistakes and create an issue on github if you cannot resolve the issue.")
    exit(1)

if ARG0 == 'show':
    if not args.grouped.get('_')[1]:
        # no arg supplied, list courses with optional all flag
        diggicamp.print_courses(dgc, all=get_bool_arg('--all'))
    elif not args.grouped.get('_')[2]:
        # one arg supplied, is it a semester name? then list semester
        arg1 = args.grouped.get('_')[1]
        if diggicamp.semester_by_name(dgc, arg1):
            diggicamp.print_courses(dgc, course=diggicamp.semester_by_name(dgc, arg1))
        elif diggicamp.course_by_name(dgc, arg1):
            # if it's not a semester, it must be a course name from the current semester
            diggicamp.print_folders(dgc, diggicamp.course_by_name(dgc, arg1))
        else:
            # if it's neither, display a not found msg
            print(f"Nothing found for \"{arg1}\"!")
            exit(1)
    else:
        # we got two args
        sem_title = args.grouped.get('_')[1]  # first arg is semester
        course_title = args.grouped.get('_')[2]  # second arg is course
        course = diggicamp.course_by_name(dgc, course_title, semester_title=sem_title)

        if not course:
            print(f'Course \"{course_title}\" was not found in semester \"{sem_title}\"!')
            exit(1)

        diggicamp.print_folders(dgc, course)
elif ARG0 == 'fetch':
    print("Fetching new data from server...")
    diggicamp.fetch(dgc, threads=THREADS)
elif ARG0 == 'pull':
    if 'f' in flags or get_bool_arg('--fetch'):
        print("Fetching new data from server...")
        diggicamp.fetch(dgc, threads=THREADS)

    print("Downloading defined folders from server...")
    diggicamp.pull(dgc, threads=THREADS)
elif ARG0 == 'clean':
    print("Cleaning old files and download entries from cache...")
    diggicamp.clean_config(dgc)
elif ARG0 == 'downloads' or ARG0 == 'dl':
    ARG1 = args.grouped.get('_')[1]

    if not ARG1 or ARG1 == 'show':
        diggicamp.print_download_definitions(dgc)

    elif ARG1 == 'add':
        course_name = args.grouped.get('_')[2]
        folder_name = args.grouped.get('_')[3]
        target = args.grouped.get('_')[4]
        regex = get_arg('--regex', optional=True)

        download_all, download_current = get_bool_arg('--all'), get_bool_arg('--current')

        incorrect_syntax_message = "Correct syntax is:\n\t- add <course> [<folder>] <path> [--sem <semester>] [--regex <regex>]\n\t- add <path> [--all|--current] [--regex <regex>] # semester and course name will be appended to the path."

        if download_all or download_current:
            if not course_name:
                print(incorrect_syntax_message)
                exit(1)
            target = course_name  # because fewer parameters are required --> course name is actually the target
            courses = [(course, semester) for semester in dgc.get_courses()[:1 if download_current else None] for course in semester["courses"]]
            for course, semester in courses:
                diggicamp.add_download(dgc, course['id'], os.path.join(target, semester['title'], course['name']) if target else semester["title"], regex, 'course')
            diggicamp.save(dgc, CFG_FILE)
            exit(0)

        if not target or not course_name:
            print(incorrect_syntax_message)
            exit(1)

        if not target:
            target = folder_name
            folder_name = None

        course = diggicamp.course_by_name(dgc, course_name, semester_title=get_arg('--sem', optional=True))

        if not course:
            print(f"No course found for \"{course_name}\"")
            exit(1)

        if not folder_name:
            diggicamp.add_download(dgc, course['id'], target, regex, 'course')
        else:
            folder = diggicamp.folder_by_name(dgc, folder_name, course)

            if not folder:
                print(f"No folder named \"{folder_name}\" found!")
                exit(1)

            diggicamp.add_download(dgc, folder['id'], target, regex, 'folder')

        puts(colored.blue("Added download rule:\n", bold=True))
        diggicamp.print_download_definitions(dgc)

    elif ARG1 == 'remove':
        index = int(args.grouped.get('_')[2])
        dls: list = dgc.conf.get('downloads')
        if not dls or index > len(dls) - 1:
            puts(colored.red("No download rule #{} found!\n".format(index), bold=True))
            puts("Available rules are:\n")
            diggicamp.print_download_definitions(dgc)
            print()
            exit(1)
        dls.remove(dls[index])
        dgc.conf.set('downloads', dls)

        puts(colored.blue("Successfully deleted rule #{}!\n".format(index), bold=True))
        diggicamp.print_download_definitions(dgc)
else:
    print("""Usage: dgc [<flags>] <command> [<args>] [--cfg <path>]

Download files for courses from digicampus.

flags:

     -v                      verbose mode - more output


other args:

     --cfg <path>            specify a config file path (default is dgc.json)


commands:

    init [<url>] --user <username> [--pass <password>]
                             initialize a new config file. if no password is 
                             specified, you will be prompted, everytime it is
                             required (not very often).
    fetch [--threads <thread count>]
                             refresh semester, courses, folders and files. Use
                             <thread count> threads for this (default 32)
    show [--all]             show courses for the current (or all) semesters
    show <semester>          show courses in a specific semester
    show <course>            show files in a specific course from the current
                             semester
    show <semester> <course> show files in a specific course from a specific
                             semester
    clean                    cleans cached folders and files, deletes all 
                             download rules. This can be used to easily clean
                             up all state after the semester is completed
      

handling downloads: ('downloads' can be shortened to 'dl')

    downloads [show]         list all entries in the sync-list
    downloads add <course> [<folder>] <target> [--sem <semester>] [--regex <regex>]
                             add a folder (or all folders) of a course to the 
                             sync-list (it will sync with 'dgc pull'). If no 
                             semester is specified, the current semester is 
                             assumed. If a regex is specified, only files 
                             matching it will be downloaded
    downloads remove <id>    remove download with specified id
    pull [-f|--fetch] [--threads <thread count>]
                             download all files from the folders on the
                             sync-list to their destinations. If not specified,
                             32 concurrent downloads are started
""")
    exit(0)

diggicamp.save(dgc, CFG_FILE)
