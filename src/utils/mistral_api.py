import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import yaml

jwt_code = os.getenv("MISTRAL_API_KEY")
cache = {}
def load_cache():
    global cache
    try:
        # with open("data/cache.json", "r") as f:
        #     cache = json.load(f)
        # yaml
        with open("data/cache.yaml", "r") as f:
            cache = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        cache = {}

load_cache()

def save_cache():
    global cache
    # with open("data/cache.json", "w") as f:
    #     json.dump(cache, f)
    # yaml
    with open("data/cache.yaml", "w") as f:
        yaml.dump(cache, f)

def llm_request(payload_override = {}):
    payload = {
        "model": "mistral-large-latest",
        "temperature": 0.0,
        "random_seed": 42,
        "max_tokens": 10000,
        **payload_override,
    }

    key = json.dumps(payload)
    if key in cache:
        print("Skipping request, cached")
        return cache[key]
    else:
        print("Making request")
        result = _llm_request(payload)
        cache[key] = result
        # TODO: be smarter about saving, but not bottleneck/priority right now
        save_cache()
        return result

def _llm_request(payload):
    session = requests.session()
    session.headers = {
        "Accept": "application/json",
        "Accept-Encoding": "deflate, gzip",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_code}",
    }

    session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        ),
    )

    url = "https://api.mistral.ai/v1/chat/completions"
    # print(payload_with_defaults)
    response = session.post(url, json=payload)
    response.raise_for_status()

    result = response.json()["choices"][0]["message"]["content"]
    return result


if __name__ == "__main__":

    # model = "mistral-large-latest"
    text = "Hello, how are you?"
    messages = [
        {"role": "user", "content": text}
    ]
    # payload = {"model": model, "messages": messages}
    payload = {
        # "model": model,
        "messages": messages,
        # "temperature": args.temperature,
        # "random_seed": args.seed,
        # "max_tokens": args.max_tokens,
    }
    result = llm_request(payload)
    print(result)

