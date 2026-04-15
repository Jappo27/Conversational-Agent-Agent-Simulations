import os
import json
import re

def writeConvo(convo, output_dir, filename):
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w") as f:
        json.dump(convo, f, indent=4)
        
def addConvo(convo, output_dir, filename):
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "a") as f:
        json.dump(convo, f, indent=4)
        
        # Function to upload a JSON file and append to vault.txt
def writeReflexion(data, file_destination):
    if data:
        # Convert dict to JSON string
        text = json.dumps(data, ensure_ascii=False)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Split into sentences
        sentences = re.split(r'(?<=[.!?]) +', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 < 1000:
                current_chunk += (sentence + " ").strip()
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk)

        # Write chunks to file
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_destination)
        with open(output_path, "a", encoding="utf-8") as vault_file:
            for chunk in chunks:
                vault_file.write(chunk.strip() + "\n")

        print("JSON content appended to vault file, one chunk per line.")

