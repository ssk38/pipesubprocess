#!/usr/bin/env python3

from setuptools import setup

def main():
    setup(
        setup_require=['setuptools_scm'],
        use_scm_version=True,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License"],
    )

if __name__ == "__main__":
    main()
