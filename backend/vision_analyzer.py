import base64
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_table_crop(image_path: str, capacity: int) -> dict | None:
    try:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You are analyzing a restaurant table from an overhead camera.
This table has a capacity of {capacity} seats.

Look at the image and count:
1. How many people are currently seated at this table?
2. Is there anyone at the table at all?

Respond ONLY with valid JSON in this exact format:
{{
  "occupied_seats": <number 0 to {capacity}>,
  "has_people": <true or false>,
  "confidence": <"high", "medium", or "low">,
  "notes": "<one short sentence>"
}}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        result = json.loads(content.strip())

        if result.get("confidence") == "low":
            return None

        return result

    except Exception as e:
        print(f"Vision error for {image_path}: {e}")
        return None
