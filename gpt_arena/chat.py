import argparse

import yaml
from config import env
from openai import OpenAI
from text import print_messages

gpt = OpenAI(api_key=env.get("OPENAI_API_KEY"))


def render_template(template: str, vars: dict) -> str:
    # TODO(d); make this more robust to handle spaces and delete non-existent vars
    for key, value in vars.items():
        value = str(value).strip() if value else ""
        template = template.replace("{{" + key + "}}", value)
    return template


def perform_chat(
    config: dict, prompt: str | None = None, system_prompt: str | None = None
):
    vars: dict = config.get("vars", {})
    hypers: dict = config.get("hypers", {})

    messages: list[str] = []
    if system_prompt:
        content = render_template(system_prompt, vars)
        messages.append({"role": "system", "content": content})
    if prompt:
        content = render_template(prompt, vars)
        messages.append({"role": "user", "content": content})

    print_messages(messages)

    response = gpt.chat.completions.create(
        model=hypers.get("model", "gpt-4"),
        messages=messages,
        temperature=0,
    )

    if response.choices[0].message.content:
        print(f"Response:\n{response.choices[0].message.content}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="GPT Arena")
    parser.add_argument(
        "-c",
        "--config-file",
        type=argparse.FileType("r", encoding="UTF-8"),
        required=False,
    )
    parser.add_argument(
        "-p",
        "--prompt-file",
        type=argparse.FileType("r", encoding="UTF-8"),
        required=False,
    )
    parser.add_argument(
        "-s",
        "--system-file",
        type=argparse.FileType("r", encoding="UTF-8"),
        required=True,
    )

    args = parser.parse_args()

    config = yaml.safe_load(args.config_file)
    prompt = args.prompt_file.read() if args.prompt_file else None
    system_prompt = args.system_file.read() if args.system_file else None

    perform_chat(config=config, prompt=prompt, system_prompt=system_prompt)
