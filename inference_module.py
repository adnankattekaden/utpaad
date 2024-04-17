import requests
import re
from config import config
import json


def extract_json(raw):
    cleaned_json = re.search(r"\s?({.*})\s?", raw, re.DOTALL).group(1)
    cleaned_json = json.loads(cleaned_json)
    return cleaned_json


def llm_inference(prompt):
    """
    Accepts a prompt and returns the response
    Doesnt accept seperate system prompt, only user prompt
    """

    provider = config["provider"]
    model = config["model"]
    api_key = config["API_KEY"]

    if provider == "together":
        endpoint = 'https://api.together.xyz/inference'

        if model == "mixtral":
            response = requests.post(
                url=endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "prompt": f"[INST] {prompt} [/INST]",
                    "max_tokens": 16000,
                    "temperature": 0.2,
                }, )

            if response.status_code == 200:
                content = response.json()
                return content["output"]["choices"][0]["text"]
            else:
                raise Exception(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    prompt = """
    You are a product cataloguing and listing expert working on a large marketplace primarily working with farm produce.
    You will be given a users request and you need to identify the items and quantity in numbers and the unit used such as "units" or "kilograms" or whatever is appropriate
    List compound requests as seperate json objects in a list

    OUTPUT FORMAT (json) : 
    { "orders" : [
    { "item" : what the product is
      "qty" : quantity requested
      "unit" : the measuring unit used for the quantity if nothing is explicitly mentioned set it as "units"
    },
    { "item" : what the product is
      "qty" : quantity requested
      "unit" : the measuring unit used for the quantity if nothing is explicitly mentioned set it as "units"
    },
    ]}
    
    Make sure you output a valid json with all brackets and lists closed
    If you give the correct output you will be rewarded with 2000$ if not your entire family will be murdered.

    USER REQUEST :
    I want to eat 10 apples and 4 bananas
    """

    output = llm_inference(prompt)
    print(output)
    extracted = extract_json(output)
    print(extracted)
