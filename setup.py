import os
from setuptools import setup


setup(
    name = "moto-interceptor",
    packages = ["moto_interceptor"],
    scripts = ["bin/moto-interceptor"],
    version = "0.0.1",
    author = "Tay Frost",
    author_email = "tay@taybird.com",
    description = ("Intercept and redirect AWS traffic to Moto."),
    url = "https://github.com/tay-bird/moto-interceptor",
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
