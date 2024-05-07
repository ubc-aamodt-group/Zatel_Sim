import json

import env
from modules.results_parser import parse_file_iterations, avg_metric, sum_metric, harmonic_avg_metric


def merge_configs(configs):
    merged_config = {}

    n_chunks = env.configs.num_chunks

    out = {}
    output_infos = []

    for i in range(n_chunks):
        output_infos.append(configs[i])

    for metric in output_infos[0]:
        if metric == 'gpu_ipc':
            out[metric] = sum_metric(metric, output_infos, len(output_infos))
        else:
            out[metric] = avg_metric(metric, output_infos, len(output_infos))

    merged_config = out

    return merged_config


def fetch_results():
    n_chunks = env.configs.num_chunks

    configs = {i: parse_file_iterations(i) for i in range(n_chunks)}

    m_configs = merge_configs(configs)
    metrics = {key: m_configs[key] for key in env.configs.metrics_to_collect}

    with open(env.configs.output, 'w') as f:
        json.dump(metrics, f)
