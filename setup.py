from pathlib import Path

from setuptools import setup, find_packages

name = "vtcff"

readme = (Path(__file__).parent / 'README.md').read_text(encoding="utf-8")

setup(
    name=name,
    version='0.1.0',

    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/vtcff_py',

    packages=find_packages(include=['vtcff', 'vtcff.*']),

    python_requires='>=3.8',
    install_requires=['framefile'],

    description="Ffmpeg wrapper for transcoding between video formats with "
                "an emphasis on maintaining quality and color depth "
                "in video production pipelines",

    long_description=readme,
    long_description_content_type='text/markdown',

    license="MIT",

    keywords="ffmpeg wrapper "
             "codec encoder decoder transcoding "
             "video audio".split(),

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows"
    ],
)