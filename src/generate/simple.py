from dotenv import load_dotenv
# Load the environment variables
load_dotenv()

import gzip
import json
import logging
import time
from argparse import Namespace
from typing import List, Optional
import requests


# import requests
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry

import os
import distutils
from utils.mistral_api import llm_request
from utils.files import read_file, write_json_file, write_yaml_file, write_jsonl_file
from utils.logger import log
from generate.types import Role, Message, Conversation

args = Namespace(
    jwt_token=os.getenv("MISTRAL_API_KEY"),
    temperature=0.0,
    seed=42,
    # max_tokens=32768,
    max_tokens=100,
    persona="deep learning researcher",
)

log.info("args")
log.info(args)

list_questions_prompt = read_file("src/prompts/list-questions-1.md")
write_answers_prompt = read_file("src/prompts/write-answers-1.md")

def generate_list_questions(persona: str, code: str):
    log.info("Generating questions...")
    text = list_questions_prompt.format(code=code, persona=persona).strip()
    questions_text = llm_request({
        "messages": [{"role": "user", "content": text}]
    })
    log.info("Questions generated successfully!")
    # split questions by line
    questions = questions_text.split("\n")
    # remove number prefix (e.g. "123."). There may be other "." in line
    # questions = [q.split(".", 1)[1].strip() for q in questions if q]
    # handle list index out of range
    questions = [q.split(".", 1)[1].strip() for q in questions if len(q.split(".", 1)) > 1]
    return questions

def second_round_generation(
    code: str, questions: List[str], snooze: Optional[int] = 0.1
):
    log.info("Generating answers...")
    results = []
    # print(questions)

    for i, question in enumerate(questions):
        print(i, question)
        try:
            text = write_answers_prompt.format(question=question, code=code)
            # answer = call_mistral(session=session, text=text)
            answer = llm_request({
                "messages": [{"role": "user", "content": text}]
            })
            print(answer)
            user_message = Message(role=Role.user, content=question) # TODO: code in context?
            assistant_message = Message(role=Role.assistant, content=answer)
            # results.append({"question": question, "answer": answer})
            convo = Conversation(messages=[user_message, assistant_message])
            results.append(convo.dict())
            log.info(f"completed {i + 1} / {len(questions)}")

            # if i == 6:
            #     break

        except Exception as e:
            log.error(e)
            # log.error(f"{e.args}")
        finally:
            time.sleep(snooze)
    return results

def write_fine_tune_config(datetime: str):
    contents = f"""
# The ID of the dataset you created above.
dataset: devin-{datetime}

conversation: {{}}

# The Hugging Face model name of the base model.
base_model: mistralai/Mistral-7B-v0.1
"""
    output_path = f"data/{datetime}/fine-tune-config.yaml"
    with open(output_path, "w") as f:
        f.write(contents)

    print()
    print("Perform fine-tune config with:")
    # firectl create fine-tuning-job --settings-file path/to/settings.yaml --display-name "My Job"
    print(f" firectl create fine-tuning-job --settings-file {output_path} --display-name \"Devin - {datetime}\"")

def generate_simple():
    datetime = time.strftime("%Y-%m-%d-%H-%M-%S")
    # FIXME: extract other code from repo

    code = "data/code/model.py,data/code/model2.py"

    questions = generate_list_questions(persona=args.persona, code=code)

    # output_path = f"data/questions-{datetime}.json"
    # write_json_file(output_path, questions)
    # ensure data/{datetime} directory exists
    os.makedirs(f"data/{datetime}", exist_ok=True)
    output_path = f"data/{datetime}/questions.yaml"
    write_yaml_file(output_path, questions)
    results = second_round_generation(code=code, questions=questions)

    # with gzip.open("output.json.gz", "wb") as f:
    #     f.write(json.dumps(results).encode("utf-8"))
    # output_path = f"data/conversions-{datetime}.json"
    # write_json_file(output_path, results)

    write_yaml_file(f"data/{datetime}/conversions.yaml", results)
    write_jsonl_file(f"data/{datetime}/conversions.jsonl", results)

    print()
    print("Upload dataset with:")
    print(f" firectl create dataset devin-{datetime} data/conversions-{datetime}.jsonl")

    write_fine_tune_config(datetime)

if __name__ == "__main__":
    generate_simple()
