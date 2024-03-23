import json
import os

import requests
from dotenv import load_dotenv
from swarms import AbstractLLM, Agent, Mistral
from loguru import logger


# Load the environment variables
load_dotenv()


# QA prompt
def get_qa_prompt(code: str):
    prompt = f"""
    
    Write 50 detailed question and answer pairs about the following code, focusing on aspects important to a deep learning researcher. Ensure the questions are specific and address the implementation's nuances: 
    
    {code}
    """
    return prompt


def get_github_repo_page(owner: str, repo: str) -> str:
    """
    Retrieves the HTML content of a GitHub repository page.

    Args:
        owner (str): The owner of the GitHub repository.
        repo (str): The name of the GitHub repository.

    Returns:
        str: The HTML content of the GitHub repository page.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    """
    try:
        logger.info(f"Getting the GitHub repository page: {owner}/{repo}")
        url = f"https://github.com/{owner}/{repo}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return None


def get_github_repo_files(owner: str, repo: str) -> list:
    """
    Retrieves the content of all Python files in a GitHub repository.

    Args:
        owner (str): The owner of the GitHub repository.
        repo (str): The name of the GitHub repository.

    Returns:
        list: A list of strings, each representing the content of a Python file.

    """
    try:
        logger.info(
            f"Getting the Python files in the GitHub repository: {owner}/{repo}"
        )
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        files = response.json()
        python_files = []
        for file in files:
            if file["name"].endswith(".py"):
                file_url = file["download_url"]
                file_content = requests.get(file_url).text
                python_files.append(file_content)
        return python_files
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return []
    
    
def fetch_code_from_github(owner: str, repo: str) -> str:
    """
    Fetches the code from a GitHub repository.

    Args:
        owner (str): The owner of the GitHub repository.
        repo (str): The name of the GitHub repository.

    Returns:
        str: The code from the GitHub repository.

    """
    code = get_github_repo_files(owner=owner, repo=repo)
    
    # Combine all the code files into a single string
    code = "\n".join(code)
    return code

    
    
# Create a dataset from the github code -- to
def create_dataset_from_repo(
    model: AbstractLLM,
    file_name: str = "dataset.json",
):
    """
    Create a dataset from a GitHub repository.

    Args:
        model (AbstractLLM): The language model to use for generating the dataset.
        file_name (str): The name of the output JSON file.

    """
    # Get the GitHub repository page
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    
    
    # Get code
    code = fetch_code_from_github(owner=owner, repo=repo)

    # Agent
    agent = Agent(
        llm=Mistral(),
        agent_name="Devin",
        max_loops=1,
        system_prompt="You're a software developer working on a project. Be helpful and follow instructions",
        sop=get_qa_prompt(code),
    )

    # Extract the code from the GitHub repository page
    code = get_github_repo_page(owner=owner, repo=repo)

    # Generate the dataset
    dataset = []
    for example in code:
        # Generate response from the agent
        response = agent(example)

        # Append example and response to the dataset
        dataset.append({"from": code, "value": response})

    # Save the dataset to a file
    dataset_path = os.getenv("DATASET_PATH")
    with open(dataset_path, "w") as file:
        json.dump(dataset, file)

    print(f"Dataset saved to: {dataset_path}")
