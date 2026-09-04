import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Find the folder containing this Python file
BASE_DIR = Path(__file__).resolve().parent

# Explicitly point to .env (check current dir, then parent dir)
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR.parent / ".env"

print("Looking for .env at:", ENV_PATH)
print(".env exists:", ENV_PATH.exists())


# Load .env
load_dotenv(dotenv_path=ENV_PATH, override=True)


# Get API key
api_key = os.getenv("OPENAI_API_KEY")


if not api_key:

    print("\nERROR: OPENAI_API_KEY was not found.")
    print("Please check that:")
    print("1. .env exists at project root or in the API folder")
    print("2. The variable name is exactly OPENAI_API_KEY")
    print("3. The .env file is saved")

else:

    print("\nAPI key found.")
    print("Key starts with:", api_key[:7])
    print("Key ends with:", api_key[-4:])
    print("Key length:", len(api_key))


    try:

        client = OpenAI(
            api_key=api_key
        )

        try:
            # First try responses API
            response = client.responses.create(
                model="gpt-4.1-mini",
                input="Reply with exactly: SkillSync OpenAI connection successful"
            )
            print("\nSUCCESS!")
            print(response.output_text)
        except Exception:
            # Fallback to chat completions API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "Reply with exactly: SkillSync OpenAI connection successful"}
                ]
            )
            print("\nSUCCESS!")
            print(response.choices[0].message.content.strip())


    except Exception as error:

        print("\nOPENAI ERROR:")
        print(type(error).__name__)
        print(error)

        if "insufficient_quota" in str(error) or "credit_balance_exhausted" in str(error):
            print("\nNote: Authentication succeeded, but your OpenAI account has exhausted its credit balance.")
            print("SkillSync will fall back gracefully to rule-based analysis until credits are added.")