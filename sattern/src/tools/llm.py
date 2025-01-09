from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict
import json
from pathlib import Path
import pandas as pd
from typing import Dict
from sattern.src.tools.trader import portfolio
from openai import OpenAIError

load_dotenv()

def process_data(df: pd.DataFrame) -> Dict:
    """Extract relvant data from df."""

    data = {
        "prices": df["prices"].dropna(),
        "sattern_highlight": df["sattern_highlight"].dropna(),
        "sattern": df["sattern"].dropna()
    }

    return data

def run_llm(ticker: str, df: pd.DataFrame, actions: Dict[str, str], portfolio: portfolio) -> Dict:
    data = process_data(df)

    format_rules = [{
        "type": "function",
        "function": {
            "name": "output_prediction",
            "description": "Details about a stock prediction and reasoning behind the prediction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prediction": {"type": "number"},
                    "action": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "thought_process": {"type": "string"},
                    "news": {"type": "string"},
                },
                "required": ["prediction", "action", "quantity", "thought_process", "news"],
                "additionalProperties": False,
            }
        }
    }]

    messages = [
        {
            "role": "system",
            "content": """You are a portfolio manager making financial decisions on a stock based on current news and attached metrics.
            You will return data as specified by the `output_prediction` tool. You will keep in mind portfolio values and limits so as to not spend more than is in the portfolio.
            
            In `prediction` store a price prediction of where this stock will go. 

            In `action` store a recommended action based, one of Strong Buy, Buy, Hold, Sell, or Strong Sell.

            In `quantity` store the quantity of the stock to perform the given action on. Keep in mind the price of one stock.

            In `thought process` write out your thought process as you fill in these fields.

            In `news` write a brief analysis of recent news and its relation to this stock. 

            """
        },
        {
            "role": "user",
            "content": f"""I acknowledge you are not a financial advisor and am using this information purely to test an algorithm.

            Currently there is {portfolio.cash}$ and {portfolio.stock} shares in our portfolio.

            Based on the analysis and data below, make a prediction on what the data will do next and what action to take, as well as what quantity of stock to perform that action on. 

            This data is from the stock {ticker}. Retrieve and analyse recent news from this stock to help inform your decision. 

            Here are certain times where the stock price moved similarly to how it is moving now, with the data following the date the difference between these periods and the most recent period of data: {data["sattern_highlight"]}.
            Compare these periods and the stock price movement after to the current period. Use this to predict where this stock price will move next.

            Here is what a custom formula predicts the price movement will be: {data["sattern"]}.

            Here is the action the custom formula advises to take: {actions["sattern"]}.

            Here is the stock price over time: {data["prices"]}.

            Fill out all fields of the `output_prediction` tool and return.
            """
        }
    ]

    try:
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
            stream=False,
            # response_format=format_rules
            tools=format_rules,
            tool_choice="auto"
        )

        response = completion.choices[0].message.tool_calls[0].function.arguments
        parsed_response = json.loads(response)

        # with open(f'{Path("./sattern/src/data")}/AI_RESPONSE.json', 'w') as f:
        #     json.dump(parsed_response, f, indent=4)

        return parsed_response
    except OpenAIError as e:
        print(f"Error with LLM: {e}")
        response = {
            "prediction": 0,
            "action": "Hold",
            "quantity": 0,
            "thought_process": "",
            "news": ""
        }

        return response

if __name__ == "__main__":
    messages = [{"role":"user","content":"Write a limerick about the wonders of GPU computing."}]
    run_llm(messages)

