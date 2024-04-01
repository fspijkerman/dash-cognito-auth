#!/usr/bin/env python

from setuptools import setup

setup(
    name="dash-cognito-auth",
    description="Dash Cognito Auth",
    long_description=open("README.md", "rt", encoding="utf-8").read().strip(),
    long_description_content_type="text/markdown",
    author="Frank Spijkerman",
    author_email="frank@jeito.nl",
    url="https://github.com/fspijkerman/dash-cognito-auth",
    license="MIT",
    package="dash_cognito_auth",
    packages=["dash_cognito_auth"],
    install_requires=[
        "dash>=0.41.0",
        "dash-core-components>=0.46.0",
        "dash-html-components>=0.15.0",
        "Flask>=1.0.2",
        "Flask-Dance>=1.2.0",
        "six>=1.11.0",
    ],
    python_requires=">=3.10",
    setup_requires=["pytest-runner", "setuptools_scm"],
    tests_require=[
        "pytest",
        "requests",
        "beautifulsoup4",
        "python-dotenv",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    use_scm_version=True,
    zip_safe=False,
)
