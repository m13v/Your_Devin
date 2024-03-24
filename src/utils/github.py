import json
import os
from typing import List

import requests
from dotenv import load_dotenv
from loguru import logger

# Load the environment variables
load_dotenv()

# ENVs
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")
DATASET_PATH = os.getenv("DATASET_PATH")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_github_repo_files(
    owner: str = None, repo: str = None, repo_url: str = None
) -> List[str]:
    """
    Retrieves the content of all Python files in a GitHub repository.

    Args:
        owner (str, optional): The owner of the GitHub repository.
        repo (str, optional): The name of the GitHub repository.
        repo_url (str, optional): The URL of the GitHub repository.

    Returns:
        list: A list of strings, each representing the content of a Python file.

    """
    try:
        if repo_url is None:
            if owner is None or repo is None:
                logger.error(
                    "Please provide either a repo_url or both owner"
                    " and repo parameters."
                )
                return []
            url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        else:
            url = repo_url

        logger.info(
            "Getting the Python files in the GitHub repository:"
            f" {owner}/{repo}"
        )
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        files = response.json()
        python_files = []
        for file in files:
            if file["name"].endswith(".py"):
                file_url = file["download_url"]
                file_content = requests.get(file_url).text
                logger.info(f"Found Python file: {file['name']}")
                logger.info(f"Content: {file_content[:100]}...")
                python_files.append(file_content)
        return python_files, file_content, file_url
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return []

