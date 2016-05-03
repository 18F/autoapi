import subprocess


def when_ready(server):
    subprocess.Popen(['invoke', 'fetch_bucket'])
