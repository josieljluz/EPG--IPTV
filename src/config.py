import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_sources():
    return load_json(
        ROOT_DIR / "config" / "sources.json"
    )


def load_channels():
    data = load_json(
        ROOT_DIR / "config" / "channels.json"
    )

    return data.get("channels", [])