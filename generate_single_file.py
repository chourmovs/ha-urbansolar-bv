# generate_single_file.py

import os

OUTPUT_FILE = "combined_output.txt"
IGNORED_DIRS = {".git", ".github", "__pycache__", "venv", "node_modules"}
IGNORED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".exe", ".zip", ".tar", ".gz", ".7z"}

def should_ignore(file_path):
    for ignored_dir in IGNORED_DIRS:
        if f"/{ignored_dir}/" in file_path.replace("\\", "/"):
            return True
    if os.path.splitext(file_path)[1].lower() in IGNORED_EXTENSIONS:
        return True
    return False

def main():
    full_content = []

    for root, dirs, files in os.walk("."):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path.startswith("./" + OUTPUT_FILE):
                continue
            if should_ignore(full_path):
                continue
            relative_path = os.path.relpath(full_path, ".")
            full_content.append(f"\n\n---\n# {relative_path}\n---\n\n")
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    full_content.append(content)
            except Exception as e:
                full_content.append(f"[Erreur de lecture: {e}]\n")

    combined_text = ''.join(full_content)

    # Estimation simple : 1 token ≈ 4 caractères
    estimated_tokens = int(len(combined_text) / 4)

    combined_text += f"\n\n---\n# Estimation du nombre de tokens : {estimated_tokens} tokens\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
        output.write(combined_text)

if __name__ == "__main__":
    main()
