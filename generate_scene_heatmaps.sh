source scenes.sh

declare -A scenes=()

SHADERS=("path-tracer" "shadow" "ambient-occlusion")

function populate_config {
	sed -e "s|<<output>>|$1|g" \
		-e "s|<<uid>>|$2|g" \
		-e "s|<<scene_name>>|$3|g" \
		-e "s|<<scene_number>>|$4|g" \
		-e "s|<<shader_type>>|$5|g" \
		-e "s|<<shadow_rays>>|$6|g" \
		-e "s|<<heatmap_path>>|$7|g" \
		-e "s|<<downscale>>|$8|g" \
		-e "s|<<const_perc>>|$9|g" \
		config_template.toml > config.toml
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
pyenv activate pvenv

for scene in "${!scenes[@]}"; do 
	for shader in "${SHADERS[@]}"
	do
		num_rays=2
		if [ $shader == "ambient-occlusion" ]
		then
			num_rays=4
		fi

		populate_config \
			"\"out.json\"" \
			"\"GEN_HEATMAPS\"" \
			"\"${scene}\"" \
			"${scenes[$scene]}" \
			"\"${shader}\"" \
			"${num_rays}" \
			"\"\"" \
			"false" \
			"0.1"

		python3.11 src/main.py
		cp "GEN_HEATMAPS/data/heatmap.ppm" "heatmaps/512x512_2spp/${shader}/${scenes[$scene]}.ppm"
	done
done

pyenv deactivate pvenv
