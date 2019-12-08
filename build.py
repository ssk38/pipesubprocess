#!/usr/bin/env python3

from pynt import task

from subprocess import run


@task()
def clean():
    '''Clean build directory.'''
    print('Cleaning')
    run("rm -rf build dist", shell=True)

@task()
def test():
    '''Run unittest'''
    print('Testing')
    run("python3 -m unittest test.test", shell=True)

@task(clean, test)
def build(target='.'):
    '''build pipesubprocess.'''
    print('Building')
    run("python3 setup.py bdist_wheel", shell=True)

@task()
def testrelease():
    '''Release to test.pypip.org.'''
    print('Releasing')
    run("ython3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*", shel=True)

@task()
def testrelease():
    '''Release to pypip.org.'''
    print('Releasing')
    run("ython3 -m twine upload dist/*", shel=True)

