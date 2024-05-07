source scenes.sh

declare -A scenes=()

PIDS=()
# DISTS=("uniform" "temp-exp")
DISTS=("uniform")

function populate_config {
	all_pixels="false"
	if [ $8 == "1.1" ]; then
		all_pixels="true"
	fi

	sed -e "s|<<output>>|$1|g" \
		-e "s|<<uid>>|$2|g" \
		-e "s|<<scene_name>>|$3|g" \
		-e "s|<<scene_number>>|$4|g" \
		-e "s|<<shader_type>>|$5|g" \
		-e "s|<<shadow_rays>>|$6|g" \
		-e "s|<<heatmap_path>>|$7|g" \
		-e "s|<<const_perc>>|$8|g" \
		-e "s|<<dist>>|$9|g" \
		-e "s|<<all_pixels>>|${all_pixels}|g" \
		config_template_home.toml > config.toml
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
	for dist in "${DISTS[@]}"
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

		p=100
		# for p in {10..10..10}
		# do
			heatmap_path="/home/ggc/ray_tracing/Predictor/heatmaps/512x512_2spp/${shader}/${scenes[$scene_name]}.ppm"
			out_dir="outputs/512x512_2spp/${scene_name}/${dist}/p${p}"
			mkdir -p "${out_dir}"

			perc="${p}"
			if [ $perc == "100" ]
			then
				perc="1.1"
			else
				perc="0.0${p}"
			fi

			populate_config \
				"\"outputs/512x512_2spp/${scene_name}/${p}_${dist}.json\"" \
				"\"${out_dir}\"" \
				"\"${scene}\"" \
				"${scenes[$scene_name]}" \
				"\"${shader}\"" \
				"${num_rays}" \
				"\"${heatmap_path}\"" \
				"${perc}" \
				"\"${dist}\""

			python3.11 src/main.py > "outputs/512x512_2spp/${scene_name}/predictor_outputs/${p}_${dist}.txt" 2>&1 &
			PIDS+=($!)
			sleep 320
		# done
	done
done

pyenv deactivate pvenv

for pid in "${PIDS[@]}"; do
	echo "test $pid"
	wait $pid
	echo "waited for test!"
done

curl \
	-H 'Title: EXPERIMENTS DONE (MOBILE)' \
	-d 'Finished executing all the scenes' \
	ntfy.sh/eiAizI8HMMHAqFPyLBYvkTY3Y2y6e7dAg1s5H8BOKTw3XRqeBbC61
