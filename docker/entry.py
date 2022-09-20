import os
import time

from docker import timer
from docker.user_group_handling import UnixUser

FILES_UID = int(os.getenv('FILES_UID', os.getenv('UID', '0')))
FILES_GID = int(os.getenv('FILES_GID', os.getenv('GID', '0')))

application_user = UnixUser(FILES_UID, FILES_GID)


for folder_name in ['/downloads', '/config']:
    res = application_user.exec(lambda: os.access(folder_name, os.W_OK))
    if res:
        continue  # already having access

    if not os.listdir(folder_name):
        os.chown(folder_name, FILES_UID, FILES_GID)
        continue
    else:
        print('Wrong permission and content in directory --> ask user to change permissions')
        exit(1)

while True:
    application_user.exec(timer.main)
    time.sleep(float(os.getenv('POLLING_INTERVAL', '900')))
