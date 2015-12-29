#!/usr/bin/env python
# Copyright (C) 2014-2015 Jurriaan Bremer - Hugo Genesse.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from json import loads


class Hide(object):

    def __init__(self, a):

        self.a = a

    def load_json(self, file_name):
        """ Takes a JSON file and returns the content in a dictionnary."""
        file_object = open(file_name, "r")
        file_content = file_object.read()
        return loads(file_content)

    def modify_registry(self, key):
        """ Takes a key dictionnary and
        applies the required reg command to modify the Windows Registry."""
        command = "reg {0} {1} /v {2} /t {3} /d {4}".format(
                key["modification_type"].strip("_key"),
                key["location"],
                key["value"],
                key["type"],
                key["data"])

        self.a.execute(command)

        #    print "Invalid operation for the following key : {}".format(
        # key["value"])

    def modify_directory(self, directory):
        """ Takes a directory dictionnary,
        Applies the required command to create or remove a directory.
        Uses the Agent directory commands."""
        mod_type = directory["modifcation_type"]

        if mod_type == "remove":

            self.a.remove(directory["path"])

        elif mod_type == "rename":

            self.a.rename(directory["path"])

        elif mod_type == "create":

            print "Method not yet created."

    def upload_file(self, filepath, contents):
        """Wrapper to upload a file."""
        self.a.upload(filepath, contents)
