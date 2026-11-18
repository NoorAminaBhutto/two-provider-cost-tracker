import os
import sys
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)


def calculate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    return input_cost + output_cost


def get_price(variable):
    try:
        return float(os.getenv(variable, "0"))
    except ValueError:
        raise ValueError(f"Invalid price value in .env: {variable}")


def run_gemini(prompt):
    print("\nConnecting to Gemini...", flush=True)

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key or not model:
        raise ValueError("Gemini API key or model is missing in .env")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=60000,
            retry_options=types.HttpRetryOptions(
                attempts=3,
                initial_delay=2,
                max_delay=10,
                exp_base=2,
                jitter=1
            )
        )
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    reply = response.text or "No text response received."

    usage = response.usage_metadata

    input_tokens = (
        getattr(usage, "prompt_token_count", 0) or 0
    ) if usage else 0

    output_tokens = (
        getattr(usage, "candidates_token_count", 0) or 0
    ) if usage else 0

    cost = calculate_cost(
        input_tokens,
        output_tokens,
        get_price("GEMINI_INPUT_PRICE"),
        get_price("GEMINI_OUTPUT_PRICE")
    )

    return {
        "provider": "Gemini",
        "model": model,
        "status": "success",
        "response": reply,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost
    }


def run_groq(prompt):
    print("\nConnecting to Groq...", flush=True)

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key or not model:
        raise ValueError("Groq API key or model is missing in .env")

    client = Groq(
        api_key=api_key,
        timeout=30.0,
        max_retries=0
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content or ""

    usage = response.usage

    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    cost = calculate_cost(
        input_tokens,
        output_tokens,
        get_price("GROQ_INPUT_PRICE"),
        get_price("GROQ_OUTPUT_PRICE")
    )

    return {
        "provider": "Groq",
        "model": model,
        "status": "success",
        "response": reply,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost
    }


def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your prompt: ").strip()

    if not prompt:
        print("Please enter a prompt.")
        return

    results = []

    providers = [
        ("Gemini", run_gemini),
        ("Groq", run_groq)
    ]

    print("\n" + "=" * 60)
    print("          TWO PROVIDER COST TRACKER")
    print("=" * 60)

    for name, function in providers:
        try:
            result = function(prompt)
            results.append(result)

            print(f"\n{name} Response:")
            print(result["response"])
            print(f"\n{name} completed successfully.")

        except Exception as error:
            print(f"\n{name} failed: {error}")

            results.append({
                "provider": name,
                "status": "failed",
                "error": str(error)
            })

    print("\n" + "=" * 65)
    print("COST SUMMARY")
    print("=" * 65)

    print(
        f"{'Provider':<12}"
        f"{'Input':<12}"
        f"{'Output':<12}"
        f"{'Total':<12}"
        f"{'Cost':<12}"
    )

    print("-" * 65)

    for result in results:
        if result["status"] == "success":
            print(
                f"{result['provider']:<12}"
                f"{result['input_tokens']:<12}"
                f"{result['output_tokens']:<12}"
                f"{result['total_tokens']:<12}"
                f"${result['cost']:.8f}"
            )
        else:
            print(f"{result['provider']:<12}FAILED")

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "results": results
    }

    output_file = ROOT / "results.json"

    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                output_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"\nResults saved to: {output_file}")

    except OSError as error:
        print(f"\nCould not save results: {error}")

    print("\nTracker finished.")


if __name__ == "__main__":
    main()