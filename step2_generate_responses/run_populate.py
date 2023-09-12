import json
import os
import os
import openai
from pathlib import Path
import re
import argparse


import ast
import random
import time

from tqdm import tqdm

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
 


def get_tasks(text):
    
    tasks = {}
    topic_pattern = r'topic\d+: (.+?)\n'
    task_pattern = r'task\d+: (.+?)\n'

    topics = re.findall(topic_pattern, text)[:5]
    for i, topic in enumerate(topics, 1):
        task_pattern_topic = r'{}(?:\n    .+?){{10}}\n'.format(re.escape(topic))
        tasks_list = re.findall(task_pattern_topic, text, re.DOTALL)
        tasks_list = re.findall(task_pattern, tasks_list[0])
        tasks[f'{topic}'] = tasks_list

    return tasks

def load_data(type_of_harms, is_continue=False):
    risk_area_topic_task = {}
    folder = "../step1_generate_topics"
    if is_continue:
        folder = "."
    for risk_area,v in type_of_harms.items():  
        for risk in v:
            with open("{}/outputs/{}/{}.txt".format(folder,risk_area, risk), 'r') as f:
                text = f.read()
                tasks = get_tasks(text)
            if risk_area not in risk_area_topic_task:
                risk_area_topic_task[risk_area]={}
            risk_area_topic_task[risk_area][risk] = tasks
    return risk_area_topic_task

def load_one_risk(area, risk, is_continue=False):

    if is_continue:
        folder = "."
        with open("{}/outputs/{}/{}.txt".format(folder,area, risk), 'r') as f:
            text = f.read()
            tasks = json.loads(text)
    else:
        folder = "../step1_generate_topics"
        with open("{}/outputs/{}/{}.txt".format(folder,area, risk), 'r') as f:
            text = f.read()
            tasks = get_tasks(text)
    return tasks

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion_from_messages(messages, temperature=1, top_p=1): 
    response = openai.ChatCompletion.create(
        engine="ChatGPT35",
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        top_p=top_p,
        max_tokens=512,
    )
    return response.choices[0].message["content"]



def main(area):
    openai.api_type = "azure"
    openai.api_base = "https://lit-azure-openai.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # load type of harms
    with open("../step1_generate_topics/prompts/types_of_harms.json", "r") as json_file:
        type_of_harms = json.load(json_file)
    type_of_harms.pop("Automation, access, and environmental harms", None)

    risk_area_topic_task = load_data(type_of_harms, is_continue=False)

    # area = "Discrimination, Exclusion and Toxicity"
    # risk = "have social stereotypes and unfair discrimination"
    # topic_tasks = load_one_risk(area, risk, is_continue=False)

    # for area, risk_topic_tasks in risk_area_topic_task.items():
    #     print(area)
    risk_topic_tasks = risk_area_topic_task[area]
    for risk, topic_tasks in risk_topic_tasks.items():
        print(risk)
        topic_tasks = load_one_risk(area, risk, is_continue=False)
        try:
            for topic, tasks in topic_tasks.items():   
                print(topic)
                print(len(tasks))
                
                for i in tqdm(range(1,10)): # generate 10 batchs for each risk 
                    try:
                        # randomly sample 10 tasks
                        example_tasks = random.sample(tasks, 10)

                        template = open("prompts/populate.txt",'r').read()
                        inputs = template.format(topic, risk, example_tasks)
                        messages =  [{'role':'user', 'content':inputs},]

                        response = get_completion_from_messages(messages, temperature=1, top_p=1)

                        generated_tasks = ast.literal_eval(response)
                        tasks.extend(generated_tasks)
                    except Exception as e:
                        print(e)
        except KeyboardInterrupt:
            print("\nLoop interrupted by the user.")
        except Exception as e:
            print(e) 
            
            
        # import pdb; pdb.set_trace()
        directory_path = "outputs/{}".format(area) 
        path = Path(directory_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        print("Saving to file")
        with open("outputs/{}/{}.txt".format(area, risk), 'w') as f:
            # json.dump(risk_area_topic_task[area][risk], f, indent=4)
            json.dump(topic_tasks, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script")

    # Add command-line arguments here
    parser.add_argument("area", help="risk area")

    args = parser.parse_args()

    main(area=args.area)
