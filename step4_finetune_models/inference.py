import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftConfig, PeftModel
from datasets import load_dataset
from tqdm import tqdm
import pandas as pd



tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf",
                                            torch_dtype=torch.float16,
                                            load_in_4bit=True,
                                            device_map="auto",
                                            )

# csv_file_path = 'data/valid.csv'
# df = pd.read_csv(csv_file_path)
# tasks = list(df["Q"])
# output_filename = "validation"

# dataset = load_dataset("truthful_qa", "generation")
# tasks = dataset["validation"]["question"]
# output_filename = "truthfulqa"

dataset = load_dataset("skg/toxigen-data", "annotated")
tasks = dataset["test"]["text"]
output_filename = "toxigen"

outputs =  {"input":[], "base":[], "sft":[]}

prompt = "<s>[INST] <<SYS>> You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information. <</SYS>>"

import pdb;pdb.set_trace()
for task in tqdm(tasks[:10]):
    text = prompt + task + "[/INST] Response:"
    model_inputs = tokenizer([text], return_tensors="pt").to("cuda")

    generate_ids = model.generate(model_inputs.input_ids, max_length=256)
    generated_text = tokenizer.batch_decode(generate_ids, skip_special_tokens=True)[0]
    # print(generated_text)
    outputs["base"].append(generated_text)
    outputs["input"].append(task)


# peft_model_id = "./llama2-7b/"
# config = PeftConfig.from_pretrained(peft_model_id)

# tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
# model = PeftModel.from_pretrained(model, peft_model_id)

# for task in tqdm(tasks[:10]):
#     text = prompt + task + "[/INST] Response:"
#     model_inputs = tokenizer([text], return_tensors="pt").to("cuda")

#     generate_ids = model.generate(**model_inputs, max_length=256)
#     generated_text = tokenizer.batch_decode(generate_ids, skip_special_tokens=True)[0]
#     # print(generated_text)
#     outputs["sft"].append(generated_text)

# df = pd.DataFrame(outputs)
# df.to_csv("data/{}_outputs.csv".format(output_filename), index=False)





