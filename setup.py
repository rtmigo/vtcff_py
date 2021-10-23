from pathlib import Path

from setuptools import setup, find_packages

name = "vtcff"

readme = (Path(__file__).parent / 'README.md').read_text(encoding="utf-8")

setup(
    name=name,
    version='0.0.0',

    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/vtcff_py',

    packages=find_packages(), #include=['vtcff', 'vtcff.*']),

    python_requires='>=3.9',
    install_requires=[],

    long_description=readme,
    long_description_content_type='text/markdown',

    license="MIT",

    keywords="".split(),

    classifiers=[
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Typing :: Typed",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows"
    ],
)
