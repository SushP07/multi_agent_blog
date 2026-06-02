import os
import time
import json
from agno.agent import Agent
from agno.models.google import Gemini

class AIEditorialEngine:
    def __init__(self):
        if not os.environ.get("GOOGLE_API_KEY"):
            raise PermissionError("Execution halted: GOOGLE_API_KEY environment variable is missing.")
            
        self.agent = Agent(
            name="Macro Sentiment Research Editor",
            role="Filter raw scraped engineering/macro feeds and compile a high-signal technical digest.",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=[
                "You are an expert financial market intelligence editor.",
                "Extract breakthroughs, architectural updates, and macro sentiment from the raw feed text.",
                "Strictly group findings by source channel and keep descriptions dense and developer-centric.",
                "Always preserve and append the original source hyperlinks to the end of every technical insight."
            ]
        )

    def generate_digest(self, raw_data_payload: str) -> str:
        """Dispatches data payloads to the LLM with built-in exponential backoff resilience."""
        max_retries = 3
        initial_delay = 4  # seconds

        for attempt in range(max_retries):
            try:
                response = self.agent.run(raw_data_payload)
                
                # Structural check: If the API returned a successful text block containing a 503 error string
                if "503" in response.content or "experiencing high demand" in response.content:
                    raise IOError("Gemini API overloaded (503 Service Unavailable).")
                    
                return response.content

            except Exception as e:
                # If we have remaining attempts, calculate the backoff delay
                if attempt < max_retries - 1:
                    sleep_time = initial_delay * (2 ** attempt)  # Delays: 4s, then 8s
                    print(f"⚠️ API Warning: {e}. Retrying execution pass in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    # Out of attempts: Return a clean engineering fallback message instead of breaking the file
                    print("❌ API Error: Max resilience thresholds exhausted.")
                    return f"## Data Processing Hold\n\nUnable to complete AI sentiment extraction today due to temporary upstream upstream service limits.\n\n### Raw Source Payload Status\n- Total Ingested Items Available: Valid\n- Upstream Error Log: {str(e)}"