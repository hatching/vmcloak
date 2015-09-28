#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback
import zipfile

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    sys.exit("ERROR: Flask library is missing (`pip install flask`)")

app = Flask("agent")
state = {}

def json_error(error_code, message):
    r = jsonify(message=message, error_code=error_code)
    r.status_code = error_code
    return r

def json_exception(message):
    r = jsonify(message=message, error_code=500,
                traceback=traceback.format_exc())
    r.status_code = 500
    return r

def json_success(message, **kwargs):
    return jsonify(message=message, **kwargs)

@app.route("/")
def get_index():
    return json_success("Cuckoo Agent!")

@app.route("/status")
def get_status():
    return json_success("Analysis status",
                        status=state.get("status"),
                        description=state.get("description"))

@app.route("/status", methods=["POST"])
def put_status():
    if "status" not in request.form:
        return json_error("No status has been provided")

    state["status"] = request.form["status"]
    state["description"] = request.form.get("description")
    return json_success("Analysis status updated")

@app.route("/system")
def get_system():
    return json_success("System", system=platform.system())

@app.route("/environ")
def get_environ():
    return json_success("Environment variables", environ=dict(os.environ))

@app.route("/path")
def get_path():
    return json_success("Agent path", filepath=os.path.abspath(__file__))

@app.route("/mkdir", methods=["POST"])
def do_mkdir():
    if "dirpath" not in request.form:
        return json_error(400, "No dirpath has been provided")

    mode = int(request.form.get("mode", 0777))

    try:
        os.makedirs(request.form["dirpath"], mode=mode)
    except:
        return json_exception("Error creating directory")

    return json_success("Successfully created directory")

@app.route("/mktemp", methods=["GET", "POST"])
def do_mktemp():
    suffix = request.form.get("suffix", "")
    prefix = request.form.get("prefix", "tmp")
    dirpath = request.form.get("dirpath")

    fd, filepath = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dirpath)
    os.close(fd)

    return json_success("Successfully created temporary file",
                        filepath=filepath)

@app.route("/mkdtemp", methods=["GET", "POST"])
def do_mkdtemp():
    suffix = request.form.get("suffix", "")
    prefix = request.form.get("prefix", "tmp")
    dirpath = request.form.get("dirpath")

    dirpath = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dirpath)
    return json_success("Successfully created temporary directory",
                        dirpath=dirpath)

@app.route("/store", methods=["POST"])
def do_store():
    if "filepath" not in request.form:
        return json_error(400, "No filepath has been provided")

    if "file" not in request.files:
        return json_error(400, "No file has been provided")

    try:
        with open(request.form["filepath"], "wb") as f:
            f.write(request.files["file"].read())
    except:
        return json_exception("Error storing file")

    return json_success("Successfully stored file")

@app.route("/retrieve", methods=["POST"])
def do_retrieve():
    if "filepath" not in request.form:
        return json_error(400, "No filepath has been provided")

    return send_file(request.form["filepath"])

@app.route("/extract", methods=["POST"])
def do_extract():
    if "dirpath" not in request.form:
        return json_error(400, "No dirpath has been provided")

    if "zipfile" not in request.files:
        return json_error(400, "No zip file has been provided")

    try:
        with zipfile.ZipFile(request.files["zipfile"], "r") as archive:
            archive.extractall(request.form["dirpath"])
    except:
        return json_exception("Error extracting zip file")

    return json_success("Successfully extracted zip file")

@app.route("/remove", methods=["POST"])
def do_remove():
    if "path" not in request.form:
        return json_error(400, "No path has been provided")

    try:
        if os.path.isdir(request.form["path"]):
            # Mark all files as readable so they can be deleted.
            for dirpath, _, filenames in os.walk(request.form["path"]):
                for filename in filenames:
                    os.chmod(os.path.join(dirpath, filename), stat.S_IWRITE)

            shutil.rmtree(request.form["path"])
            message = "Successfully deleted directory"
        elif os.path.isfile(request.form["path"]):
            os.chmod(request.form["path"], stat.S_IWRITE)
            os.remove(request.form["path"])
            message = "Successfully deleted file"
    except:
        return json_exception("Error removing file or directory")

    return json_success(message)

@app.route("/execute", methods=["POST"])
def do_execute():
    if "command" not in request.form:
        return json_error(400, "No command has been provided")

    # Execute the command asynchronously? As a shell command?
    async = "async" in request.form
    shell = "shell" in request.form

    cwd = request.form.get("cwd")
    stdout = stderr = None

    try:
        if async:
            subprocess.Popen(request.form["command"], shell=shell, cwd=cwd)
        else:
            p = subprocess.Popen(request.form["command"], shell=shell, cwd=cwd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
    except:
        return json_exception("Error executing command")

    return json_success("Successfully executed command",
                        stdout=stdout, stderr=stderr)

@app.route("/kill")
def do_kill():
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if shutdown is None:
        return json_error(500, "Not running with the Werkzeug server")

    shutdown()
    return json_success("Quit the Cuckoo Agent")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default="0.0.0.0")
    parser.add_argument("port", nargs="?", default="8000")
    args = parser.parse_args()

    app.run(host=args.host, port=int(args.port))
