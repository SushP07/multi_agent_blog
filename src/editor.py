import os
from agno.agent import Agent
from agno.models.google import Gemini

class AIEditorialEngine:
    def __init__(self):
        self._validate_credentials()
        self.agent = Agent(
            name="AI Technical Editor",
            role="Filter corporate noise and summarize deep technical AI breakthroughs with source links.",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=[
                "You are a Senior MLOps and AI Software Engineer reviewing the latest lab updates.",
                "Extract high-signal technical data and delete marketing or corporate fluff.",
                "CRITICAL RULE: You must preserve the source URL provided for each article.",
                "Every single bullet point or technical breakthrough you mention MUST end with a clickable Markdown link pointing back to its original article.",
                "Format the link exactly like this: [Read Source](URL) or [OpenAI News](URL) depending on the channel name.",
                "Format the output in clean, scannable Markdown with three clear headings:",
                "   - ## 🚀 Critical Technical Breakthroughs",
                "   - ## 🛠️ Model & SDK Updates",
                "   - ## 💡 Engineering / MLOps Takeaways"
            ],
        )

    def _validate_credentials(self) -> None:
        if not os.environ.get("GOOGLE_API_KEY"):
            raise PermissionError("Environment execution failed: GOOGLE_API_KEY is not set.")

    def generate_digest(self, raw_data: str) -> str:
        response = self.agent.run(raw_data)
        return response.content