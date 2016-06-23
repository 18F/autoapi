import os
import sys
import pwd
import subprocess
from dotenv import load_dotenv


MY_DIR = os.path.abspath(os.path.dirname(__file__))
HOST_UID = os.stat(MY_DIR).st_uid
HOST_USER = 'autoapi_user'
DOTENV_PATH = os.path.join(os.path.dirname(__file__), '.env')


def entrypoint(argv):
    '''
    This is a Docker entrypoint that configures the container to run
    as the same uid of the user on the host container, rather than
    the Docker default of root. Aside from following security best
    practices, this makes it so that any files created by the Docker
    container are also owned by the same user on the host system.
    '''

    if HOST_UID != os.geteuid():
        if not does_uid_exist(HOST_UID):
            username = HOST_USER
            while does_username_exist(username):
                username += '0'
            home_dir = '/home/%s' % username
            subprocess.check_call([
                'adduser',
                '-h', home_dir,
                '-u', str(HOST_UID),
                '-S', username,
            ])
        os.environ['HOME'] = '/home/%s' % pwd.getpwuid(HOST_UID).pw_name
        os.setuid(HOST_UID)

    if not os.path.exists('/autoapi/node_modules'):
        subprocess.check_call(
            "ln -s /tmp/node_modules /autoapi/node_modules",
            shell=True
        )

    os.execvp(argv[1], argv[1:])


def does_username_exist(username):
    '''
    Returns True if the given OS username exists, False otherwise.
    '''

    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def does_uid_exist(uid):
    '''
    Returns True if the given OS user id exists, False otherwise.
    '''

    try:
        pwd.getpwuid(uid)
        return True
    except KeyError:
        return False


if __name__ == "__main__":
    if os.path.exists(DOTENV_PATH):
        load_dotenv(DOTENV_PATH)
    entrypoint(sys.argv)
