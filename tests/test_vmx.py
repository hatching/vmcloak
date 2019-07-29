import re
import os
import logging
import argparse
import subprocess
import copy as _copy
from argparse import Action
import IPython

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
OPTIONAL = '?'

class CommandError(Exception):
    pass

class VMWareError(Exception):
    pass

def _ensure_value(obj, name, value):
    if getattr(obj, name, None) is None:
        setattr(obj, name, value)
    return getattr(obj, name)

class _DictAction(Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        if nargs == 0:
            raise ValueError('nargs for append actions must be > 0; if arg '
                             'strings are not supplying the value to append, '
                             'the append const action may be more appropriate')
        if const is not None and nargs != OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(_DictAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        dict_name = _copy.copy(_ensure_value(namespace, self.dest, {}))
        for k, v in zip(values[0::2], values[1::2]):
            dict_name[k] = v
        setattr(namespace, self.dest, dict_name)

class VMX(object):
    def __init__(self, vmx_path):
        self.vmx_path = vmx_path
        self.vmrun = "/usr/bin/vmrun"

    def vmx_parse(self):
        vminfo = dict()
        if not self.vmx_path.endswith(".vmx"):
            raise VMWareError("Wrong configuration: vm path not "
                                "ending witht .vmx: %s" % self.vmx_path)

        if not os.path.exists(self.vmx_path):
            raise VMWareError("VMX file %s not found" % self.vmx_path)

        with open(self.vmx_path, 'r') as f:
            content = f.readlines()

        for line in content:
            match = re.search(r'(?P<key>.*)\s=\s(?P<value>.*)', line.rstrip())
            if match:
                key = match.group('key')
                value = match.group('value')
                vminfo[key] = value
        return vminfo

    def _call(self, *args, **kwargs):
        cmd = list(args)

        for k, v in kwargs.items():
            if v is None or v is True:
                cmd += ["--" + k]
            else:
                cmd += ["--" + k.rstrip("_"), str(v)]

        try:
            log.debug("Running command: %s", cmd)
            ret = subprocess.check_output(cmd)
        except Exception as e:
            log.error("[-] Error running command: %s" % e)
            raise CommandError

        return ret.strip()

    def isrunning(self):
        """ Check to see if the VM is running or not """
        vm_list = self._call(self.vmrun, 'list')
        instances = re.findall(r'Total running VMs:\s(\d+)', vm_list)
        running = False
        #import ipdb; ipdb.set_trace()
        if len(instances):
            if int(instances[0]) > 0:
                vm_list = vm_list.splitlines()[1:]
                for vm in vm_list:
                    if os.path.basename(vm) == os.path.basename(self.vmx_path):
                        running = True
        return running


    def exists(self, keyword, value=None):
        """ check the existence of a keyword in VMX config file """
        found = False
        line_num = 0
        pattern = re.compile(r'(?P<keyword>.*)\s=\s"(?P<value>.*)"')
        if keyword:
            try:
                with open(self.vmx_path, 'r+') as f:
                    content = f.readlines()
                    for i, line in enumerate(content):
                        # pass shebang
                        if line.startswith('#!'):
                            continue
                        result = re.match(pattern, line.rstrip())
                        if result:
                            keyword_,value_ = result.group('keyword'), result.group('value')
                        if keyword == keyword_:
                            found = True
                            line_num = line
                            if value is None:
                                value = value_
                            break
            except IOError as e:
                log.error("I/O error: %s"%e)
        return found, line_num, value


    def readvar(self, name, var_type="runtimeConfig"):
        """ Reads a variable from the virtual machine state or
        runtime configuration as stored in the .vmx file"""
        if self.isrunning():
            return self._call(self.vmrun, 'readVariable', self.vmx_path, var_type, name)
        else:
            found, _, value = self.exists(name)
            if found:
                return value
            else:
                log.error("value not found")
                return None


    def modifyvm(self, keyword, value, remove=False):
        """On success returns True otherwise False"""
        try:
            with open(self.vmx_path, 'r+') as f:
                content = f.readlines()
                found, line, _ = self.exists(keyword, value)
                if found:
                    content[content.index(line)] = re.sub(r'"(.*)"', '\"%s\"' % value, line)
                if not found:
                    attribute = "{0} = \"{1}\"".format(keyword, value)
                    content.append(attribute)
                f.seek(0)
                f.truncate()
                f.write(''.join(content))
                return True
        except IOError as e:
            log.error("I/O error: %s"%e)
            return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="a simple parser for vmware vmx file")
    parser.add_argument("vmx_path", help="path to a valid vmx file")
    parser.add_argument("-w", "--writeVariable", dest="attribute", nargs="*", help="write a variable in vmx file", action=_DictAction)
    parser.add_argument("-r", "--readVariable", dest="vars", nargs="*", help="read a variable from vmx file", action="append")
    args = parser.parse_args()

    if args.vmx_path:
        vmx = VMX(args.vmx_path)
        vminfo = vmx.vmx_parse()
        if args.attribute:
            for key, value in args.attribute.items():
                try:
                    if vmx.modifyvm(key, value):
                        raise VMWareError
                except VMWareError as e:
                    log.error("error: %s"%e)
        elif args.vars:
            for var in args.vars:
                if len(var):
                    log.error("%s = %s" % (var, vmx.readvar(var[0])))
