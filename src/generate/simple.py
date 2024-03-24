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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import os
from utils.mistral_api import llm_request
from utils.files import read_file, write_json_file

from utils.logger import log

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
            results.append({"question": question, "answer": answer})
            log.info(f"completed {i + 1} / {len(questions)}")
        except Exception as e:
            log.error(e)
            # log.error(f"{e.args}")
        finally:
            time.sleep(snooze)
    return results


def generate_simple():
    # FIXME: extract other code from repo
    code = "data/code/model.py"

    questions = generate_list_questions(persona=args.persona, code=code)
    log.info("Questions:")
    log.info(len(questions))
    write_json_file("data/questions.json", questions)

    results = second_round_generation(code=code, questions=questions)

    # with gzip.open("output.json.gz", "wb") as f:
    #     f.write(json.dumps(results).encode("utf-8"))

if __name__ == "__main__":
    generate_simple()
