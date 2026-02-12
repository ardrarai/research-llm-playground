import itertools
from pipeline.orchestrator import run_pipeline, compare_runs
from utils.experiment_logger import log_single_run, log_comparison_run


def generate_config_grid(base_config, param_grid):
    """
    Creates all config combinations.
    """

    keys = param_grid.keys()
    values = param_grid.values()

    configs = []

    for combo in itertools.product(*values):
        new_config = base_config.__class__(**vars(base_config))
        for k, v in zip(keys, combo):
            setattr(new_config, k, v)
        configs.append(new_config)

    return configs


def run_single_sweep(configs, document_path, query, progress_callback=None):
    """
    Run many configs independently.
    """

    results = []

    for i, config in enumerate(configs):

        result = run_pipeline(config, document_path, query)
        log_single_run(config, result)

        results.append(result)

        if progress_callback:
            progress_callback(i + 1, len(configs))

    return results


def run_comparison_sweep(config_pairs, document_path, query, progress_callback=None):
    """
    Run many config comparisons.
    """

    analyses = []

    for i, (config_A, config_B) in enumerate(config_pairs):

        result_A = run_pipeline(config_A, document_path, query)
        result_B = run_pipeline(config_B, document_path, query)

        analysis = compare_runs(result_A, result_B)

        log_comparison_run(config_A, result_A, config_B, result_B, analysis)
        analyses.append(analysis)

        if progress_callback:
            progress_callback(i + 1, len(config_pairs))

    return analyses
