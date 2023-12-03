#!/bin/bash

declare -A scenes=()

source "$(dirname "$0")/header.sh"

ARGS=($@)

OUT_PPM="ppms"
OUT_AERIAL="aerial"
OUT_STATS="stats"

PIDS=()

trap "" SIGABRT

function get_args {
	for arg in "${ARGS[@]}"
	do
		scene=(${arg//=/ })
		echo "${scene[0]}"
		echo "${scene[1]}"
		scenes["${scene[0]}"]="${scene[1]}"
	done
}

function setup_env {
	source ~/.bashrc > /dev/null &&
	source "${EMBREE_VARS}" &&

	mkdir -p $OUT_DIR &&
	mkdir -p $OUT_DIR/$OUT_STATS &&
	mkdir -p $OUT_DIR/$OUT_PPM &&
	mkdir -p $OUT_DIR/$OUT_AERIAL &&

	export CPATH="/usr/lib/gcc/x86_64-linux-gnu/9/include/" &&
	cd "${GPGPUSIM_DIR}" &&
	export VK_ICD_FILENAMES=${ICD_FILENAMES} &&
	source setup_environment &&
	make -j &&
	cd "${RAY_TRACER_DIR}/build/linux/bin" ;
}

# $1 for scene name
# $2 for scene number
function execute_scene {
	mkdir -p "$OUT_DIR/$OUT_STATS/$1"

	local args="--width ${WIDTH} --height ${HEIGHT} --scene $2 --samples ${SAMPLES}"

	for (( i=0; i<$NUM_CHUNKS; i++ )); do
		for (( k=0; k<$ITER_NUM; k++ )); do

			local out_name_path="$OUT_DIR/$OUT_STATS/out_chunks_${NUM_CHUNKS}_${i}_${k}_path.txt"
			echo "executed a ray tracing program $1 with $NUM_CHUNKS chunks, index: $i" &&

			local coordinates_path="$COORDINATES_DIR/chunk_${i}_${k}.coords"
			cp gpgpusim.config_sample gpgpusim.config &&
			echo "-selected_coordinates $coordinates_path" >> gpgpusim.config &&

			./RayTracer $args --shader-type ${SHADER_TYPE} --shadowrays ${SHADOW_RAYS} > $out_name_path 2>&1 &
			PIDS+=($!)
			sleep 200

		done
	done
}

function move_info {
	for file in *.ppm; do
		[ -f "$file" ] || break
		mv "$file" $OUT_DIR/$OUT_PPM/ || true
	done

	for file in *.log.gz; do
		[ -f "$file" ] || break
		mv "$file" $OUT_DIR/$OUT_AERIAL/ || true
	done
}

function main {
	get_args && setup_env &&

	for scene in "${!scenes[@]}"; do 
		execute_scene ${scene} ${scenes[$scene]}
		# sleep 8
	done

	for pid in "${PIDS[@]}"; do
		echo "$pid"
		wait $pid
		echo "waited!"
	done

	move_info
}

main
