import os
from datetime import datetime
from src.config_loader import ConfigLoader
from src.ingestion import RSSIngestionEngine
from src.editor import AIEditorialEngine

class DigestPipeline:
    def __init__(self, output_dir: str = "digests"):
        self.output_dir = output_dir
        self.config_loader = ConfigLoader()
        self.ingestion_engine = RSSIngestionEngine(digests_dir=output_dir)
        self.editorial_engine = AIEditorialEngine() # Instantiated as editorial_engine

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
        print("📁 Loading news source channels from JSON config...")
        # FIX 1: Route configuration extraction through the config_loader instance
        config_data = self.config_loader.load_sources()
        
        # Safe extraction handle regardless of whether sources.json maps a root list or dictionary wrapper
        sources = config_data.get("sources", []) if isinstance(config_data, dict) else config_data
        
        print("📡 Triggering self-healing adaptive gap scan...")
        raw_data = self.ingestion_engine.scrape_feeds(sources)

        if not raw_data:
            print("📅 No new articles found within the gap scan window today. Exiting smoothly.")
            return "No updates."

        print("🤖 Forwarding collected data delta to AI Editorial Engine...")
        # FIX 2: Corrected attribute call name from editor_engine to self.editorial_engine
        digest_content = self.editorial_engine.generate_digest(raw_data)
        
        print("💾 Persisting generated markdown intelligence brief to disk...")
        # FIX 3: Route saving handle through the existing _persist_to_disk method
        saved_path = self._persist_to_disk(digest_content)
        
        print(f"✅ Success! Daily brief compiled cleanly at: {saved_path}")
        return "Pipeline run executed successfully."