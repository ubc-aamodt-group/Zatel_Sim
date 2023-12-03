#!/bin/bash

SCENES=($@)

declare -A scenes=()

PIDS=()
PERCS=(1 2 4 8 16)
CHUNK_TYPES=("fine-grained" "coarse-grained")

function populate_config {
	sed -e "s|<<output>>|$1|g" \
		-e "s|<<uid>>|$2|g" \
		-e "s|<<scene_name>>|$3|g" \
		-e "s|<<scene_number>>|$4|g" \
		-e "s|<<shader_type>>|$5|g" \
		-e "s|<<shadow_rays>>|$6|g" \
		-e "s|<<heatmap_path>>|$7|g" \
		-e "s|<<downscale_factor>>|$8|g" \
		-e "s|<<chunk_type>>|$9|g" \
		config_template_p2.toml > config.toml
}

function get_args {
	for arg in "${SCENES[@]}"
	do
		scene=(${arg//=/ })
		scenes["${scene[0]}"]="${scene[1]}"
	done
}

get_args

source ~/.bashrc
source /opt/embree-3.12.2.x86_64.linux/embree-vars.sh
pyenv activate pvenv

for scene_name in "${!scenes[@]}"; do
	for ct in "${CHUNK_TYPES[@]}"
	do
		scene_name_parts=(${scene_name//_/ })
		scene="${scene_name_parts[0]}"
		shader="${scene_name_parts[1]}"

		num_rays=2
		if [ $shader == "ambient-occlusion" ]
		then
			num_rays=4
		fi

		mkdir -p "outputs/512x512_2spp/${scene_name}/predictor_outputs/"

		for df in "${PERCS[@]}"
		do
			heatmap_path="/ggc/ray_tracing/Predictor/heatmaps/512x512_2spp/${shader}/${scenes[$scene_name]}.ppm"
			out_dir="outputs/512x512_2spp/${scene_name}/${ct}/f${df}"
			files_out="/out_files/512x512_2spp/${scene_name}/"
			mkdir -p "${files_out}"
			mkdir -p "${out_dir}"

			populate_config \
				"\"/out_files/512x512_2spp/${scene_name}/${df}_${ct}.json\"" \
				"\"${out_dir}\"" \
				"\"${scene}\"" \
				"${scenes[$scene_name]}" \
				"\"${shader}\"" \
				"${num_rays}" \
				"\"${heatmap_path}\"" \
				"${df}" \
				"\"${ct}\""

			python3.11 src/main.py > "outputs/512x512_2spp/${scene_name}/predictor_outputs/${df}_${ct}.txt" 2>&1 &
			PIDS+=($!)
			sleep 500
		done
	done
done

pyenv deactivate pvenv

for pid in "${PIDS[@]}"; do
	echo "test $pid"
	wait $pid
	echo "waited for test!"
done

# curl \
# 	-H 'Title: EXPERIMENTS DONE' \
# 	-d 'Finished executing all the scenes' \
# 	ntfy.sh/eiAizI8HMMHAqFPyLBYvkTY3Y2y6e7dAg1s5H8BOKTw3XRqeBbC61
