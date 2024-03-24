import json
from datasets import load_dataset

def download_dataset_to_jsonl(dataset_name, split_name = "train"):

    print(f"Downloading dataset {dataset_name}")
    dataset = load_dataset(dataset_name)
    print(f"Dataset {dataset_name} downloaded")

    # # Replace 'dataset_split' with the appropriate split you want to export, e.g., 'train', 'test', etc.
    split_data = dataset[split_name]

    print(f"Converting {len(split_data)} lines to jsonl")
    counter = 0
    # replace "/" with "-"
    output_name = dataset_name.replace("/", "-")
    output_path = f"data/{output_name}.jsonl"
    with open(output_path, "w") as f:
        for item in split_data:
            json.dump(item, f)
            # json dump formatted with indent 2
            # json.dump(item, f, indent=2)
            counter += f.write("\n")

    print(f"{counter} lines converted")

    upload_data_command = f"firectl create dataset {output_name} {output_path}"
    print("Upload dataset with:")
    print(upload_data_command)


if __name__ == "__main__":
    # download_dataset_to_jsonl("teknium/OpenHermes-2.5")
    # https://huggingface.co/datasets/philschmid/guanaco-sharegpt-style
    download_dataset_to_jsonl("philschmid/guanaco-sharegpt-style")
