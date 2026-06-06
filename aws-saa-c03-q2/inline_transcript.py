import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python inline_transcript.py <project_directory>")
        sys.exit(1)

    project_dir = sys.argv[1]
    transcript_path = os.path.join(project_dir, "transcript.json")
    index_path = os.path.join(project_dir, "index.html")

    if not os.path.exists(transcript_path):
        print(f"Error: transcript.json not found in {project_dir}")
        sys.exit(1)

    if not os.path.exists(index_path):
        print(f"Error: index.html not found in {project_dir}")
        sys.exit(1)

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    # Convert to minified JSON string
    transcript_str = json.dumps(transcript_data)

    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    placeholder = "/* TRANSCRIPT_PLACEHOLDER */"
    
    if placeholder in index_content:
        new_content = index_content.replace(placeholder, f"var TRANSCRIPT = {transcript_str};")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Success: Transcript successfully inlined!")
    elif "var TRANSCRIPT = " in index_content:
        # If already inlined, warn user
        print("Notice: var TRANSCRIPT is already inlined in index.html. Revert index.html first to re-run.")
    else:
        print("Error: Neither placeholder nor TRANSCRIPT array variable found in index.html")

if __name__ == "__main__":
    main()
