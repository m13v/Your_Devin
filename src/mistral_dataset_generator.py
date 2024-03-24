import gzip
import json
import logging
import time
from argparse import Namespace
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

args = Namespace(
    jwt_token="TWfVrlX659GSTS9hcsgUcPZ8uNzfoQsg",
    temperature=0.0,
    seed=42,
    max_tokens=32768,
    persona="deep learning researcher",
)

prompt1 = """Write 200 detailed questions about the following code below, focusing on aspects important to a {args.persona}. Ensure the questions are specific and address the implementation's nuances:\n\n{code}"""

prompt2 = """Given the question and the code snippet provided below, generate a comprehensive, detailed answer. The response should be well-structured, covering the foundational concepts for beginners, including intermediate details and insights, and also addressing advanced considerations where applicable. Aim to make the explanation accessible to a broad audience, gradually building from basic principles to more complex ideas as the answer progresses.

    Question: {question}

    Code Snippet:
    {code}

    ---

    Comprehensive Answer:
    - Overview: Provide a brief introduction to the topic, ensuring it is accessible to beginners.
    - Detailed Explanation: Delve into the specifics of the question, offering a clear and thorough understanding. Incorporate intermediate-level details and explanations, ensuring to explain any technical terms or advanced concepts introduced.
    - Advanced Insights: Where relevant, include advanced-level insights or considerations, providing depth and showing the implications or potential applications of the topic at a high level of expertise.
    - Conclusion: Summarize the key points made throughout the answer, reinforcing the learning and ensuring clarity on the topic.

    Please ensure the answer is logically structured, progressively building in complexity and thoroughly covering the topic in a manner that educates and engages readers across various levels of expertise.
    """.strip()


def call_mistral(session, text: str):
    url = "https://api.mistral.ai/v1/chat/completions"
    model = "mistral-large-latest"
    messages = [{"role": "user", "content": text}]

    response = session.post(
        url,
        json={
            "model": model,
            "messages": messages,
            "temperature": args.temperature,
            "random_seed": args.seed,
            "max_tokens": args.max_tokens,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def first_round_generation(session, code: str):
    text = prompt1.format(code=code).strip()
    questions = call_mistral(session=session, text=text)
    return questions


def second_round_generation(
    session, code: str, questions: List[str], snooze: Optional[int] = 1
):
    results = []
    for i, question in enumerate(questions):
        try:
            text = prompt2.format(question=question, code=code)
            answer = call_mistral(session=session, text=text)
            results.append({"question": question, "answer": answer})
            log.info(f"completed {i + 1} / {len(questions)}")
        except Exception as e:
            log.error(f"{e.args}")
        finally:
            time.sleep(snooze)
    return results


def main():
    session = requests.session()
    session.headers = {
        "Accept": "application/json",
        "Accept-Encoding": "deflate, gzip",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.jwt_token}",
    }

    session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=5, backoff_factor=1, status_forcelist=[502, 503, 504]
            )
        ),
    )

    with open("./model.py", "rb") as f:
        code = f.read()

    questions = first_round_generation(session=session, code=code)
    results = second_round_generation(session=session, code=code, questions=questions)

    with gzip.open("output.json.gz", "wb") as f:
        f.write(json.dumps(results).encode("utf-8"))
