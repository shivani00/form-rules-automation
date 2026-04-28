import json
import os
from uuid import uuid4
from config import config
from logger import get_logger

logger = get_logger("osari_service")

FILE_PATH = os.path.join(config.BASE_DIR, "storage", "osari.json")


def read_data():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        return json.load(f)


def write_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def create_mapping(mapping):
    data = read_data()
    mapping["id"] = str(uuid4())

    data.append(mapping)
    write_data(data)

    logger.info("OSARI mapping created")
    return mapping


def get_mappings():
    return read_data()


def update_mapping(mapping_id, updated):
    data = read_data()

    for i, m in enumerate(data):
        if m["id"] == mapping_id:
            updated["id"] = mapping_id
            data[i] = updated
            write_data(data)
            return updated

    return None