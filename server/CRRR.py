from ollamaClass import ollamaClass 
from RAG.localrag import EstablishConnection, LoadVault, EmbedVault, VaultEmbed, ollama_chat
from RAG.FileUpload import convert_pdf_to_text, upload_txtfile, upload_jsonfile
import json, os
from write import writeConvo, addConvo, writeReflexion
from datetime import datetime

def generateAgentText(profile, ConvoNum, task, vault, base_dir, output_dir, IGoutput_dir, ReflexVaultPath, modelNum, counter, Conversation = [], reflexCount = 5):
    LLMOutput = []
    
    model = ollamaClass(profile["modelName"])
    model.jsonExtract(profile)
    client = EstablishConnection(model.modelName)
    prompt = model.getPrompt()
    
    count = 0
    while count <= reflexCount:
        model.updateContent(prompt)
        vault_content_model = LoadVault(vault)
        vault_embeddings_model = EmbedVault(vault_content_model)
        vault_embeddings_tensor_model = VaultEmbed(vault_embeddings_model)
        
        rewritten_query, relevant_context, thinkning, response = ollama_chat(vault_embeddings_tensor_model, vault_content_model, profile, Conversation, client, model)
        writeConvo({"ID": datetime.now().strftime("%Y%m%d%H%M%S%f"), "Response": response, "Thiking": thinkning }, output_dir, f"{IGoutput_dir}/{modelNum}/Initial/InitGen-{ConvoNum}{counter}{count}.json")
        
        ReflexVault = LoadVault(ReflexVaultPath)
        ReflexVaultEmbeddings = EmbedVault(ReflexVault)
        ReflexVaultEmbeddingsTensor = VaultEmbed(ReflexVaultEmbeddings)
        
        model.updateContent(f"""You are an evaluator that determines whether a model's RESPONSE Follows a valid line of thinking.
                                You are given:
                                - THINKING: {thinkning}
                                - RESPONSE: {response}

                                Your job is to decide whether this RESPONSE:
                                1. A valid continuation of the THINKING.

                                Return ONLY one word:
                                - "True"  → if BOTH conditions are satisfied.
                                - "False" → otherwise.

                                Evaluation criteria:

                                A. Validity (must satisfy ALL):
                                - The RESPONSE logically follows from the THINKING.
                                - The RESPONSE is entailed by the reasoning chain.
                                - The RESPONSE is not contradictory, irrelevant, or random.

                                Reject (return "False") if:
                                - The RESPONSE is only useful for this specific example.
                                - The RESPONSE is trivial, obvious, or redundant.
                                - The RESPONSE does not improve future reasoning.
                                - The RESPONSE is too narrow, too contextual, or too noisy.

                                Return ONLY "True" or "False".""")
        model.generateResponse()
        Action = model.getResponseMessage()["content"]
        
        model.updateContent(f"""You are an evaluator that determines whether a model's RESPONSE should be added to a long-term Reflexion database.
                                You are given:
                                - THINKING: {thinkning}
                                - RESPONSE: {response}

                                Your job is to decide whether this RESPONSE is both:
                                1. A valid continuation of the THINKING, and
                                2. Valuable enough to store as a long-term Reflexion.

                                Return ONLY one word:
                                - "True"  → if BOTH conditions are satisfied.
                                - "False" → otherwise.

                                Evaluation criteria:

                                A. Validity (must satisfy ALL):
                                - The RESPONSE logically follows from the THINKING.
                                - The RESPONSE is entailed by the reasoning chain.
                                - The RESPONSE is not contradictory, irrelevant, or random.

                                B. Long-term value (must satisfy AT LEAST ONE):
                                - The RESPONSE expresses a generalizable principle or pattern.
                                - The RESPONSE corrects a reasoning error in a reusable way.
                                - The RESPONSE provides an insight that would improve future reasoning tasks.
                                - The RESPONSE identifies a failure mode or success pattern that is not instance-specific.
                                - The RESPONSE is concise, non-noisy, and not tied to ephemeral context.

                                Reject (return "False") if:
                                - The RESPONSE is only useful for this specific example.
                                - The RESPONSE is trivial, obvious, or redundant.
                                - The RESPONSE does not improve future reasoning.
                                - The RESPONSE is too narrow, too contextual, or too noisy.

                                Return ONLY "True" or "False".
                                """)
        model.generateResponse()
        Addition = model.getResponseMessage()["content"]
        
        if "True" in Addition:
            writeReflexion({"Task": task, "Response": response, "Thinkning": thinkning}, (os.path.normpath(os.path.join(base_dir, f"RAG/model{modelNum}Reflexion.txt"))))
            
        if "True" in Action:
            ReflexPrompt = f"""
            You are performing Reflexion-style iterative refinement. 
            Given the baseline response below, produce an improved version by:
            - Identifying weaknesses, gaps, or unclear reasoning
            - Preserving correct and valuable content
            - Incorporating useful insights from earlier attempts
            - Enhancing clarity, structure, and depth
            - Ensuring the final answer is more accurate, coherent, and helpful

            Baseline response:
            {response}
            
            Baseline Thinking:
            {thinkning}
            
            Baseline Action:
            {Action}

            Now produce a refined response that meaningfully improves upon it.
            """
            model.updateContent(ReflexPrompt)
            Reflexrewritten_query, Reflexrelevant_context, ReflexThinkning, ReflexResponse = ollama_chat(ReflexVaultEmbeddingsTensor, ReflexVault, profile, [], client, model)
            writeConvo({"ID": datetime.now().strftime("%Y%m%d%H%M%S%f"), "Response": ReflexResponse, "Thiking": ReflexThinkning }, output_dir, f"{IGoutput_dir}/{modelNum}/Reflex/ReflexGen-{ConvoNum}{counter}{count}.json") 
            
            
            model.updateContent(f"""
            Rewrite the content of {ReflexResponse} by removing any chain‑of‑thought, internal reasoning, or step‑by‑step explanations. 
            Preserve:
            • the final conclusions  
            • all factual statements  
            • the user‑visible meaning  

            Do not add new information. Do not change the final answer. Only remove reasoning traces.
            """)
            model.generateResponse()
            cotFreeResponse = model.getResponseMessage()["content"]
            writeConvo({"ID": datetime.now().strftime("%Y%m%d%H%M%S%f"), "Response": cotFreeResponse, "Action": Action}, output_dir, f"{IGoutput_dir}/{modelNum}/Final/FinalRes-{ConvoNum}{counter}{count}.json") 
            
            return cotFreeResponse, thinkning
        
        else:
            LLMOutput.append([response, thinkning])
            count += 1
            
    curBest = 0
    curBestPos = 0
    for i, (cotFreeResponse, thinkning) in enumerate(LLMOutput):
        model.updateContent(f"Evaluate the quality of the response {cotFreeResponse} and the reasoning process (ReflexThinking). Return ONLY a number from 1–100 with no explanation.")
        model.generateResponse()
        Score = model.getResponseMessage()["content"]
        try:
            if int(Score) > curBest:
                curBest = Score
                curBestPos = i
        except Exception as e:
            print(e)
                
    writeConvo({"ID": datetime.now().strftime("%Y%m%d%H%M%S%f"), "Response": LLMOutput[curBestPos][0], "Thiking": LLMOutput[curBestPos][1] }, output_dir, f"{IGoutput_dir}/{modelNum}/ReflexGen-{counter}{count}") 
    return LLMOutput[curBestPos][0], LLMOutput[curBestPos][1]
