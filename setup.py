import os
#from pipenv.project import Project
#from pipenv.utils import convert_deps_to_pip
from setuptools import setup


#pipfile = Project(chdir=False).parsed_pipfile
#requirements = convert_deps_to_pip(pipfile['packages'], r=False)

setup(
    name = "moto-interceptor",
    dependency_links=["http://github.com/spulec/moto/tarball/64152f4#egg=moto"],
    install_requires = ["cryptography", "flask", "moto"],
    packages = ["moto_interceptor"],
    scripts = ["bin/moto-interceptor"],
    version = "0.0.1",
    author = "Tay Frost",
    author_email = "tay@taybird.com",
    description = ("Intercept and redirect AWS traffic to Moto."),
    url = "https://github.com/tay-bird/moto-interceptor",
    classifiers = [
        "Development Status :: 3 - Alpha",
    ],
)
