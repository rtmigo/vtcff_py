import subprocess


def lint():
    print("Running pylint...")
    r = subprocess.call(['pylint', 'vtcff'])
    if r & 1 or r & 2 or r & 32:
        print(f"pylint return code is {r}")
        if r & 1:
            print(f"fatal message")
        if r & 2:
            print(f"error message")

        exit(1)

    print("Running mypy...")
    if subprocess.call(['mypy', 'vtcff',
                        '--ignore-missing-imports']) != 0:
        exit(1)


if __name__ == "__main__":
    lint()
