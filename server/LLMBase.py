from ollamaClass import ollamaClass 
from RAG.localrag import EstablishConnection, LoadVault, EmbedVault, VaultEmbed, ollama_chat
from RAG.FileUpload import convert_pdf_to_text, upload_txtfile, upload_jsonfile
import json, os
from write import writeConvo, addConvo, writeReflexion
from datetime import datetime

def generateAgentText(profile, vault, base_dir, output_dir, IGoutput_dir, ReflexVaultPath, modelNum, counter, Conversation = [], reflexCount = 5):
    LLMOutput = []
    
    model = ollamaClass(profile["modelName"])
    model.jsonExtract(profile)
    
    model.generateResponse()
    OutPut = model.getReseponse()
    
    response = OutPut["message"]["content"]
    thinking = OutPut["message"]["thinking"]
    
    return response, thinking
