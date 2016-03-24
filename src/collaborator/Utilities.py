'''
Created on Mar 17, 2016

@author: DJ
'''
from click import echo

def print_dictionary(d):
    echo(d)

def print_attribute_list(a):
    echo("\tName,\tSkill\tLevel")
    i = 0
    for x in a:
        echo("{0}\t{1}\t{2}".format(i, x['name'], x['skill'], x['level']))
        i = i+1

def print_organization_list(a):
    echo("\tName")
    i = 0
    for x in a:
        echo("{0}\t{1}".format(i, x['name']))
        i = i+1