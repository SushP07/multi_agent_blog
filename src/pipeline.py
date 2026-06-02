import os
from datetime import datetime
from src.config_loader import ConfigLoader
from src.ingestion import RSSIngestionEngine
from src.editor import AIEditorialEngine

class DigestPipeline:
    def __init__(self, output_dir: str = "digests"):
        self.output_dir = output_dir
        self.config_loader = ConfigLoader()
        self.ingestion_engine = RSSIngestionEngine()
        self.editorial_engine = AIEditorialEngine()

    def _persist_to_disk(self, content: str) -> str:
        """Internal helper handling file persistence encapsulation."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        today_str = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.output_dir, f"{today_str}_daily_brief.md")
        meta_header = f"# Daily AI Research Digest\n*Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}*\n\n"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(meta_header + content)
        return file_path

    def run(self):
        """Orchestrates the ingestion, processing, and output generation."""
        # Load sources config data
        sources = self.load_sources()
        
        # --- FIXED ALIGNMENT LINE HERE ---
        # Update from fetch_all_feeds to scrape_feeds
        raw_data = self.ingestion_engine.scrape_feeds(sources)
        # ----------------------------------

        if not raw_data:
            print("📅 No new articles found within the gap scan window today. Exiting smoothly.")
            return "No updates."

        # Dispatch the payload cleanly down to your resilient editor engine
        print("🤖 Forwarding collected data to the AI Editorial Engine...")
        digest_content = self.editor_engine.generate_digest(raw_data)
        
        # Persist output to the digests folder
        self.save_output(digest_content)
        return "Pipeline run executed successfully."