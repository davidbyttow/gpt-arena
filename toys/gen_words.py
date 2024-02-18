import json
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam
from gpt_arena.config import env
from termcolor import colored


gen_words_system_prompt = """
You are creating a game such that the user has to create words from a set of letters that can then be combined to craft a new item.

For example, if you want to create "Lightning" from "Cloud", you might add the word "Fire" to Cloud. And therefore, you would create a set of letters such as: [I, F, C, E, R, A, B, S, U]

If you're given a target word, come up with two words that should be combined to create that target word. For example: "Steam" could be made of "Water" and "Air". Nuclear missile may be "Uranium" and "Metal", and so on.

Use the provide_words function to provide the words.
"""

gen_words_function = json.loads(
    """{
  "name": "provide_words",
  "description": "Provide two words that can be combined into the target word",
  "parameters": {
    "type": "object",
    "properties": {
      "word1": {
        "type": "string",
        "description": "the first word"
      },
      "word2": {
        "type": "string",
        "description": "the second word"
      }
    },
    "required": [
      "word1",
      "word2"
    ]
  }
}
"""
)

gpt = OpenAI(api_key=env.get("OPENAI_API_KEY"))


def gen_words(target):
    messages = [
        {"role": "system", "content": gen_words_system_prompt},
        {"role": "user", "content": f"Target: {target}"},
    ]
    tools = [ChatCompletionToolParam(function=gen_words_function, type="function")]
    response = gpt.chat.completions.create(
        messages=messages,
        model="gpt-4",
        temperature=0,
        tools=tools,
    )
    tool_calls = response.choices[0].message.tool_calls
    args: dict = json.loads(tool_calls[0].function.arguments)
    return [args.get("word1").lower(), args.get("word2").lower()]


def main():
    while True:
        target = input("Target word: ")
        if target == "":
            break
        print(f"Words: {gen_words(target)}")


if __name__ == "__main__":
    main()
