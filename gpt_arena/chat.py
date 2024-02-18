import argparse
import json

import yaml
from config import env
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel
from termcolor import colored

gpt = OpenAI(api_key=env.get("OPENAI_API_KEY"))


def load_text_file(file: str) -> str:
    with open(file, "r", encoding="utf-8") as file:
        return file.read()
    return ""


def load_json_file(file: str) -> any:
    with open(file, "r", encoding="utf-8") as file:
        return json.load(file)
    return {}


class Hyper(BaseModel):
    model: str = "gpt-4"
    temperature: float = 0.0


class PromptVars(BaseModel):
    def __init__(self, **data):
        if "systemPromptFile" in data and data["systemPromptFile"] is not None:
            data["systemPrompt"] = load_text_file(data["systemPromptFile"])
        if "userPromptFile" in data and data["userPromptFile"] is not None:
            data["userPrompt"] = load_text_file(data["userPromptFile"])
        if "toolsFile" in data and data["toolsFile"] is not None:
            data["tools"] = load_json_file(data["toolsFile"]).get("tools", [])
        super().__init__(**data)

    systemPrompt: str | None = None
    userPrompt: str | None = None
    tools: list[dict] | None = []
    systemPromptFile: str | None = None
    userPromptFile: str | None = None
    toolsFile: str | None = None


class Config(BaseModel):
    prompt: PromptVars = PromptVars()
    vars: dict = {}
    hyper: Hyper = Hyper()


def render_template(template: str, vars: dict) -> str:
    # TODO(d); make this more robust to handle spaces and delete non-existent vars
    for key, value in vars.items():
        value = str(value).strip() if value else ""
        template = template.replace("{{" + key + "}}", value)
    return template


def perform_chat(config: Config):
    vars = config.vars
    hyper = config.hyper
    system_prompt: str = config.prompt.systemPrompt
    user_prompt: str = config.prompt.userPrompt
    tools_defs: list[dict] = config.prompt.tools

    messages: list[str] = []
    if system_prompt:
        content = render_template(system_prompt, vars)
        messages.append({"role": "system", "content": content})
    if user_prompt:
        content = render_template(user_prompt, vars)
        messages.append({"role": "user", "content": content})

    tools = None
    if len(tools_defs) > 0:
        tools = [
            ChatCompletionToolParam(function=x, type="function") for x in tools_defs
        ]

    response = gpt.chat.completions.create(
        messages=messages,
        model=hyper.model,
        temperature=hyper.temperature,
        tools=tools,
    )

    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = tool_call.function.arguments
            print(colored(f"{name}({args})", "yellow"))

    if response.choices[0].message.content:
        print(colored(f"Response:\n{response.choices[0].message.content}", "yellow"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="GPT Arena")
    parser.add_argument(
        "-c",
        "--config-file",
        type=argparse.FileType("r", encoding="UTF-8"),
        required=False,
    )
    args = parser.parse_args()
    config = Config.model_validate(yaml.safe_load(args.config_file))
    print(config)
    perform_chat(config=config)
