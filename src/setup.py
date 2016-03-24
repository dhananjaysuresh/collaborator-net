'''
Created on Mar 14, 2016

@author: DJ
'''
from setuptools import setup

setup(
    name='collaborator.net',
    version='0.1',
    py_modules=['Interface', 'DB_Manager'],
    install_requires=[
        'Click',
    ],
    entry_points={
         'console_scripts': [
            'collaborator = collaborator.DB_Manager:main',
    ],
    }
)