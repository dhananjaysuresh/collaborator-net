'''
Created on Mar 14, 2016

@author: DJ
'''
from setuptools import setup

setup(
    name='collaborator.net',
    version='1.0',
    py_modules=['DB_Manager'],
    install_requires=[
        'click',
        'py2neo',
        'pymongo'
    ],
    entry_points={
         'console_scripts': [
            'collaborator = collaborator.DB_Manager:main',
    ],
    }
)