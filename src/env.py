from dataclasses import dataclass
from typing import Union


@dataclass
class PrintLevels:
    info:  str
    warn:  str
    error: str


@dataclass
class Configs:
    # general
    output: str

    # tools
    tools_path: str
    tools_tracer: str
    tools_gpgpusim: str
    embree_vars: str
    nvidia_vk_icd_filenames: str
    lavapipe_vk_icd_filenames: str

    # workload
    width: int
    height: int
    samples: int
    scene_name: str
    scene_number: str
    shader_type: str
    shadow_rays: int

    # heatmap
    heatmap: str
    heatmap_scale: float
    clusters: int
    max_iter: int
    epsilon: float

    # model
    gpgpusim_config: str
    downscaled_gpusimconfig: str
    section_width: int
    section_height: int
    iterations: int
    enable_edges: bool
    all_pixels_in_chunks: bool
    const_percentage: float
    distribution: Union[str, list[float]]
    num_pixels_scale: float
    min_trace_perc: float
    shared_parameters: str
    chunks_type: str
    debug: bool
    metrics_to_collect: list[str]

    # TBD
    num_chunks: int


plvl = PrintLevels(
    "INFO",
    "WARN",
    "ERROR")

configs = None


def change_configs(new_configs: Configs):
    global configs
    configs = new_configs
