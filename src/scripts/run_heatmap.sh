
source /opt/embree-3.12.2.x86_64.linux/embree-vars.sh
export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
cd /home/ggc/ray_tracing/RayTracingInVulkan//build/linux/bin
./RayTracer --width 512 --height 512 --samples 2 --scene 18 --show-heatmap --heatmap-scale 0.5 --no-overlay --shadowrays 2 --shader-type 0
cp heatmap.ppm /home/ggc/ray_tracing/Predictor/data/
    