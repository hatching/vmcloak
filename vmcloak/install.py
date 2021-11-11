# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
import logging
import time

import vmcloak.dependencies
from vmcloak.agent import Agent
from vmcloak.exceptions import DependencyError
from vmcloak.misc import wait_for_agent
from vmcloak.ostype import get_os
from vmcloak.repository import Session, Image

log = logging.getLogger(__name__)

class InstallError(Exception):
    pass

_recipes = {
    "win10x64": ["ie11", "dotnet:4.7.2", "java:7u80", "vcredist:2013",
                 "vcredist:2019", "edge", "carootcert", "adobepdf",
                 "wallpaper", "optimizeos", "disableservices"],
    "win7x64": ["ie11", "dotnet:4.7.2", "java:7u80", "vcredist:2013",
                 "vcredist:2019", "carootcert", "adobepdf", "wallpaper",
                "optimizeos", "disableservices"]
}

def find_recipe(osversion):
    os_recipe = _recipes.get(osversion)
    if not os_recipe:
        raise InstallError(
            f"No recommended software/settings available for '{osversion}'"
        )

    return os_recipe

def _split_dep_version(dep):
    if ":" not in dep:
        return dep, None

    dependencency, version = dep.split(":", 1)
    return dependencency.strip(), version.strip()

def parse_dependencies_list(dependencies):
    """Read all key=value settings and dependencies, and versions from the
    dependencies string list. Return a list of (dep,version) entries
    and a settings dictionary."""
    deps_versions = []
    settings = {}
    settings_versions = []
    for dependency in dependencies:
        if "." in dependency and "=" in dependency:
            key, value = dependency.split("=", 1)
            # Store the value if it is a version. We do this so we can later
            # merge these with the deps:versions given in another format.
            if key.endswith(".version"):
                depname, _ = key.split(".", 1)
                settings_versions.append((depname.strip(), value.strip()))
            else:
                settings[key.strip()] = value.strip()
        else:
            deps_versions.append(_split_dep_version(dependency))

    # Replace dep,None with the version for the deps given as a settings
    # string instead of dep:version format.
    for dep, version in settings_versions:
        try:
            i = deps_versions.index((dep, None))
        except ValueError:
            continue

        deps_versions.pop(i)
        deps_versions.insert(i, (dep, version))

    return deps_versions, settings

def _raise_for_non_existing(deps_versions):
    non_existing = set()

    for dep, _ in deps_versions:
        if dep not in vmcloak.dependencies.names:
            non_existing.add(dep)

    if non_existing:
        raise InstallError(
            f"One or more specified dependencies are not supported/unknown: "
            f"{', '.join(non_existing)}"
        )

def _wait_for_agent(agent, timeout=1200):
    # wrap func just to change default argument.
    wait_for_agent(agent, timeout=timeout)

class _Installable:

    def __init__(self, dependency_class, installer, class_args):
        self.dependency_class = dependency_class
        self.installer = installer
        self.class_args = class_args

        self.did_install = False
        self.dependency = None

    @property
    def name(self):
        return self.dependency_class.name

    def do_install(self):
        try:
            self.dependency = self.dependency_class(
               installer=self.installer, **self.class_args
            )
            self.dependency.run()
        except DependencyError as e:
            raise InstallError(
                f"Dependency '{self.dependency_class.name}' "
                f"raised an error: {e}"
            )
        # Catch base error of install until we catch/wrap exceptions in agent
        # and all other things used in run() calls.
        except Exception as e:
            log.exception(e)
            raise InstallError(
                f"Unexpected failure during install of "
                f"'{self.dependency_class.name}'. {e}"
            )

        self.did_install = True
        versions = self.installer.installed.setdefault(
            self.dependency.name, []
        )
        if self.dependency.version:
            versions.append(self.dependency.version)

