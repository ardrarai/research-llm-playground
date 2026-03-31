import json
import os
from datetime import datetime
from utils.behavior_interpreter import interpret_metrics

LOG_PATH = "data/experiments/experiment_log.json"


def _ensure():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        json.dump([], open(LOG_PATH, "w"))


def _load():
    _ensure()
    return json.load(open(LOG_PATH))


def _save(data):
    json.dump(data, open(LOG_PATH, "w"), indent=2)


def log_single_run(config, result):

    logs = _load()

    logs.append({
        "timestamp": datetime.now().isoformat(),
        "mode": "single",
        "config": vars(config),
        "metrics": result["metrics"],
        "debug": result.get("debug", {}),
        "insights": interpret_metrics(result)
    })

    _save(logs)


def log_comparison_run(config_A, result_A, config_B, result_B, analysis):

    logs = _load()

    logs.append({
        "timestamp": datetime.now().isoformat(),
        "mode": "comparison",
        "config_A": vars(config_A),
        "config_B": vars(config_B),
        "analysis": analysis
    })

    _save(logs)


def load_experiment_history():
    return _load()
