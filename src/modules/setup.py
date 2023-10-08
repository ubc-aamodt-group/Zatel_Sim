import subprocess

import env
from modules.parse_args import parse_toml
from modules.helper_methods import dprint


def create_dirs():
    """
    Creating necessary directories
    """
    subprocess.run(["mkdir", "-p", "data"])
    subprocess.run(["mkdir", "-p", "data/coordinates"])
    subprocess.run(["mkdir", "-p", "data/tracer_out"])

    if env.configs.debug:
        subprocess.run(["mkdir", "-p", "data/debug"])

    dprint(env.plvl.info, "Created necessary directories")


def setup():
    parse_toml()
    create_dirs()
    dprint(env.plvl.info, "Setup done")
