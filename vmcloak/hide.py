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
        mod_type = key["mod_type"].split("_")
        if mod_type[0] == "add":
            command = "reg {0} {1} /v {2} /t {3} /d {4} /f".format(
                    mod_type[0],
                    key["location"],
                    key["value"],
                    key["datatype"],
                    key["data"])
        elif mod_type[0].find("del") >= 0:
            command = "reg delete {} /f".format(key["location"])

        # command = "{}".format(command)
        print command
        response = self.a.execute(command)
        print response.content

        #    print "Invalid operation for the following key : {}".format(
        # key["value"])

    def modify_directory(self, directory):
        """ Takes a directory dictionnary,
        Applies the required command to create or remove a directory.
        Uses the Agent directory commands."""
        mod_type = directory["mod_type"].split("_")
        print mod_type[0]
        if mod_type[0] == "rm":
            print "Removing directory : %s" % directory["dirpath"]
            self.a.remove(directory["dirpath"])

        elif mod_type[0] == "mv":

            self.a.rename(directory["dirpath"])

        elif mod_type[0] == "add":

            print "Adding directory %s." % directory["dirpath"]
            self.a.mkdir(directory["dirpath"])

        else:
            print "Not a valid option."

    def upload_file(self, filepath, contents):
        """Wrapper to upload a file."""
        self.a.upload(filepath, contents)
