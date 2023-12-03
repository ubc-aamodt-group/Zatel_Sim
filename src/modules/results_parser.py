from functools import reduce
import env
import re


def sum_metric(metric, infos, k):
    e = infos[0][metric]
    if isinstance(e, str):
        return e
    elif isinstance(e, list):
        values = [i[metric] for i in infos]
        sums = reduce(lambda a, b: [a[i] + b[i] for i in range(len(a))], values)
        return list(sums)
    else:
        values = [i[metric] for i in infos]
        v = sum(values)
        return v


def avg_metric(metric, infos, k):
    e = infos[0][metric]
    if isinstance(e, str):
        return e
    elif isinstance(e, list):
        values = [i[metric] for i in infos]
        sums = reduce(lambda a, b: [a[i] + b[i] for i in range(len(a))], values)
        return list(map(lambda v: v / k, sums))
    else:
        values = [i[metric] for i in infos]
        v = sum(values)
        return v / k


def harmonic_avg_metric(metric, infos, k):
    e = infos[0][metric]
    if isinstance(e, str):
        return e
    elif isinstance(e, list):
        values = [i[metric] for i in infos]
        sums = reduce(lambda a, b: [a[i] + b[i] for i in range(len(a))], values)
        return list(map(lambda v: v / k, sums))
    else:
        values = [0 if i[metric] == 0 else 1.0/i[metric] for i in infos]
        v = sum(values)
        return 0 if v == 0 else k / v


def parse_file(config, path, chunk_i):
    output_info = {
        "config": config,
        "bwutil_sum": 0,
        "bwutil_count": 0,
        "dram_eff_sum": 0,
        "dram_eff_count": 0
    }

    visited_read_miss_rate = False
    visited_overall_miss_rate = False

    with open(path) as file:
        while True:
            line = file.readline()
            if not line:
                break

            line = line.strip()

            if "gpu_ipc" in line:
                nums = re.findall(r'\d+\.\d+', line)
                output_info["gpu_ipc"] = float(nums[0])

            elif "gpu_sim_cycle" in line:
                nums = re.findall(r'\d+', line)
                output_info["gpu_sim_cycle"] = int(nums[0]) / env.configs.perc_per_chunk[chunk_i]

            elif "rt_avg_nodes_per_ray" in line:
                nums = re.findall(r'\d+', line)
                output_info["rt_avg_nodes_per_ray"] = int(nums[0])

            elif "L0C_total_cache_misses" in line:
                nums = re.findall(r'\d+', line)
                output_info["L0C_total_cache_misses"] = int(nums[1])

            elif "L0C_total_cache_accesses" in line:
                nums = re.findall(r'\d+', line)
                output_info["L0C_total_cache_accesses"] = int(nums[1])

            elif "L1D_total_cache_miss_rate" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["L1D_total_cache_miss_rate"] = float(nums[0])

            elif "L2_total_cache_miss_rate" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["L2_total_cache_miss_rate"] = float(nums[0])

            elif "bwutil" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["bwutil_sum"] += float(nums[0])
                output_info["bwutil_count"] += 1

            elif "dram_eff=" in line:
                nums = re.findall(r'\d*\.\d+', line.split(' ')[1])
                output_info["dram_eff_sum"] += float(nums[0])
                output_info["dram_eff_count"] += 1

            elif "rt_avg_warp_occupancy" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_warp_occupancy"] = float(nums[0])

            elif "rt_avg_efficiency" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_efficiency"] = float(nums[0])

            elif "rt_avg_performance" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_performance"] = float(nums[0])

            elif "rt_avg_op_intensity" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_op_intensity"] = float(nums[0])

            elif "rt_avg_warp_latency" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_warp_latency"] = float(nums[0])

            elif "rt_avg_thread_latency" in line:
                nums = re.findall(r'\d*\.\d+', line)
                output_info["rt_avg_thread_latency"] = float(nums[0])

            elif "Warp Occupancy Distribution" in line:
                warp_nums = file.readline().strip()
                warps = re.findall(r'W\d\d?:\d+', warp_nums)
                output_info["warp_occupancy_distribution"] = [int(warp.split(':')[1]) for warp in warps]

            elif "gpgpu_n_rt_mem" in line:
                mems = file.readline().strip()
                output_info["gpgpu_n_rt_mem"] = [int(mem) for mem in mems.split()]

            elif "Stats for Kernel 0 Classification" in line:
                _ = file.readline()
                _ = file.readline()
                arr_info = file.readline().strip()
                elements = arr_info.split()
                elements.pop()
                elements.pop(0)
                output_info["stats_kernel_op_classification"] = [int(element) for element in elements]

            elif "rt_read_miss_rate" in line:
                nums = re.findall(r'\d*\.\d+', line)
                if visited_read_miss_rate:
                    output_info["rt_l2_read_miss_rate"] = float(nums[0])
                else:
                    output_info["rt_l1_read_miss_rate"] = float(nums[0])

                visited_read_miss_rate = True

            elif "rt_overall_miss_rate" in line:
                nums = re.findall(r'\d*\.\d+', line)
                if visited_overall_miss_rate:
                    output_info["rt_l2_overall_miss_rate"] = float(nums[0])
                else:
                    output_info["rt_l1_overall_miss_rate"] = float(nums[0])

                visited_overall_miss_rate = True

            elif "gpgpu_simulation_time" in line:
                nums = re.findall(r'\d+ sec\)$', line)
                output_info["running_time"] = int(nums[0][:-5])

            else:
                pass

    if len(output_info) < 6:
        return None

    output_info['dram_eff'] = output_info['dram_eff_sum'] / output_info['dram_eff_count']
    output_info['bwutil'] = output_info['bwutil_sum'] / output_info['bwutil_count']

    return output_info


def parse_file_iterations(chunk_i):
    config = "path"
    output_infos = []
    out = {}

    for c in range(env.configs.iterations):
        path = f"{env.configs.uid}/data/tracer_out/stats/out_chunks_{env.configs.num_chunks}_{chunk_i}_{c}_{config}.txt"
        output_info = parse_file(config, path, chunk_i)
        if output_info is not None:
            output_infos.append(output_info)

    for metric in output_infos[0]:
        out[metric] = avg_metric(metric,
                                 output_infos,
                                 len(output_infos))

    return out

