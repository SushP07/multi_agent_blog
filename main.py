import sys
from src.pipeline import DigestPipeline

def main():
    print("🚀 Initializing Production AI Newsletter Agent Engine...")
    try:
        pipeline = DigestPipeline()
        output_file = pipeline.run()
        print(f"💾 Pipeline complete. Output saved to: {output_file}")
        
    except (FileNotFoundError, ValueError, PermissionError) as err:
        print(f"❌ Pipeline Execution Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unhandled System Failure: {e}", file=sys.stderr)
        sys.exit(5)

if __name__ == "__main__":
    main()