class DependencyInstaller:

    def __init__(self, image, dependencies, attrs={}):
        self.image = image
        self.dependency_list = dependencies
        self.attrs = attrs

        deps_versions, settings = parse_dependencies_list(dependencies)
        self.install_queue = deps_versions
        self.deps_settings = settings
        _raise_for_non_existing(deps_versions)

        self._depending_deps = {}

        self.installed = {}
        self.platform = image.platform
        self.machinery = self.platform.VM(image.name)
        self.os_helper = get_os(image.osversion)
        self.agent = Agent(image.ipaddr, image.port)
        self._prepared = False
        self._no_machine_start = False

    def _find_in_queue(self, dep):
        for item in self.install_queue:
            if item[0] == dep:
                return item[0], item[1], self.install_queue.index(item)

        return None, None, None

    def _discover_subdependencies(self, dependency_class):
        depends_on = dependency_class.get_dependencies(self.image)
        if not depends_on:
            return

        for dep_dependency in depends_on:
            name, version = _split_dep_version(dep_dependency)

            self._depending_deps.setdefault(
                dependency_class.name, []
            ).append((name, version))

            dep_dep_class = vmcloak.dependencies.names[name]
            self._discover_subdependencies(dep_dep_class)

            # Check if the dependency of the dependency was already given
            # as something to be installed. Warn user that their version
            # might not be used as another is needed.
            chosen_dep, chosen_version, pos = self._find_in_queue(name)
            if not chosen_dep:
                continue

            # Skip the conflicting version check if this dependency can
            # have multiple versions installed.
            if dep_dep_class.multiversion:
                continue

            # Remove dep from install queue as it is now part of the
            # dep dependencies dict. These will be installed first.
            self.install_queue.pop(pos)
            if chosen_version and version != chosen_version:
                log.error(
                    f"Dependency '{dependency_class.name}' has its own"
                    f" dependency: '{name}' with version: '{version}'. "
                    f"Overwriting chosen version: {chosen_version}"
                )
            elif version:
                log.error(
                    f"Dependency '{dependency_class.name}' has its own "
                    f"dependency: '{name}' with version: '{version}'. "
                    f"Using version '{version}' for '{name}'"
                )

    def _populate_dep_dependencies(self):
        for dep, version in self.install_queue[:]:
            dep_installer = vmcloak.dependencies.names[dep]

            self._discover_subdependencies(dep_installer)

    def do_reboot(self):
        try:
            # Ignore timeout/socket etc errors as machine will
            # shut down.
            self.agent.reboot()
            # Wait a bit, so machine can actually shut down.
            time.sleep(10)
        except (IOError, OSError):
            pass

        # Long timeout as a boot may take long after windows/system updates.
        _wait_for_agent(self.agent, timeout=1200)

    def prepare(self, timeout=1200, no_machine_start=False):
        """Compile list of all dependencies to install and starts a vm for the
        image to install them on. Returns when the vm has booted and its agent
        is reachable."""
        log.debug("Find all dependencies of the chosen dependencies")
        self._populate_dep_dependencies()

        if not no_machine_start:
            self.platform.start_image_vm(self.image, self.attrs)
        else:
            self._no_machine_start = no_machine_start

        _wait_for_agent(self.agent, timeout=timeout)
        self._prepared = True

    def _is_installed(self, depname, version=None):
        # Dep with version installed on previous install run?
        if self.image.dependency_installed(depname, version):
            return True

        # Was this dep with version installed during current install run?
        try:
            installed_versions = self.installed[depname]
        except KeyError:
            return False

        if version and version not in installed_versions:
            return False

        return True

    def _do_install(self, depname, depversion, skip_installed=True):
        # Skip if dependency already installed on image a
        # previous run or during the current run.
        log.info(
            f"Installing dependency: {depname} "
            f"version={depversion or 'no version/default'}"
        )
        if skip_installed and self._is_installed(depname, depversion):
            log.debug(
                f"Dependency: {depname} version={depversion} already satistied "
                f"during this or previous install run"
            )
            return None

        installed_dep_deps = False
        # If the current dependency has its own dependencies, install
        # those first.
        dep_deps = self._depending_deps.get(depname, [])
        if dep_deps:
            log.debug(
                f"'{depname}' has several dependencies of its own. "
                f"Installing these first: "
                f"{', '.join(f'{k}:{v}' for k,v in dep_deps)}"
            )
        for dep_dep, version in dep_deps:
            installable = self._do_install(dep_dep, version)
            # Stop installing further sub dependencies for this dependency.
            # We already know it cannot be installed of a failed sub dependency
            if installable and not installable.did_install:
                raise InstallError(
                    f"'{depname}' dependency '{dep_dep}' {version or ''} did "
                    f"not succeed."
                )
            installed_dep_deps = True

        if installed_dep_deps:
            # Reboot the VM if any dep deps were installed as we
            # expect most dependencies to be related to KB installs.
            log.info("Rebooting vm for dependencies to take effect")
            self.do_reboot()

        installable = _Installable(
            vmcloak.dependencies.names[depname],
            self,
            class_args=dict(h=self.os_helper, m=self.machinery,
                            a=self.agent,
                            i=self.image,
                            version=depversion,
                            settings=self.deps_settings)
        )
        installable.do_install()

        return installable

    def install_all(self, skip_installed=True):
        """Install all dependencies and subdependencies. Returns True or False
        to indicate if all were successfully installed."""
        dep_count = 0
        has_fails = False
        for dep, dep_version in self.install_queue:
            dep_count += 1
            try:
                installable = self._do_install(
                    dep, dep_version, skip_installed
                )
            except InstallError as e:
                log.error(
                    f"Failed to install dependency '{dep}'. {e}"
                )
                has_fails = True
                continue

            # Do a reboot is a dependency/change requires it. But only if
            # it is not the last one. If it is the last one, normal shutdown
            # will suffice.
            if installable and installable.dependency_class.must_reboot and \
                    len(self.install_queue) != dep_count:
                log.debug(
                    f"Rebooting machine as dependency '{dep}' requires it."
                )
                self.do_reboot()

        log.info("No more dependencies to install")

        return not has_fails

    def _update_installed_image(self):
        deps_versions = set()
        for depname, versions in self.installed.items():
            if not versions:
                deps_versions.add((depname, None))
            else:
                for version in versions:
                    deps_versions.add((depname, version))

        ses = Session()
        try:
            image = ses.query(Image).filter_by(name=self.image.name).first()
            image.add_installed_versions(deps_versions)
            ses.commit()
        finally:
            ses.close()

    def finish(self, do_shutdown=True):
        """Update the repository image with the installed dependency names
        and version and shut down the vm."""
        if self.installed:
            self._update_installed_image()

        if not do_shutdown:
            return

        if self._no_machine_start:
            return

        log.debug("Shutting down vm")
        try:
            self.agent.shutdown()
        except (IOError, OSError) as e:
            log.error(f"Error sending shutdown command to agent. {e}")

        try:
            self.platform.wait_for_shutdown(self.image.name)
        except ValueError as e:
            log.error(f"Error while waiting for vm to shut down: {e}")

        self.platform.remove_vm_data(self.image.name)
