# Getting Started

1. [Create a new OpenAI API key](https://platform.openai.com/account/api-keys)
1. (Optional) The free trial tier for OpenAI API access is severely rate limited; consider upgrading to a paid account
1. Rename `.env.sample` to `.env` and update it with your API key
1. (Optional) Set up a virtual environment:
    * `python -m venv .venv`
    * `.venv\Scripts\activate`
    * `python.exe -m pip install --upgrade pip`
1. Install packages: `pip install -r requirements.txt`
    * If you are on Windows and encounter a problem installing `chromadb`, please see [this GitHub Issue](https://github.com/chroma-core/chroma/issues/189#issuecomment-1454418844) for a fix

Note: these samples use the GPT-3.5 Turbo model because it is available for Free Trial accounts. Consider switching to a GPT-4 series model if you upgraded to a paid account.

## Regenerate requirements.txt

`pipreqs . --ignore ".venv"`
