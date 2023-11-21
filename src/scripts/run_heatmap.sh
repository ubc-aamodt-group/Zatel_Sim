
source /opt/embree-3.12.2.x86_64.linux/embree-vars.sh
export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
cd /home/ggc/ray_tracing/RayTracingInVulkan//build/linux/bin
./RayTracer --width 512 --height 512 --samples 2 --scene 1 --show-heatmap --heatmap-scale 1.0 --no-overlay --shadowrays 4 --shader-type 2
cp heatmap.ppm /home/ggc/ray_tracing/Predictor/GEN_HEATMAPS/data/
    