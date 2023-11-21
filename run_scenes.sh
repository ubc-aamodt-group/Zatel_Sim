source scenes.sh

declare -A scenes=()

function populate_config {
	sed -e "s|<<output>>|$1|g" \
		-e "s|<<uid>>|$2|g" \
		-e "s|<<scene_name>>|$3|g" \
		-e "s|<<scene_number>>|$4|g" \
		-e "s|<<heatmap_path>>|$5|g" \
		-e "s|<<downscale>>|$6|g" \
		-e "s|<<const_perc>>|$7|g" \
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
	mkdir -p "outputs/512x512_2spp/${scene}/predictor_outputs/"

	for p in {10..90..10}
	do
		heatmap_path="/home/ggc/ray_tracing/Predictor/heatmaps/512x512_2spp/${scenes[$scene]}.ppm"
		out_dir="outputs/512x512_2spp/${scene}/p${p}"
		mkdir -p "${out_dir}"

		populate_config \
			"\"outputs/512x512_2spp/${scene}/${p}.json\"" \
			"\"${out_dir}\"" \
			"\"${scene}\"" \
			"${scenes[$scene]}" \
			"\"${heatmap_path}\"" \
			"false" \
			"0.${p}"

		python3.11 src/main.py > "outputs/512x512_2spp/${scene}/predictor_outputs/${p}.txt" 2>&1 &
		sleep 480
	done
done

pyenv deactivate pvenv
