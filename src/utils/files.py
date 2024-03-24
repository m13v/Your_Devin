from utils.logger import log
import json
import yaml

def read_file(file_path: str) -> str:
    log.info(f"Reading file from: {file_path}")
    with open(file_path, "r") as f:
        return f.read()

def write_file(file_path: str, content: str):
    with open(file_path, "w") as f:
        f.write(content)

def write_json_file(file_path: str, content: dict):
    log.info(f"Writing to file to: {file_path}")
    with open(file_path, "w") as f:
        json.dump(content, f, indent=2)

def write_yaml_file(file_path: str, content: dict):
    log.info(f"Writing to file to: {file_path}")
    with open(file_path, "w") as f:
        yaml.dump(content, f)

def write_jsonl_file(file_path: str, content: dict):
    log.info(f"Writing to file to: {file_path}")
    with open(file_path, "w") as f:
        for item in content:
            json.dump(item, f)
            f.write("\n")