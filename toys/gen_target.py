import json
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam
from gpt_arena.config import env
from termcolor import colored
import random

gen_word_system_prompt = """
You are creating a game such that the user has to create words from a set of letters that can then be combined to craft a new item.

For example, if the user wants to create "Lightning" from "Cloud", you might add the word "Fire" to Cloud.

You should generate a word that can be decomposed into two words. For example: "Steam" could be made of "Water" and "Air". Nuclear missile may be "Uranium" and "Metal", and so on.

Some sample words that could work: steam, air, nuclear missile, earthworm, planet, ice, snow, mammoth, tiger, and so on.

Use the provide_word function to provide the word.
"""

gen_word_function = json.loads(
    """{
  "name": "provide_word",
  "description": "Provide word that can be decomposed into two words",
  "parameters": {
    "type": "object",
    "properties": {
      "explanation": {
        "type": "string",
        "description": "an explanation of why this word was chosen"
      },
      "word": {
        "type": "string",
        "description": "the target word that the user should have to build"
      }
    },
    "required": [
      "explanation",
      "word"
    ]
  }
}
"""
)

gpt = OpenAI(api_key=env.get("OPENAI_API_KEY"))


def gen_target():
    messages = [
        {"role": "system", "content": gen_word_system_prompt},
        {"role": "user", "content": f"Generate a new word please"},
    ]
    tools = [ChatCompletionToolParam(function=gen_word_function, type="function")]
    response = gpt.chat.completions.create(
        messages=messages,
        model="gpt-4",
        temperature=0.5,
        tools=tools,
    )
    tool_calls = response.choices[0].message.tool_calls
    args: dict = json.loads(tool_calls[0].function.arguments)
    return args.get("word").lower()


def main():
    while True:
        input("Press enter to generate a new word...")
        print(f"Word: {gen_target()}")


if __name__ == "__main__":
    main()
