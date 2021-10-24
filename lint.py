import subprocess


def lint():

    # pip3 install --upgrade setuptools pip distlib

    print("Running pylint...")
    r = subprocess.call(['pylint', 'vtcff'])
    if r & 1 or r & 2 or r & 32:
        exit(1)

    print("Running mypy...")
    if subprocess.call(['mypy', 'vtcff',
                        '--ignore-missing-imports']) != 0:
        exit(1)

if __name__ == "__main__":
    lint()