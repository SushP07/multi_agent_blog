import feedparser
from datetime import date, timedelta
from dateutil import parser
from typing import Dict

class RSSIngestionEngine:
    def __init__(self, limit_per_source: int = 5):
        self.limit = limit_per_source

    def fetch_all_feeds(self, sources: Dict[str, str]) -> str:
        """Iterates through feeds and pulls articles published strictly on the previous day."""
        aggregated_payload = ""
        
        # Calculate yesterday's date target (e.g., if today is May 17, target is May 16)
        yesterday = date.today() - timedelta(days=1)
        print(f"📅 Filtering for updates published strictly on: {yesterday}")
        
        for channel_name, feed_url in sources.items():
            print(f"📡 Ingesting from [{channel_name}]: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"⚠️ Warning: Feed empty or unreachable for {channel_name}")
                continue

            count = 0
            for entry in feed.entries:
                # Enforce the scan limit boundary per source
                if count >= self.limit:
                    break
                
                # Extract publication or updated timestamp tags
                pub_date_str = entry.get("published", entry.get("updated", None))
                if not pub_date_str:
                    continue
                
                try:
                    # Parse the timestamp string and normalize it to a date object
                    article_date = parser.parse(pub_date_str).date()
                    
                    # MATCHING ENGINE: Only compile if it matches yesterday's date
                    if article_date == yesterday:
                        title = entry.get("title", "No Title")
                        summary = entry.get("summary", "No Summary Available")
                        source_url = entry.get("link", "#")
                        
                        aggregated_payload += (
                            f"--- SOURCE: {channel_name} ---\n"
                            f"Title: {title}\n"
                            f"URL: {source_url}\n"
                            f"Summary: {summary}\n\n"
                        )
                        count += 1
                        
                except Exception as e:
                    print(f"❌ Failed to parse date string '{pub_date_str}': {e}")
                    continue
                    
        return aggregated_payload