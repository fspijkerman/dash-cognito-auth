#!/usr/bin/env python

from setuptools import setup

setup(
    name="dash-cognito-auth",
    description="Dash Cognito Auth",
    long_description=open('README.md', 'rt').read().strip(),
    long_description_content_type='test/markdown',
    author="Frank Spijkerman", author_email='fspijkerman@gmail.com',
    url="https://github.com/fspijkerman/dash-cognito-auth",
    license='MIT',
    package='dash_cognito_auth',
    packages=['dash_cognito_auth'],
    install_requires=[
        'dash>=0.26.5',
        'dash-core-components>=0.28.3',
        'dash-html-components>=0.12.0',
        'Flask>=0.12.4',
        'Flask-Dance>=0.14.0',
        'six>=1.11.0',
    ],
    setup_requires=['pytest-runner', 'setuptools_scm'],
    tests_require=['pytest'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    use_scm_version=True,
    zip_safe=False,
)
