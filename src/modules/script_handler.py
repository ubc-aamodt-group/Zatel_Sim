import os
import subprocess

import env
from modules.helper_methods import dprint
from modules.helper_methods import shader_type_to_code


def setup_script_env():
    out_dir = os.path.join(os.getcwd(), "data/tracer_out/")
    coords_dir = os.path.join(os.getcwd(), "data/coordinates/")

    shader_type = shader_type_to_code()

    header = f"""NUM_CHUNKS={env.configs.num_chunks}
WIDTH=\"{env.configs.width}\"
HEIGHT=\"{env.configs.height}\"
SAMPLES=\"{env.configs.samples}\"
OUT_DIR=\"{out_dir}\"
ITER_NUM={env.configs.iterations}
COORDINATES_DIR=\"{coords_dir}\"
EMBREE_VARS=\"{env.configs.embree_vars}\"
GPGPUSIM_DIR=\"{env.configs.tools_gpgpusim}\"
RAY_TRACER_DIR=\"{env.configs.tools_tracer}\"
ICD_FILENAMES=\"{env.configs.lavapipe_vk_icd_filenames}\"
SHADER_TYPE=\"{shader_type}\"
SHADOW_RAYS={env.configs.shadow_rays}"""

    with open('src/scripts/header.sh', 'w') as f:
        f.write(header)


def run_tracer_script():
    """
    Run the script that launches Vulkan-Sim for each chunk with the generated coordinates
    """
    script_name = 'trace.sh'
    header_name = 'header.sh'

    subprocess.run(['cp',
                    os.path.join('src', 'scripts', 'RayTracing.rgen_heatmap_off'),
                    os.path.join(env.configs.tools_tracer, 'assets', 'shaders', 'RayTracing.rgen')])

    subprocess.run(['cp',
                    os.path.join('src', 'scripts', 'CMakeLists_offscreen.txt'),
                    os.path.join(env.configs.tools_tracer, 'CMakeLists.txt')])

    d = os.getcwd()

    os.chdir(env.configs.tools_tracer)
    subprocess.run(['bash', 'build_linux.sh'])

    os.chdir(d)

    subprocess.run(['cp', 
                    os.path.join('src', 'scripts', header_name),
                    os.path.join(env.configs.tools_tracer, 'build', 'linux', 'bin')])

    subprocess.run(['cp', 
                    os.path.join('src', 'scripts', script_name),
                    os.path.join(env.configs.tools_tracer, 'build', 'linux', 'bin')])

    subprocess.run(['bash',
                    os.path.join(env.configs.tools_tracer, 'build', 'linux', 'bin', script_name),
                    f'{env.configs.scene_name}={env.configs.scene_number}'])
