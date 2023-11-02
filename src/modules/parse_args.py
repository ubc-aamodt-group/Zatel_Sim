import tomllib

import env
from env import Configs, change_configs
from modules.helper_methods import dprint


def parse_toml():
    """
    Parsing the config.toml file into Configs dataclass
    """
    conf = {}
    with open('config.toml', 'rb') as f:
        conf = tomllib.load(f)

    new_configs = Configs(
        conf['output'],
        conf['uid'],

        conf['tools']['path'],
        conf['tools']['tracer'],
        conf['tools']['gpgpusim'],
        conf['tools']['embree_vars'],
        conf['tools']['nvidia_vk_icd_filenames'],
        conf['tools']['lavapipe_vk_icd_filenames'],

        conf['workload']['width'],
        conf['workload']['height'],
        conf['workload']['samples'],
        conf['workload']['scene_name'],
        conf['workload']['scene_number'],
        conf['workload']['shader_type'],
        conf['workload']['shadow_rays'],

        f"{conf['uid']}/data/heatmap.ppm",
        conf['heatmap']['scale'],
        conf['heatmap']['clusters'],
        conf['heatmap']['max_iter'],
        conf['heatmap']['epsilon'],

        conf['model']['gpuconfig'],
        f"{conf['uid']}/data/gpgpusim.config_p",
        conf['model']['section_width'],
        conf['model']['section_height'],
        conf['model']['iterations'],
        conf['model']['enable_edges'],
        conf['model']['all_pixels_in_chunks'],
        conf['model']['const_percentage'],
        conf['model']['distribution'],
        conf['model']['num_pixels_scale'],
        conf['model']['min_trace_perc'],
        conf['model']['shared_parameters'],
        conf['model']['chunks_type'],
        conf['model']['debug'],
        conf['model']['metrics_to_collect'],

        0)

    change_configs(new_configs)

    dprint(env.plvl.info, "Parsed the config file")
