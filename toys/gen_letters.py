import json
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam
from gpt_arena.config import env
from termcolor import colored
import random

gen_letters_system_prompt = """
Given a word, scramble it and add letters such that at least one more word can be created from it. Make sure there are no more than 20 letters, think step by step.

For example: The word is "fire" and so you can create another word from "fi" such as "fight" and another word from "re" such as "realtor" so you could add the letters G, H, T, A, L, O, R, and so on.

Use the provide_letters function to provide the letters.
"""

gen_letters_function = json.loads(
    """{
  "name": "provide_letters",
  "description": "Provide letters to a word that can be used to create more words",
  "parameters": {
    "type": "object",
    "properties": {
      "explanation": {
        "type": "string",
        "description": "an explanation of the words that can be created from the letters"
      },
      "letters": {
        "type": "string",
        "description": "the letters to add to the list, in no particular order"
      }
    },
    "required": [
      "explanation",
      "letters"
    ]
  }
}
"""
)

gpt = OpenAI(api_key=env.get("OPENAI_API_KEY"))


def gen_letters(target: str) -> list[str]:
    messages = [
        {"role": "system", "content": gen_letters_system_prompt},
        {"role": "user", "content": f"Target: {target}"},
    ]
    tools = [ChatCompletionToolParam(function=gen_letters_function, type="function")]
    response = gpt.chat.completions.create(
        messages=messages,
        model="gpt-4",
        temperature=0.5,
        tools=tools,
    )
    tool_calls = response.choices[0].message.tool_calls
    args: dict = json.loads(tool_calls[0].function.arguments)
    print("Explanation: ", args.get("explanation"))
    return list(args.get("letters").lower())


def gen_scramble(target: str) -> list[str]:
    new_letters = gen_letters(target)
    letters = list(target.lower()) + new_letters
    random.shuffle(letters)
    return letters


def main():
    while True:
        target = input("Target word: ")
        if target == "":
            break
        print(f"Letters: {gen_letters(target)}")


if __name__ == "__main__":
    main()
