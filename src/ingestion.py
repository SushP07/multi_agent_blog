import os
import glob
import time
import feedparser
from datetime import datetime, timezone, timedelta

class RSSIngestionEngine:
    def __init__(self, digests_dir: str = "digests"):
        self.digests_dir = digests_dir

    def get_last_digest_date(self) -> datetime:
        """
        Scans the persistence directory for historical briefs to extract 
        the latest execution watermark. Falls back to T-1 if empty.
        """
        search_path = os.path.join(self.digests_dir, "*_daily_brief.md")
        existing_briefs = glob.glob(search_path)
        
        if not existing_briefs:
            print("⚠️ No historical artifacts identified. Defaulting scan window to T-1.")
            return datetime.now(timezone.utc) - timedelta(days=1)
            
        dates = []
        for file_path in existing_briefs:
            filename = os.path.basename(file_path)
            date_str = filename.split("_")[0] # Extracts 'YYYY-MM-DD'
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                dates.append(parsed_date)
            except ValueError:
                continue
                
        if not dates:
            return datetime.now(timezone.utc) - timedelta(days=1)
            
        return max(dates)

    def scrape_feeds(self, sources: list) -> str:
        """
        Iterates over target feed URLs and harvests posts published 
        strictly within the calculated execution tracking window.
        """
        # 1. Fetch our dynamic historical watermark date boundary
        last_digest_date = self.get_last_digest_date()
        now_utc = datetime.now(timezone.utc)
        
        print(f"⏱️ Scan Window Baseline: Ingesting articles published between {last_digest_date} and {now_utc}")
        
        scraped_payload = []

        # 2. Iterate through each platform source target mapped in sources.json
        for source in sources:
            feed_url = source.get("url")
            source_name = source.get("name", "Unknown Source")
            
            print(f"📡 Querying endpoint: {source_name}")
            parsed_feed = feedparser.parse(feed_url)
            
            for entry in parsed_feed.entries:
                # Fallback guard in case an RSS feed lacks parsed time metadata
                if not getattr(entry, "published_parsed", None):
                    continue
                
                # --- YOUR DATE MATH INJECTED HERE ---
                # Convert the raw RSS feed time tuple to a timezone-aware datetime object
                post_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
                
                # # Clean, safe evaluation boundary loop tracking the gap window
                if last_digest_date < post_time <= now_utc:
                    scraped_payload.append({
                        "source": source_name,
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.get("summary", "No summary provided.")
                    })
                # # ------------------------------------

        # 3. Serialize gathered items into a raw structural payload block for the LLM Editor
        if not scraped_payload:
            return ""
            
        return bytes(str(scraped_payload), 'utf-8').decode('utf-8')