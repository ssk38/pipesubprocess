with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    setup_require=['setuptools_scm'],
    use_scm_version=True,
)
