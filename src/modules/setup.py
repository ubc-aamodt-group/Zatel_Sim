import subprocess

import env
from modules.parse_args import parse_toml
from modules.helper_methods import dprint


def create_dirs():
    """
    Creating necessary directories
    """
    subprocess.run(["mkdir", "-p", env.configs.uid])
    subprocess.run(["mkdir", "-p", f"{env.configs.uid}/data"])
    subprocess.run(["mkdir", "-p", f"{env.configs.uid}/data/coordinates"])
    subprocess.run(["mkdir", "-p", f"{env.configs.uid}/data/tracer_out"])

    if env.configs.debug:
        subprocess.run(["mkdir", "-p", f"{env.configs.uid}/data/debug"])

    dprint(env.plvl.info, "Created necessary directories")


def setup():
    parse_toml()
    create_dirs()
    dprint(env.plvl.info, "Setup done")
