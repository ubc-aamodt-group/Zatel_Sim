source scenes.sh

declare -A scenes=()

function populate_config {
	sed -e "s/<<scene_name>>/$1/g" \
		-e "s/<<scene_number>>/$2/g" \
		-e "s/<<heatmap_path>>/$3/g" \
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
	populate_config "\"${scene}\"" "${scenes[$scene]}"
	python3.11 src/main.py
	cp "GEN_HEATMAPS/data/heatmap.ppm" "heatmaps/512x512_2spp/${scenes[$scene]}.ppm"
done

pyenv deactivate pvenv
