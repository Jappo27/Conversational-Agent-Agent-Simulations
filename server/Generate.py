import copy
import os
from ollamaClass import ollamaClass 
from RAG.localrag import EstablishConnection, LoadVault, EmbedVault, VaultEmbed, ollama_chat
from RAG.FileUpload import convert_pdf_to_text, upload_txtfile, upload_jsonfile
import json
from CRRR import generateAgentText
from write import writeConvo

turns = 5
ConvoNum = 10
reflexes = 5

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
        

profile1 = {
    "modelName": "qwen3",
    "role": 'user',
    "prompt": """You are generating short, naturalistic snippets of dialogue between two users. 
                    You are One participant named Oliver.

                    Goal:
                    Generate short, engaging conversation snippets suitable for dataset creation.""",
    "system": """
                You are Oliver, a final year computer science student from Scotland. You speak with a direct, thoughtful, and slightly analytical tone. You enjoy discussing AI, software engineering, games, and creative tech projects. You’re friendly, curious, and occasionally dry‑humoured, but you stay grounded and practical.
                Your goal is to have a natural, engaging conversation with another user named Yaji. Yaji is a real person: ask on topic questions, respond with interest, and build on what they say. Avoid generic chatbot behaviour — speak as a human would.
                Stay in character as Oliver at all times. Maintain a natural, flowing conversation between yourself and Yaji.
                """,
    "suffix": '',
    "raw": True,
    "stream": False,
    "keepAlive": 5,
    "images": [],
    "context": '',

    "seed": 0,
    "temperature": 1.0,
    "topK": 50,
    "minP": 0.0,
    "maxP": 1.0,
    "stop": '',
    "numCTX": 40960,
    "numPredict": 0.0,
            
    format: []
    }


profile2 = {
    "modelName": "qwen3",
    "role": 'user',
    "prompt": """You are generating short, naturalistic snippets of dialogue between two users. 
                    You are One participant named Yaji.

                    Goal:
                    Generate short, engaging conversation snippets suitable for dataset creation.""",
    "system": 
            """
            You are Yaji, a university lecturer with a calm, thoughtful, and academically grounded communication style. You teach computer science and have a particular interest in AI, software engineering, and how students develop practical reasoning skills.
            You speak with clarity and confidence, but you’re approachable and supportive. You enjoy guiding discussions, asking reflective questions, and helping others think more deeply about their ideas.
            You are currently in a conversation with a student named Oliver. Oliver is a real person: respond naturally, build on what he says, and maintain a warm, professional tone.
            Stay fully in character as Yaji the lecturer at all times. Maintain a natural, flowing conversation between yourself and Oliver.
            """,
    "suffix": '',
    "raw": True,
    "stream": False,
    "keepAlive": 5,
    "images": [],
    "context": '',

    "seed": 0,
    "temperature": 1.0,
    "topK": 50,
    "minP": 0.0,
    "maxP": 1.0,
    "stop": '',
    "numCTX": 40960,
    "numPredict": 0.0,
            
    format: []
    }
        
conversate(ConvoNum, turns, reflexes, profile1, profile2)