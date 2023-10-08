import os
import math
import subprocess

import env
from modules.helper_methods import dprint


def downscale_gpuconfig():
    c = open(env.configs.gpgpusim_config, 'r')
    lines = c.readlines()
    c.close()

    values = []

    for line in lines:
        for param in env.configs.shared_parameters:
            if line.startswith(f"-{param} "):
                v = int(line.split(' ')[1])
                values.append(v)

    gcd = math.gcd(*values)
    
    p = open(env.configs.downscaled_gpusimconfig, 'w')

    for line in lines:
        line_to_write = line
        for param in env.configs.shared_parameters:
            if line.startswith(f"-{param} "):
                val = int(line.split(' ')[1]) / gcd
                if env.configs.debug:
                    new_line = f"-{param} {int(val)} # MODIFIED\n"
                else:
                    new_line = f"-{param} {int(val)}\n"
                line_to_write = new_line

        p.write(line_to_write)

    p.close()

    subprocess.run(["cp", f"{os.path.join('data', 'gpgpusim.config_p')}", f"{os.path.join(env.configs.tools_tracer, 'build', 'linux', 'bin', 'gpgpusim.config_sample')}"])

    env.configs.num_chunks = gcd
    env.change_configs(env.configs)

    dprint(env.plvl.info, f"Downscaled each selected parameter of gpgpusim config by {gcd}")
