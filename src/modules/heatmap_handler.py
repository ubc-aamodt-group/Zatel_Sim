import subprocess
import os
from dataclasses import dataclass
import numpy as np
import cv2
from numpy.typing import NDArray

import env
from modules.helper_methods import shader_type_to_code


@dataclass
class Heatmap:
    pixels: NDArray[np.uint8]
    labels: NDArray[np.uint8]
    centers: NDArray[np.uint8]
    shape: tuple[int, int]


def capture_heatmap():
    subprocess.run(['cp',
                    os.path.join('src', 'scripts', 'CMakeLists_gui.txt'),
                    os.path.join(env.configs.tools_tracer, 'CMakeLists.txt')])

    subprocess.run(['cp',
                    os.path.join('src', 'scripts', 'RayTracing.rgen_heatmap_on'),
                    os.path.join(env.configs.tools_tracer, 'assets', 'shaders', 'RayTracing.rgen')])

    d = os.getcwd()

    os.chdir(env.configs.tools_tracer)
    subprocess.run(['bash', 'build_linux.sh'])

    os.chdir(d)

    run_script = f"""
source {env.configs.embree_vars}
export VK_ICD_FILENAMES={env.configs.nvidia_vk_icd_filenames}
cd {env.configs.tools_tracer}/build/linux/bin
./RayTracer --width {env.configs.width} --height {env.configs.height} --samples {env.configs.samples} --scene {env.configs.scene_number} --show-heatmap --heatmap-scale 0.5 --no-overlay --shadowrays {env.configs.shadow_rays} --shader-type {shader_type_to_code()}
cp heatmap.ppm {d}/data/
    """

    with open('src/scripts/run_heatmap.sh', 'w') as f:
        f.write(run_script)

    subprocess.run(['bash', 'src/scripts/run_heatmap.sh'])


def get_simplified_heatmap_pixels(filename) -> Heatmap:
    img = cv2.imread(filename)

    pixels = img.reshape((-1, 3))
    pixels = np.float32(pixels)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, env.configs.max_iter, env.configs.epsilon)
    k = env.configs.clusters
    comp, labels, centers = cv2.kmeans(pixels, k, None, criteria, 40, 
                                       cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)

    # NOTE: swizzling from BGR (surface format) to RGB for PPM
    centers = np.flip(centers, 1)

    heatmap_info = Heatmap(centers[labels.flatten()],
                           labels.flatten(),
                           centers,
                           (img.shape[0], img.shape[1]))

    return heatmap_info
