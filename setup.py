#!/usr/bin/env python3

from setuptools import setup

def main():
    setup(
        setup_require=['setuptools_scm'],
        use_scm_version=True,
    )

if __name__ == "__main__":
    main()
