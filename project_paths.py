"""Пути к постоянным данным: локально и на Amvera (/data)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
IS_AMVERA = "AMVERA" in os.environ


def get_data_dir() -> Path:
    if IS_AMVERA:
        return Path("/data")
    return PROJECT_ROOT


def get_users_db_path() -> Path:
    if IS_AMVERA:
        return Path("/data/users.db")
    return PROJECT_ROOT / "database" / "users.db"


def get_metrics_db_path() -> Path:
    if IS_AMVERA:
        return Path("/data/metrics.db")
    return PROJECT_ROOT / "logger" / "reports" / "metrics.db"


def get_cpu_tracer_db_path() -> Path:
    if IS_AMVERA:
        return Path("/data/cpu_tracer.db")
    return PROJECT_ROOT / "cpu_tracer.db"


def ensure_data_dirs() -> None:
    paths = [
        get_users_db_path(),
        get_metrics_db_path(),
        get_cpu_tracer_db_path(),
    ]
    if not IS_AMVERA:
        paths.append(PROJECT_ROOT / "logger" / "reports")

    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
