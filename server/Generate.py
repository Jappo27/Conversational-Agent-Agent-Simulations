import copy
import os
from ollamaClass import ollamaClass 
from RAG.localrag import EstablishConnection, LoadVault, EmbedVault, VaultEmbed, ollama_chat
from RAG.FileUpload import convert_pdf_to_text, upload_txtfile, upload_jsonfile
import json
from CRRR import generateAgentText
from write import writeConvo

def vaultFiles(path, destionation):
    files = []

    # Walk through all subdirectories
    for root, _, filenames in os.walk(path):
        for name in filenames:
            if name.lower().endswith(".json") or name.lower().endswith(".pdf") or name.lower().endswith(".PDF") or name.lower().endswith(".txt"):
                files.append(os.path.join(root, name))
                
    for file in files:
        if file.lower().endswith(".json"):
            upload_jsonfile(file, destionation)
        elif file.lower().endswith(".pdf") or file.lower().endswith(".PDF"):
            convert_pdf_to_text(file, destionation)
        elif file.lower().endswith(".txt"):
            upload_txtfile(file, destionation)
        else:
            print(f"Error in uploading {file}")


def conversate(ConvoNum, turns, reflexes, profile1, profile2):
    
    StartingProfile1 = profile1
    StartingProfile2 = profile2
    
    model1 = ollamaClass(profile1["modelName"])
    model2 = ollamaClass(profile2["modelName"])
    model1.jsonExtract(profile1)
    model2.jsonExtract(profile2)

    ModelVault1Path = "modelVault1.txt"
    ReflexVault1Path = "model1Reflexion.txt"

    ModelVault2Path = "modelVault2.txt"
    ReflexVault2Path = "model2Reflexion.txt"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "RAGOutput")
    IGoutput_dir = os.path.join(output_dir, "Governance")
    
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAGOutput"), exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(IGoutput_dir, exist_ok=True)

    
    writeConvo(model1.dictify(), output_dir, f"Model-1.json")
    writeConvo(model2.dictify(), output_dir, f"Model-2.json")
    
    vaultFiles("server/VectorStore1", "modelVault1.txt")
    vaultFiles("server/VectorStore2", "modelVault2.txt")
    
    for counter in range(ConvoNum):
        
        profile1 = copy.deepcopy(StartingProfile1)
        profile2 = copy.deepcopy(StartingProfile2)
        
        print(f"Generating Conversation {counter}")
        Agent1Task = profile1["prompt"]
        Agent2Task = profile2["prompt"]
        
        model1Conversation = []
        model2Conversation = []
        
        model1history = []
        model2history = []
        
        model1Thinking = []
        model2Thinking = []
        
        for i in range(turns):
            print(f"Generating Turn {i}")
            response, thinking = generateAgentText(profile1, counter, Agent1Task, ModelVault1Path, base_dir, output_dir, IGoutput_dir, ReflexVault1Path, 1, i, model2history, reflexes)
            model1Conversation.append(response)
            model1Thinking.append(thinking)
            profile2["prompt"] = f"""
                ### Task
                {Agent2Task}
                
                ### Histiory
                {zip(model1Conversation[-3:] if model1Conversation else "", model2Conversation[-3:] if model2Conversation else "")}

                ### Input
                {response}

                ### Instructions
                - Follow your assigned role.
                - Produce an output.
                - Do not rewrite or ignore the task.
                """
            
            response, thinking = generateAgentText(profile2, counter, Agent2Task, ModelVault2Path, base_dir, output_dir, IGoutput_dir, ReflexVault2Path, 2, i, model1history, reflexes)
            
            model2Conversation.append(response)
            model2Thinking.append(thinking)
            profile1["prompt"] = f"""
                ### Task
                {Agent1Task}
                
                ### Histiory
                {zip(model2Conversation[-3:] if model2Conversation else "", model1Conversation[-3:] if model1Conversation else "")}
                
                ### Input
                {response}

                ### Instructions
                - Follow your assigned role.
                - Produce an output.
                - Do not rewrite or ignore the task.
                """
        
        writeConvo({"model1": model1Conversation, "model2": model2Conversation}, output_dir, f"Conversation/Conversation-{counter}.json")
        writeConvo({"model1": model1Thinking, "model2": model2Thinking}, output_dir, f"Thinking/Thinking-{counter}.json")
        

ALLOWED_KEYS = {
    "modelName", "role", "prompt", "system", "suffix", "raw", "stream",
    "keepAlive", "images", "context", "seed", "temperature", "topK",
    "minP", "maxP", "stop", "numCTX", "numPredict", "format", 'options', 'tool_calls', 'response', 'model', 'template'
}

def validate_profile_json(data: dict):
    unknown = set(data.keys()) - ALLOWED_KEYS
    if unknown:
        raise ValueError(f"Invalid keys found in profile: {unknown}")
    return True


def loadUserJson(txt):
    while True:
        path = input(txt).strip()

        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)

            # Validate keys
            try:
                validate_profile_json(data)
            except Exception as e:
                print(f"Profile validation failed: {e}")
                continue

            filename = os.path.basename(path)
            return data, filename

        else:
            print(f"File not found: {path}. Try again.")
            
def validateParams(turns, ConvoNum, reflexes):
    params = {
        "turns": turns,
        "ConvoNum": ConvoNum,
        "reflexes": reflexes
    }

    for name, value in params.items():
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{name} must be greater than 0, got {value}")

    return True

def getInputFromUser(prompt_text):
    while True:
        value = input(prompt_text).strip()

        if not value.isdigit():
            print("Please enter a valid positive integer.")
            continue

        value = int(value)

        if value <= 0:
            print("Value must be greater than 0.")
            continue

        return value

profile1, filename = loadUserJson("Enter path to first agent profile: ")
profile2 , filename = loadUserJson("Enter path to second agent profile: ")
    

# --- Loop until valid ---
while True:
    turns = getInputFromUser("Enter number of turns: ")
    ConvoNum = getInputFromUser("Enter number of conversations: ")
    reflexes = getInputFromUser("Enter number of reflexions: ")

    try:
        validateParams(turns, ConvoNum, reflexes)
        print("Parameters accepted.")
        break
    except Exception as e:
        print(f"Invalid input: {e}")

conversate(ConvoNum, turns, reflexes, profile1, profile2)