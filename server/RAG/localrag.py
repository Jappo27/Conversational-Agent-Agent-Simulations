import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
from ollamaClass import ollamaClass

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Function to get relevant context from the vault based on user input
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input[:512])["embedding"]
    if  not input_embedding:  # Check if the tensor has any elements
        return []
    # Compute cosine similarity between the input and vault embeddings
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Adjust top_k if it's greater than the number of available scores
    top_k = min(top_k, len(cos_scores))
    # Sort the scores and get the top-k indices
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Get the corresponding context from the vault
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

def rewrite_query(user_input_json, conversation_history, ollama_model, client):
    user_input = json.loads(user_input_json)["Query"]
    prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
    The rewritten query should:
    
    - Include "Show your chain of thought"
    - Preserve the core intent and meaning of the original query
    - Expand and clarify the query to make it more specific and informative for retrieving relevant context
    - Avoid introducing new topics or queries that deviate from the original query
    - DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query
    
    Return ONLY the rewritten query text, without any additional formatting or explanations.
    
    Original query: [{user_input}]
    
    Rewritten query: 
    """
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})
   
def ollama_chat(vault_embeddings, vault_content, profile1, conversation_history, client, model):
    conversation_history.append({"role": "user", "content": profile1["prompt"]})
    
    if len(conversation_history) > 1:
        query_json = {
            "Query": profile1["prompt"],
            "Rewritten Query": ""
        }
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, profile1["modelName"], client)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
    else:
        rewritten_query = profile1["prompt"]
    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents:" + CYAN + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    user_input_with_context = profile1["prompt"]
    if relevant_context:
        user_input_with_context = profile1["prompt"] + "\n\nRelevant Context:\n" + context_str
    
    conversation_history[-1]["content"] = user_input_with_context
    
    model.updateContent(rewritten_query)
    model.generateResponse()
    response = model.getReseponse()
    
    conversation_history.append({"role": "assistant", "content": response["message"]["content"]})
    
    return rewritten_query, relevant_context, response["message"]["thinking"], response["message"]["content"]

def EstablishConnection(model):
    # Configuration for the Ollama API client
    print(NEON_GREEN + "Initializing Ollama API client..." + RESET_COLOR)
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key = model
    )
    return client

def LoadVault(path):
    #Load Vault contents
    print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
    vault_content = []
    
    if os.path.exists(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))):
        with open(os.path.join(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))), "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()
            
    return vault_content

def EmbedVault(vault_content):
    #Embed vault content
    print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)
    vault_embeddings = []
    for content in vault_content:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
        vault_embeddings.append(response["embedding"])
    return vault_embeddings

def VaultEmbed(vault_embeddings):
    # Convert to tensor and print embeddings
    print("Converting embeddings to tensor...")
    vault_embeddings_tensor = torch.tensor(vault_embeddings) 
    return vault_embeddings_tensor
