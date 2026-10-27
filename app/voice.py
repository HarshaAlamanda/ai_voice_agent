import asyncio
import re
import shutil
import subprocess
import time

import edge_tts
import speech_recognition as sr

from app.agent import ask_agent
from app.conversation import ConversationManager


class VoiceReceptionist:
    def __init__(self):
        # ============================================================
        # SPEECH RECOGNITION
        # ============================================================
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.4

        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.10
        self.recognizer.dynamic_energy_ratio = 1.35

        # ============================================================
        # CONVERSATION MANAGER
        # ============================================================
        self.manager = ConversationManager()

        # ============================================================
        # EDGE TTS
        # ============================================================
        self.voice = "en-IN-NeerjaNeural"
        self.rate = "+40%"
        self.volume = "+0%"
        self.pitch = "+0Hz"

        # ============================================================
        # AUDIO PLAYER
        # ============================================================
        self.ffplay = shutil.which("ffplay")

        if not self.ffplay:
            raise RuntimeError(
                "ffplay was not found in PATH. "
                "Install FFmpeg and ensure ffplay is available."
            )

        # ============================================================
        # MICROPHONE CALIBRATION
        # ============================================================
        print("Calibrating microphone...")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.8
                )
        except Exception as error:
            print(f"Microphone calibration warning: {error}")

        print("Microphone ready.")

    # ================================================================
    # EMAIL NORMALIZATION
    # ================================================================
    @staticmethod
    def normalize_spoken_email(text: str) -> str:
        """
        Convert common spoken email symbols into written form.

        Examples:
            name at gmail dot com -> name@gmail.com
            name at the rate gmail dot com -> name@gmail.com

        This does not guess missing characters.
        """

        if not text:
            return ""

        value = text.strip().lower()

        replacements = [
            (r"\bat the rate\b", "@"),
            (r"\bat rate\b", "@"),
            (r"\bat sign\b", "@"),
            (r"\bat\b", "@"),
            (r"\bdot\b", "."),
            (r"\bperiod\b", "."),
            (r"\bunderscore\b", "_"),
            (r"\bunder score\b", "_"),
            (r"\bhyphen\b", "-"),
            (r"\bdash\b", "-"),
        ]

        for pattern, replacement in replacements:
            value = re.sub(pattern, replacement, value)

        # Remove spaces around email symbols.
        value = re.sub(r"\s*@\s*", "@", value)
        value = re.sub(r"\s*\.\s*", ".", value)
        value = re.sub(r"\s*_\s*", "_", value)
        value = re.sub(r"\s*-\s*", "-", value)

        # Remove spaces between digits:
        # 1587 -> remains 1587
        # 1 5 8 7 -> 1587
        value = re.sub(r"(?<=\d)\s+(?=\d)", "", value)

        # Remove spaces between spoken letters before @.
        # a h a r s h a@gmail.com -> aharsha@gmail.com
        if "@" in value:
            local, domain = value.split("@", 1)

            local = re.sub(
                r"(?<=\b[a-z])\s+(?=[a-z]\b)",
                "",
                local
            )

            # Also remove spaces throughout a local part made
            # exclusively of individual letters and digits.
            if re.fullmatch(r"(?:[a-z]\s+)+[a-z0-9]*", local):
                local = re.sub(r"\s+", "", local)

            value = local + "@" + domain

        # Extract an email-shaped candidate if one exists.
        match = re.search(
            r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
            value
        )

        if match:
            return match.group(0)

        return value.strip()

    # ================================================================
    # SPEECH RECOGNITION
    # ================================================================
    def listen(self):
        """
        Record a complete utterance and recognize Indian English.
        A longer phrase limit gives the caller time to spell an email.
        """

        try:
            with self.microphone as source:
                print("\nListening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=25
                )

        except sr.WaitTimeoutError:
            print("Listening timeout.")
            return ""

        except Exception as error:
            print(f"Microphone error: {error}")
            return ""

        start = time.perf_counter()

        # Try Indian English first.
        # Try US English only if the first attempt cannot understand.
        text = ""

        for language in ("en-IN", "en-US"):
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=language
                )

                if text:
                    break

            except sr.UnknownValueError:
                continue

            except sr.RequestError as error:
                print(f"Speech recognition service error: {error}")
                return ""

            except Exception as error:
                print(f"Speech recognition error: {error}")
                return ""

        if not text:
            print("Could not understand the caller.")
            return ""

        elapsed = time.perf_counter() - start

        print(f"[Speech recognition: {elapsed:.2f}s]")
        print(f"Caller: {text}")

        # Normalize when the utterance appears to contain an email.
        lower_text = text.lower()

        email_indicators = [
            "email",
            "gmail",
            "outlook",
            "yahoo",
            "hotmail",
            "at the rate",
            "at rate",
            "dot com",
            "@",
        ]

        if any(word in lower_text for word in email_indicators):
            normalized = self.normalize_spoken_email(text)

            if normalized != lower_text.strip():
                print(f"[Email normalization: {normalized}]")

            return normalized

        return text.strip()

    # ================================================================
    # LOOKUP ACKNOWLEDGEMENT
    # ================================================================
    def should_use_lookup_ack(self, text: str) -> bool:
        """Identify requests that may require appointment lookups."""

        text_lower = text.lower()

        lookup_words = [
            "meeting",
            "meet",
            "appointment",
            "book",
            "booking",
            "schedule",
            "available",
            "availability",
            "slot",
            "tomorrow",
            "today",
            "thursday",
            "friday",
            "monday",
            "tuesday",
            "wednesday",
            "saturday",
            "sunday",
            "next week",
            "this week",
        ]

        return any(word in text_lower for word in lookup_words)

    # ================================================================
    # QUICK ACKNOWLEDGEMENT
    # ================================================================
    def speak_acknowledgement(self):
        self.speak(
            "Sure, give me a moment while I check the available slots."
        )

    # ================================================================
    # EDGE TTS STREAMING
    # ================================================================
    async def stream_speech(self, text: str):
        """Stream Edge TTS audio into FFplay."""

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )

        process = subprocess.Popen(
            [
                self.ffplay,
                "-nodisp",
                "-autoexit",
                "-loglevel",
                "error",
                "-i",
                "pipe:0",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio" and process.stdin:
                    process.stdin.write(chunk["data"])
                    process.stdin.flush()

        except BrokenPipeError:
            print("Audio player closed the stream.")

        except Exception as error:
            print(f"TTS streaming error: {error}")

        finally:
            try:
                if process.stdin:
                    process.stdin.close()
            except Exception:
                pass

            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    # ================================================================
    # SPEAK
    # ================================================================
    def speak(self, text: str):
        """Convert text into speech."""

        if not text or not text.strip():
            return

        try:
            asyncio.run(self.stream_speech(text.strip()))

        except Exception as error:
            print(f"Speech error: {error}")

    # ================================================================
    # PROCESS CALLER MESSAGE
    # ================================================================
    def process(self, user_text: str):
        """Send caller input to the existing AI agent."""

        if not user_text:
            return

        try:
            start = time.perf_counter()

            response = ask_agent(
                user_text,
                self.manager
            )

            elapsed = time.perf_counter() - start

            print(f"[Agent response: {elapsed:.2f}s]")

        except Exception as error:
            print(f"Agent error: {error}")

            response = (
                "I'm sorry, I had a temporary issue processing "
                "that request. Could you please say that again?"
            )

        if response:
            print(f"Agent: {response}")
            self.speak(response)

    # ================================================================
    # MAIN VOICE LOOP
    # ================================================================
    def run(self):
        print("=" * 60)
        print("Agentic AI Solutions - Voice Receptionist")
        print("=" * 60)

        self.speak(
            "Hello, welcome to Agentic AI Solutions. "
            "How may I assist you today?"
        )

        while True:
            try:
                user_text = self.listen()

                if not user_text:
                    continue

                text_lower = user_text.lower().strip()

                if text_lower in {
                    "goodbye",
                    "bye",
                    "exit",
                    "quit",
                    "stop",
                }:
                    self.speak(
                        "Thank you for contacting Agentic AI Solutions. "
                        "Have a wonderful day."
                    )
                    break

                self.process(user_text)

            except KeyboardInterrupt:
                print("\nVoice receptionist stopped.")
                break

            except Exception as error:
                print(f"Voice loop error: {error}")

                self.speak(
                    "I'm sorry, something went wrong. "
                    "Please try again."
                )


# ================================================================
# MAIN
# ================================================================
def main():
    try:
        receptionist = VoiceReceptionist()
        receptionist.run()

    except KeyboardInterrupt:
        print("\nExiting...")

    except Exception as error:
        print(f"Fatal error: {error}")


if __name__ == "__main__":
    main()