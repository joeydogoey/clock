import subprocess

def start_radio(url):
    return subprocess.Popen(
        ["mpg123", "-q", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def stop_radio(proc):
    if proc:
        proc.terminate()
