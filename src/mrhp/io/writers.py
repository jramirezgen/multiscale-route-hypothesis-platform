"""File I/O helpers: JSON, Markdown, TSV, hashing, snapshots."""

import hashlib
import json
import os
import shutil
import datetime


def timestamp_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def write_json(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)


def write_md(path: str, content: str) -> int:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return len(content.splitlines())


def write_tsv(path: str, headers: list, rows: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(headers) + "\n")
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")


def safe_div(a, b, default=0.0):
    return a / b if b != 0 else default


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def get_output_dir(base_dir: str) -> str:
    return ensure_dir(os.path.join(base_dir, "outputs"))


def get_report_dir(base_dir: str) -> str:
    return ensure_dir(os.path.join(base_dir, "reports"))


def get_figure_dir(base_dir: str) -> str:
    return ensure_dir(os.path.join(base_dir, "figures"))


def get_log_dir(base_dir: str) -> str:
    return ensure_dir(os.path.join(base_dir, "logs"))


def snapshot_inputs(cfg: dict, yaml_path: str) -> dict:
    """Create SHA-256 snapshot of all input files."""
    snap = {
        "timestamp": timestamp_now(),
        "config_file": os.path.basename(yaml_path),
        "config_sha256": sha256_file(yaml_path),
        "files": {},
    }

    gem_path = cfg.get("gem", {}).get("model_path", "")
    if gem_path and os.path.isfile(gem_path):
        snap["files"]["gem"] = {"path": gem_path, "sha256": sha256_file(gem_path)}

    rtqpcr_path = cfg.get("validation", {}).get("rtqpcr_path", "")
    if rtqpcr_path and os.path.isfile(rtqpcr_path):
        snap["files"]["rtqpcr"] = {"path": rtqpcr_path, "sha256": sha256_file(rtqpcr_path)}

    return snap
