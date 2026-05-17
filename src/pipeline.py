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

    def run(self) -> os.PathLike:
        """Orchestrates the end-to-end data processing workflow."""
        sources = self.config_loader.load_sources()
        if not sources:
            raise ValueError("No target sources found in configuration.")

        raw_data = self.ingestion_engine.fetch_all_feeds(sources)
        if not raw_data.strip():
            raise ValueError("No data scraped from specified network target channels.")

        print("\n🤖 Invoking AI Editorial Agent...")
        digest_content = self.editorial_engine.generate_digest(raw_data)
        
        saved_path = self._persist_to_disk(digest_content)
        return saved_path