from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

def run_llm(data):

    format_rules = [
    {
        "type": "function",
        "function": {
            "name": "output_prediction",
            "description": "Details about a stock prediction and reasoning behind the prediction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prediction": {
                        "type": "float",
                        "description": "Price prediction of where this stock will go."
                    },
                    "action": {
                        "type": "string",
                        "description": "Recommended action based on the prediciton and confidence. One of Strong Buy, Buy, Hold, Sell, or Strong Sell"
                    },
                    "quantity": {
                        "type": "int",
                        "description": "Stock quantity to perform the given action on. Keep in mind portfolio limits."
                    },
                    "thought_process": {
                        "type": "string",
                        "description": "Thought process as you think through this."
                    },
                    "news": {
                        "type": "string",
                        "description": "Analysis of recent news and its relation to this stock."
                    },
                },
                "required": ["prediction", "confidence", "news"],
                "additionalProperties": False,
            }
        }
    }
    ]

    messages = [
        {
            "role": "system",
            "content": """You are a portfolio manager making financial decisions on a stock based on current news and attached metrics.
            You will return data as specified by the `output_prediction` tool. You will keep in mind portfolio values and limits so as to not spend more than is in the portfolio."""
        },
        {
            "role": "user",
            "content": f"""I acknowledge you are not a financial advisor and am using this information purely to test an algorithm.

            Based on the analysis and data below, make a prediction on what the data will do next and what action to take, as well as what quantity of stock to perform that action on. 

            This data is from the stock {data["ticker"]}. Retrieve and analyse recent news from this stock to help inform your decision. 

            Here are certain times where the stock price moved similarly to how it is moving now, with the data following the date the difference between these periods and the most recent period of data: {data["sattern_highlight"]}.
            Compare these periods and the stock prive movement after to the current period. Use this to predict where this stock price will move next.

            Here is what a custom formula predicts the price movement will be: {data["sattern"]}.

            Here is the action the custom formula advises to take: {data["sattern_decision"]}.

            Here is the stock price over time: {data["prices"]}.

            Fill out all fields of the `output_prediction` tool and return. 
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
        stream=True,
        tools=format_rules,
        tool_choice="output_prediction"
    )

    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

if __name__ == "__main__":
    messages = [{"role":"user","content":"Write a limerick about the wonders of GPU computing."}]
    run_llm(messages)

