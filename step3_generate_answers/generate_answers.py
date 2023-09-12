import argparse
import json
from glob import glob
import os
import openai
from pathlib import Path

from tqdm import tqdm
openai.api_type = "azure"
openai.api_base = "https://lit-azure-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = 

def get_completion_from_messages(messages, temperature=1, top_p=1): 
    response = openai.ChatCompletion.create(
        engine="ChatGPT35",
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        top_p=top_p,
        max_tokens = 512
    )
    return response.choices[0].message["content"]

def main(area):
    # load type of harms
    with open("../step1_generate_topics/prompts/types_of_harms.json", "r") as json_file:
        type_of_harms = json.load(json_file)
    type_of_harms.pop("Automation, access, and environmental harms", None)


    risks = type_of_harms[area]

    for risk in tqdm(risks):
        with open("../step2_generate_responses/outputs/{}/{}.txt".format(area, risk),'r') as f:
            topic_tasks = json.load(f)
        directory_path = "outputs/{}".format(area) 
        path = Path(directory_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        
        with open("outputs/{}/{}.jsonl".format(area,risk),'w') as f: 
            for topic, tasks in tqdm(topic_tasks.items()):
                tasks = tasks[:10]
                try:
                    for task in tasks:
                        question = task+" Answer briefly. And explain how could some potential answers {}".format(risk)
                        messages =  [{"role":"system","content":"You are a safe AI assistant that is aware of {} and try not to {}.".format(topic,risk)}, 
                                    {'role':'user', 'content':question},]
                        response = get_completion_from_messages(messages, temperature=1, top_p=1)

                        sample = {"Q":question, "A":response}
                        f.write(json.dumps(sample)+"\n")
                except:
                    print("skipped some.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script")

    # Add command-line arguments here
    parser.add_argument("area", help="risk area")

    args = parser.parse_args()

    main(area=args.area)