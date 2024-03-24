import torch
from datasets import load_dataset
from peft import AutoPeftModelForCausalLM, LoraConfig
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer

__references__ = [
    "https://www.philschmid.de/fine-tune-google-gemma",
    "https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/blob/main/tokenizer_config.json#L42",
    "https://huggingface.co/datasets/teknium/OpenHermes-2.5",
]

model_id = "mistralai/Mistral-7B-v0.1"
tokenizer_id = "mistralai/Mistral-7B-v0.1"
dataset_id = "teknium/OpenHermes-2.5"

############


def create_conversation(d):
    return {
        "messages": [
            # {
            #     "role": "system",
            #     "content": system_message.format(schema=sample["context"]),
            # },
            {"role": "user", "content": d["conversations"][0]["value"]},
            {"role": "assistant", "content": d["conversations"][1]["value"]},
        ]
    }


dataset = load_dataset(dataset_id, split="train")
dataset = dataset.shuffle().select(range(10_000))
dataset = dataset.map(
    create_conversation, remove_columns=dataset.features, batched=False
)

# dataset = dataset.train_test_split(test_size=2500 / 12500)
dataset_name = "./open_hermes25_formatted.json"
dataset.to_json(dataset_name, orient="records")

############


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16,
    quantization_config=bnb_config,
)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token
tokenizer.chat_template = "{{ bos_token }}{% for message in messages %}{% if (message['role'] == 'user') != (loop.index0 % 2 == 0) %}{{ raise_exception('Conversation roles must alternate user/assistant/user/assistant/...') }}{% endif %}{% if message['role'] == 'user' %}{{ '[INST] ' + message['content'] + ' [/INST]' }}{% elif message['role'] == 'assistant' %}{{ message['content'] + eos_token}}{% else %}{{ raise_exception('Only user and assistant roles are supported!') }}{% endif %}{% endfor %}"


peft_config = LoraConfig(
    lora_alpha=128,
    lora_dropout=0.05,
    r=256,
    bias="none",
    target_modules="all-linear",
    task_type="CAUSAL_LM",
)

args = TrainingArguments(
    output_dir="output",  # directory to save and repository id
    # num_train_epochs=1,  # number of training epochs
    # max_steps=100,
    per_device_train_batch_size=16,  # batch size per device during training
    gradient_accumulation_steps=2,  # number of steps before performing a backward/update pass
    gradient_checkpointing=True,  # use gradient checkpointing to save memory
    optim="adamw_torch_fused",  # use fused adamw optimizer
    logging_steps=10,  # log every 10 steps
    save_strategy="epoch",  # save checkpoint every epoch
    bf16=True,  # use bfloat16 precision
    tf32=True,  # use tf32 precision
    learning_rate=2e-4,  # learning rate, based on QLoRA paper
    max_grad_norm=0.3,  # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,  # warmup ratio based on QLoRA paper
    lr_scheduler_type="constant",  # use constant learning rate scheduler
    push_to_hub=False,  # push model to hub
    report_to="wandb",  # report metrics to tensorboard
)

max_seq_length = 3072
trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=dataset,
    # dataset_text_field="value",
    peft_config=peft_config,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    packing=True,
    dataset_kwargs={
        "add_special_tokens": False,  # We template with special tokens
        "append_concat_token": False,  # No need to add additional separator token
    },
)

trainer.train()

trainer.save_model()


# Load PEFT model on CPU
model = AutoPeftModelForCausalLM.from_pretrained(
    args.output_dir, torch_dtype=torch.float16, low_cpu_mem_usage=True
)

# Merge LoRA and base model and save
merged_model = model.merge_and_unload()
merged_model.save_pretrained(
    args.output_dir, safe_serialization=True, max_shard_size="2GB"
)

merged_model.push_to_hub("temp", variant="bf16")
tokenizer.push_to_hub("temp", variant="bf16")
