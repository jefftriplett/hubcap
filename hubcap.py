import os
import subprocess
import sys
import time
import typer

from rich import print


SYSTEM = (
    "you are a coding agent. "
    """you can read and write files. Eg `cat helloworld.txt`, `echo "hello\nworld" > helloworld.txt` output the next command required to progress your goal. """
    "output `DONE` when done."
)


def chat(*, prompt: str, system: str | None = None) -> str:
    if system:
        options = f"--system {quote(system)}"
    else:
        options = "--continue"

    print(f"[blue][PROMPT][/blue] {prompt}")
    response = subprocess.getoutput(f"llm {options} {quote(prompt)}\n")
    print(f"[yellow][RESPONSE][/yellow] {response}")
    return response


def quote(string: str) -> str:
    # Equivalent of PHP's escapeshellarg
    return "'{}'".format(string.replace("'", "'\\''"))


def main(prompt: str):
    response = chat(
        prompt=f"GOAL: {prompt}\n\nWHAT IS YOUR OVERALL PLAN?", system=SYSTEM
    )

    while True:
        response = chat(
            prompt="SHELL COMMAND TO EXECUTE OR `DONE`. NO ADDITIONAL CONTEXT OR EXPLANATION:"
        ).strip()
        if response == "DONE":
            break

        time.sleep(3)

        try:
            output = subprocess.check_output(
                response, stderr=subprocess.STDOUT, shell=True
            ).decode()
            return_code = 0
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
            return_code = e.returncode

        response = chat(
            prompt=f"COMMAND COMPLETED WITH RETURN CODE: {return_code}. OUTPUT:\n"
            f"{output}\n\n"
            "WHAT ARE YOUR OBSERVATIONS?"
        )


if __name__ == "__main__":
    typer.run(main)
