import os
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(BASE_DIR, ".env"),
    override=True
)


# ============================================================
# API KEY
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in .env"
    )


# ============================================================
# CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(
    prompt: str,
    max_retries: int = 1
) -> str:

    last_error = None

    for attempt in range(max_retries + 1):

        try:

            start = time.perf_counter()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "temperature": 0,
                    "max_output_tokens": 300
                }
            )

            elapsed = time.perf_counter() - start

            print(
                f"[Gemini: {elapsed:.2f}s]"
            )

            if response.text:
                return response.text.strip()

            return ""

        except Exception as error:

            last_error = error

            error_text = str(error)

            if any(
                code in error_text
                for code in [
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "quota"
                ]
            ):

                raise RuntimeError(
                    "Gemini API quota is currently unavailable."
                ) from error

            temporary = any(
                code in error_text
                for code in [
                    "500",
                    "502",
                    "503",
                    "504",
                    "UNAVAILABLE"
                ]
            )

            if not temporary:
                raise

            if attempt >= max_retries:
                break

            wait = 2 ** attempt

            print(
                f"[Gemini temporary error. "
                f"Retrying in {wait}s...]"
            )

            time.sleep(wait)

    raise RuntimeError(
        f"Gemini model '{MODEL_NAME}' "
        "is temporarily unavailable."
    ) from last_error