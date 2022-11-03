# DiggiCamp

Scrape your digicampus (that use a very specific single sign-on)


## Installation

### Self-contained inside virtual environment:

If you don't want to install anything, just use `diggicamp-venv.sh` that automatically loads dependencies inside a virtual environment. Just symlink it into your desired PATH folder and everything will be taken care of. If you have any problems with the virtual environment, the script intercepts the `install` argument and reinstalls all dependencies again if supplied.

### Other

If you feel the need to pollute your global python package space, you can install dependencies manually by running `pip install -r requirements.txt`. You should probably not do this.

## Usage

This... thing... exposes a couple of ways to interact with it:

### CLI

to use the cli, link the `diggicamp_cli.py` script anywhere to your path (alias is `dgc` or something like that) and then use it like this:

```
Usage: dgc [<flags>] <command> [<args>] [--cfg <path>]

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
    fetch [--threads <threadcount>]
                             refresh semester, courses, folders and files. Use
                             <threadcount> threads for this (default 32)
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
    
    downloads add <course> [<folder>] <target> [--sem <semster>] [--regex <regex>]
                             add a folder (or all folders) of a course to the 
                             sync-list (it will sync with 'dgc pull'). If no 
                             semester is specified, the current semester is 
                             assumed. If a regex is specified, only files 
                             matching it will be downloaded
    downloads add <target> [--all|--current] [--regex <regex>]
                            --all: add all courses of all semesters to the sync-list
                            --current: add all courses of the current semester to the sync-list
                            If a regex is specified, only files 
                            matching it will be downloaded
                             
    downloads remove <id>    remove download with specified id
    pull [-f|--fetch] [--threads <threadcount>]
                             download all files from the folders on the
                             sync-list to their destinations. If not specified,
                             32 concurrent downloads are started
```

### Docker-compose

* Regularly built
* env
* env settings
* docker-compose
* docker-compose up -d

### Python package

You can also just import the `diggicamp` package in python3 and use it that way. Although documentation is scarce.

```python
from diggicamp import *

## Basics
# open an existing conf
dgc = d_open('path-to-your-dgc.json') #defaults to 'dgc.json'

# fetch from server
fetch(dgc, threads=16)

# create new dgc instance and save the dgc.json file
dgc = new('path-to-your-dgc.json') #defaults to 'dgc.json'
# add username and password to auth
dgc.conf.add_auth('plain', username="", password="")

# add a download config
add_download(dgc, folder_id, target_path) # optional pattern arg

# download all configured folders
pull(dgc, threads=64)

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
print_courses(dgc, course)
```

# structure of the config file

The config file is json. It has the following entries:
* `version`: a version string representing the version of diggicamp
* `baseurl`: the base url of the digicampus website
* `credentials`: the credentials. Format for this is:
  * `mode`: the credential mode used. Available modes:
    * `plain`: The credentials are stored in plaintext in the fields `username` and `password`
    * `prompt`: Ask the user for his password every time login is required (this does not happen often, as the session is saved between executions)
* `courses`: An array of semesters. Sorted in descending order, so the first element is the current semester
  * `title`: Semester title
  * `courses`: An array of the courses of the semester
* `downloads`: An array of download rules with these fields:
  * `course`: id of the course
  * `target`: path where to download
  * `regex`: (optional) a regex files not matching will be ignored
* `course_download`: The file and folder information scraped from digicampus. A dictionary with course ids as keys. Value has the following fields:
  * `root_files`: Array of files in the root folder of the course
  * `folders`: Array of subfolders. Each entry has the following fields
    * `id`: Folder id
    * `name`: Folder name (includes full path from the course root)
    * `files`: An array of files of this folder
  * Each file entry has the following fields:
    * `id`: file id
    * `name`: file name (displayed, no file ending)
    * `fname`: file name (real, with file ending)
    * `type`: ?
    * `last_mod`: When the file was last modified on digicampus (is usually the upload time)
* `cookies`: session cookies, used internally
* `downloaded_versions`: The versions of the downloaded files to prevent double downloads. A dictionary with file id as key and download time as value

# TO-DO:

* [X] multithreaded downloads
* [X] multithreaded sync
* [X] pull with fetch in one command
* [ ] cli autocomplete
* [ ] multiple auth options (pass, prompt, etc)
* [X] store session between calls
* [ ] compare regex before downloading
