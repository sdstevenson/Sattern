from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

def run_llm(data):
    messages = [
        {
            "role": "user",
            "content": f"""
            Based on the analysis below, make your decision on what the data will do next. 

            This data is from the stock {data["ticker"]}. Retrieve and analysise recent news from this stock to inform your decision. 

            Here are periods of data where the data moved similarly to how it is moving now, with the data following the data the difference between these periods and the most recent data: {data["sattern_highlight"]}
            Compare these periods and their movement after to the current period and use that to predict where this data will move next.

            Here is what a custom formula predicts will happen to the data: {data["sattern"]}

            And here is the current data: {data["prices"]}.

            Give your own prediction of what the data will get to in 20 days, and the estimated probability as a percentage of this happening. 
            """
        }
    ]

    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.getenv('NIM_API_KEY')
    )

    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=messages,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

if __name__ == "__main__":
    messages = [{"role":"user","content":"Write a limerick about the wonders of GPU computing."}]
    run_llm(messages)

