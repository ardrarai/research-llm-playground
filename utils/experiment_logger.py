import json
import os
from datetime import datetime

LOG_PATH = "data/experiments/experiment_log.json"


def _ensure_log_file():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)


def _load_logs():
    _ensure_log_file()
    with open(LOG_PATH, "r") as f:
        return json.load(f)


def _save_logs(logs):
    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)


def log_single_run(config, result):
    logs = _load_logs()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": "single",
        "config": vars(config),
        "metrics": result["metrics"],
        "debug": result.get("debug", {}),
        "output_length": len(result["output"])
    }

    logs.append(entry)
    _save_logs(logs)


def log_comparison_run(config_A, result_A, config_B, result_B, analysis):
    logs = _load_logs()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": "comparison",
        "config_A": vars(config_A),
        "config_B": vars(config_B),
        "metrics_A": result_A["metrics"],
        "metrics_B": result_B["metrics"],
        "analysis": analysis
    }

    logs.append(entry)
    _save_logs(logs)


def load_experiment_history():
    return _load_logs()
