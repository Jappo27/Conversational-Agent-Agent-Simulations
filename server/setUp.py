import os
import shutil
from fileUpload import convert_pdf_to_text, upload_txtfile, upload_jsonfile

def cleanseDir(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def cleanseFile(file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
    except Exception as e:
        print(f"Failed to clear {file_path}. Reason: {e}")
        
def RAGUpload(folderPath, fileDestination):
    for filename in os.listdir(folderPath):
        filePath = os.path.join(folderPath, filename)
        if not os.path.isfile(filePath):
            continue
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            convert_pdf_to_text(filePath, fileDestination)
        elif ext == "txt":
            upload_txtfile(filePath, fileDestination)
        elif ext == "json":
            upload_jsonfile(filePath, fileDestination)
        else:
            print(f"Skipping unsupported file: {filename}")

BASE = os.path.dirname(os.path.abspath(__file__))

def cleanseDefault():
    cleanseFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAG/model1Reflexion.txt"))
    cleanseFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAG/model2Reflexion.txt"))
    cleanseFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAG/modelVault1.txt"))
    cleanseFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAG/modelVault2.txt"))

    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VectorStore1"))
    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VectorStore2"))

    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Conversation"))
    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/1/Final"))
    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/2/Final"))

    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/1/Initial"))
    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/2/Initial"))

    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/1/Reflex"))
    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Governance/2/Reflex"))

    cleanseDir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput/Thinking"))
