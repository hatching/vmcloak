#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer - Hugo Genesse.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from json import loads


class Hide(Object):

    def __init__(a):

        self.a = a

    def load_json(file_name):
    """ Takes a JSON file and returns the content in a dictionnary."""
        file_object = open(file_name, "r")
        file_content = file_object.read()
        return loads(file_content)

    def modify_registry(key):
    """ Takes a key dictionnary and applies the required reg command to modify the Windows Registry."""
        command = "reg {0} {1} /v {2} /t {3} /d {4}".format(
            
                key["modification_type"],
                key["location"],
                key["value"],
                key["type"],
                key["data"])

        if !self.a.execute(command)

            print "Invalid operation for the following key : {}".format(key["value"])

    def modify_directory(directory):
    """ Takes a directory dictionnary and applies the required command to create or remove a directory. Uses the Agent directory commands."""
        mod_type = directory["modifcation_type"]

        if mod_type == "remove"

            self.a.remove(directory["path"])

        elif mod_type == "create"

            raise
