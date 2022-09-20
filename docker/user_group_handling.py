import os
from multiprocessing import Queue, Process
from typing import Callable

queue = Queue()


class UnixUser:
    def __init__(self, uid: int, gid: int):
        self.uid = uid
        self.gid = gid

    def apply_and_call(self, q: Queue, function: Callable):
        os.setgid(self.gid)
        os.setuid(self.uid)
        q.put(function())

    def exec(self, function: Callable):
        p = Process(target=self.apply_and_call, args=(queue, function))
        p.start()
        p.join()
        res = queue.get()
        return res


# def get_files_user_by_id(uid: int, default_username='download'):
#     status_code, stdout = execute_shell('id', str(uid))
#     if not status_code:
#         # user exists
#         return re.sub(r'[^)]*\(([^)]+).*', r'\1', stdout)
#
#     status_code, stdout = execute_shell('useradd', '-u', str(uid), default_username)
#     assert status_code == 0, 'user creation failed'
#     return default_username


# def get_files_group_by_id(gid: int, default_group_name='download') -> str:
#     status_code, stdout = execute_shell('getent', 'group', str(gid))
#
#     if not status_code:
#         # group exists
#         return re.sub(r':.*', '', stdout)
#
#     status_code, stdout = execute_shell('groupadd', '-g', str(gid), default_group_name)
#     assert status_code == 0, 'group creation failed'
#     return default_group_name
