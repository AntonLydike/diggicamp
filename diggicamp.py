#!/usr/bin/env python3

import diggicamp
from clint.arguments import Args
from clint.textui import puts, colored, indent


def get_arg(name: str, default=None, optional: bool = False):
    if args.grouped.get(name) and args.grouped.get(name)[0]:
        return args.grouped.get(name)[0]
    if optional or default != None:
        return default
    print("Expected argument \"{}\" but got nothing!".format(name))
    exit(1)


def get_bool_arg(name: str):
    return args.grouped.get(name) != None


args = Args()
flags = set()

# remove flags from args
for flag in args.flags.all:
    if flag[:2] == '--':
        continue

    args.remove(flag)
    flags = flags.union(flag[1:])

if 'v' in flags:
    puts(colored.blue('Grouped Arguments: ') + str(dict(args.grouped)))
    puts(colored.blue('Flags: ') + str(flags))

arg0 = args.grouped.get('_')[0]

cfg_file = get_arg('--cfg', 'dgc.json')

dgc = diggicamp.d_open(cfg_file)

dgc.verbose = 'v' in flags

if arg0 == 'init':
    dgc = diggicamp.new(cfg_file)
    usr = get_arg('--user')
    pw = get_arg('--pass')
    dgc.conf.add_auth('plain', username=usr, password=pw)

    if args.grouped.get('_')[1]:
        dgc.conf.set('baseurl', args.grouped.get('_')[1])

elif arg0 == 'show':
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
elif arg0 == 'fetch':
    print("fetching new data from server...")
    diggicamp.fetch(dgc)
elif arg0 == 'pull':
    print("downloading defined folders from server...")
    dgc.download_cached_folders()
elif arg0 == 'add':
    course_name = args.grouped.get('_')[1]
    folder_name = args.grouped.get('_')[2]
    target = args.grouped.get('_')[3]

    if not course_name or not folder_name or not target:
        print("correct syntax is: add <course> <folder> <path> [--sem <semester>] [--regex <regex>]")
        exit(1)

    regex = get_arg('--regex', optional=True)

    course = diggicamp.course_by_name(dgc, course_name, semester_title=get_arg('--sem', optional=True))
    if not course:
        print(f"No course found for \"{course_name}\"")
        exit(1)

    folder = diggicamp.folder_by_name(dgc, folder_name, course)

    if not folder:
        print(f"No folder named \"{folder_name}\" found!")
        exit(1)

    diggicamp.add_download(dgc, folder['id'], target, regex)
else:
    print("""Usage: dgc [<flags>] <command> [<args>]

Download files for courses from digicampus.

flags:

     -v                      verbose mode - more output
     --cfg <path>            specify a config file path (default is dgc.json)

commands:

    init [<url>] --user <username> --pass <password>
                             Initialize a new config file
    show [--all]             show courses for the current (or all) semesters
    fetch                    refresh semester, courses, folders and files
    show <semester>          show courses in a specific semester
    show <course>            show files in a specific course from the current 
                             semester
    show <semester> <course> show files in a specific course from a specific
                             semester
    add <course> <folder> <target> [--sem <semster>] [--regex <regex>]
                             add a folder to the sync-list (it will sync with 
                             'dgc pull'). If no semester is specified, the 
                             current semester is assumed. If a regex is 
                             specified, only files matching it will be 
                             downloaded
    pull                     download all files from the folders on the 
                             sync-list to their destinations
""")

diggicamp.save(dgc, cfg_file)

print()
