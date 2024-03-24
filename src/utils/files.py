from utils.logger import log
import json

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
