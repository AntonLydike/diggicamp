# DiggiCamp

Scrape your digicampus (that use a very specific single sign-on)


## Usage

This... thing... exposes a couple of ways to interact with it:

### CLI
to use the cli, link the `diggicamp.py` script anywhere to your path (alias is `dgc` or something like that) and then use it like this:

```
Usage: dgc [<flags>] <command> [<args>]

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
```

### Python package

You can also just import the `diggicamp` package in python3 and use it that way. Although documentation is scarce.

```python3
from diggicamp import *

## Basics
# open an existing conf
dgc = d_open('path-to-your-dgc.json') #defaults to 'dgc.json'

# fetch from server
fetch(dgc)

# create new dgc instance and save the dgc.json file
dgc = new('path-to-your-dgc.json') #defaults to 'dgc.json'
# add username and password to auth
dgc.conf.add_auth('plain', username="", password="")

# add a download config
add_download(dgc, folder_id, target_path) # optional pattern arg

# download all configured folders
pull(dgc)

## Helpers:

# find semesters
semester_by_name(dgc, 'SS 2019')

# find courses 
course = course_by_name(dgc, 'Analysis II') # optional semster_title

# find folders
folder_by_name(dgc, 'Script', course)

# find courses by id:
course_by_id(dgc, 'a0808df98009adfe98af')

## Printing

# print courses
print_courses(dgc, all=True)

# print folders in a course
print_curses(dgc, course)
```


# TO-DO:

* [ ] multithreaded downloads
* [ ] multithreaded sync
* [ ] pull with fetch in one command
* [ ] cli autocomplete
* [ ] multiple auth options (pass, prompt, etc)
* [ ] store session between calls
