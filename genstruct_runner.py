import logging
import os
import random
from argparse import Namespace

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

__references__ = [
    "https://huggingface.co/NousResearch/Genstruct-7B",
    "https://huggingface.co/spaces/HuggingFaceH4/starchat-playground",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

args = Namespace(
    seed=42, model_name="NousResearch/Genstruct-7B", cache_dir="/cache/huggingface"
)

torch.manual_seed(args.seed)
random.seed(args.seed)


def load_models():
    os.makedirs(args.cache_dir, exist_ok=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        cache_dir=args.cache_dir,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="flash_attention_2",
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, cache_dir=args.cache_dir)
    return model, tokenizer


msg = [
    {
        "title": "p-value",
        "content": "The p-value is used in the context of null hypothesis testing in order to quantify the statistical significance of a result, the result being the observed value of the chosen statistic T {\displaystyle T}.[note 2] The lower the p-value is, the lower the probability of getting that result if the null hypothesis were true. A result is said to be statistically significant if it allows us to reject the null hypothesis. All other things being equal, smaller p-values are taken as stronger evidence against the null hypothesis.",
    }
]
inputs = tokenizer.apply_chat_template(msg, return_tensors="pt").cuda()

print(
    tokenizer.decode(model.generate(inputs, max_new_tokens=512)[0]).split(
        tokenizer.eos_token
    )[0]
)
