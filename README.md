# Conversational-Agent-Agent-Simulations

Psychologists often spend a significant portion of their time conducting interviews with subjects. When conducting surveys, human participants should be the gold standard when sourcing reliable information. However, when conducting these interviews, difficulties can occur as it can face a myriad of issues, such as long interview processes, thus limiting samples, issues with ethics, or a lack of participants. As agentic AI becomes more prevalent in society, we must understand how an AI will interact with individuals and other agentic AI. When interacting with others, the main considerations are both action and intention. These agents will then engage in agent-to-agent conversations to generate a large volume of synthetic data. The next step is to utilise Natural Language Processing (NLP) and compare the synthetic data with natural dyadic conversational data.

"Foresight is not about predicting the future, it's about minimizing surprise." — Karl Schroeder

## Requirements

### Required Downloads  
Before running the project, ensure the following dependencies are installed:

- **Python**
- https://www.python.org/downloads/release/python-3120/

- **IDE (VSC)**
  Recommended: https://code.visualstudio.com/
  
- **Ollama (Windows)**  
  https://ollama.com/download/windows  

- **React (Frontend Framework)**  
  https://react.dev/learn/installation
  
- **Node.js (Frontend Framework)**    
  https://nodejs.org/en

- **PrimeReact (UI Component Library)**  
  https://primereact.org/installation/  

### Python Dependencies  
To install all required Python packages, open a terminal in the project root and run:

```
pip install -r requirements.txt
npm install
npm install vite --save-dev
```

This installs all backend dependencies, including model clients, embedding libraries, PDF processing, and server utilities.

---

## Set Up

Ensure that LongPathsEnabled is enabled
https://www.youtube.com/watch?v=U_Imp2TQyQI&t=162s
(If you are using a University device you will need to contact IT services)

Navigate to the backend server directory and start the API:

```
cd server
python server.py
```

Once the server is running, your frontend can communicate with the backend, load agents, process RAG documents, and interact with your Ollama models.
# Utilisation

 # # Persona Design Tab
When the GUI loads, the Persona Design tab is the first screen you’ll see. This workspace allows you to create, edit, export, and import persona design fields that will ultimately form a structured persona.json file.
To begin defining a persona:
- Select Add Field.
- Import JSON
- Export JSON
  
These fields allow you to build flexible, reusable persona definitions that can be exported for later use or imported into new sessions.


<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/7f27c3da-a250-42c0-addf-b1d0188b5ae4" />

Add Field Options
The Add Field feature provides three input types, each designed for different kinds of data:
- Custom Field — A short, free‑text input for small custom parameters or single‑value entries.
- Text File Upload — Allows uploading a .txt file containing larger lists or long-form data. Ideal for bulk inputs.
- Boolean Field — A simple yes/no selector, also supporting a third state for Did Not State when no explicit choice is provided.
Use these field types to tailor data collection to the structure and size of the information you need.


<img width="1920" height="1033" alt="image" src="https://github.com/user-attachments/assets/715df014-8a62-4fb2-9e35-40dab2c8e619" />



Export JSON Option:
The Export JSON feature provides an easy method to quickly:
- save or duplicate persona templates


<img width="1920" height="1140" alt="ExportPersona" src="https://github.com/user-attachments/assets/d1d33ea2-ede8-4aa0-98b1-a28a38a2f8e2" />


Import JSON Option:
The Import JSON feature provides an easy method to quickly:
- upload previously designed templates
- upload previously designed persona templates


<img width="1920" height="1140" alt="uploadJSON" src="https://github.com/user-attachments/assets/1b847a9c-0162-4807-b0db-80cf5a755420" />

# # Agent Design Tab

This tab enables fully custom agent‑persona design. When the GUI loads, a persona sentence is automatically generated using the persona profiles created in the previous tabs.

If no persona sentence is available, the system will fall back to generating one using the gemma3:12b model. Ensure that this model is installed in your local Ollama environment to enable automatic persona synthesis.


<img width="1920" height="1548" alt="image" src="https://github.com/user-attachments/assets/c7eca702-07f1-4f1e-804b-df0393f4c37c" />

## Agent Configuration

Each agent is defined using a structured set of fields that mirror Ollama‑style model configuration concepts. These fields determine how the agent behaves, how it interprets instructions, and how it interacts within the wider system.

### **Model Select**  (Required)
Specifies the underlying Ollama model used to generate responses.  
This should match a model installed in your local Ollama environment (e.g., `gemma3:12b`, `llama3.1:8b`, `mistral:7b`).  
The selected model determines the agent’s reasoning ability, style, and performance.
Full list of models: [https://ollama.com/library, This project only utilises models that have the ability to return thinking ](https://ollama.com/search?c=thinking)

### **Role**  
Defines the high‑level behavioural identity of the agent.  
Options include:  
- `"System"`  
- `"User"`  
- `"Assistant"`  
- `"Tool"`  

This field acts similarly to the `role` concept in system‑prompting, guiding the agent’s overall persona and purpose.

### **Prompt**  
A short instruction describing how the agent should behave.  
This is equivalent to the **primary system prompt** in Ollama model definitions.  
Use this field to define tone, constraints, or behavioural rules. (In OllamaClass.py this is defined as m.prompt, and model.updateContent())
Example:  
> “You are a concise, technically accurate assistant specialising in agentic AI workflows.”

### **System**  
Extended system‑level instructions that shape the agent’s reasoning and output style.  
This is where you define deeper behavioural logic, multi‑step reasoning expectations, or domain‑specific constraints.  
In Ollama terms, this corresponds to the `system` block inside a model’s configuration.

### **Suffix**  
Optional text appended to the end of every prompt sent to the model.  


<img width="887" height="562" alt="image" src="https://github.com/user-attachments/assets/a310b842-5236-4444-8885-6a76919be420" />

## Agent Extras

These optional fields provide fine‑grained control over how the agent interacts with the model backend and how responses are delivered. They mirror advanced Ollama runtime parameters and allow you to tune performance, streaming behaviour, and context handling.

### **Stream**  
Enables or disables token‑streaming for the agent’s responses.  
When enabled, the model returns output incrementally as it is generated, improving responsiveness for long outputs or interactive workflows.

### **Raw**  
When true, returns the raw response from the model without any prompt templating
Useful for debugging, inspecting token behaviour, or building custom formatting layers on top of the model output.

Typical values:  
- `true` — return raw model output exactly as generated  
- `false` — apply normal formatting and cleanup  

### **KeepAlive**  
Specifies how long the model instance should remain active after a request.  
A longer keep‑alive reduces cold‑start latency when making repeated calls to the same model.

Examples:  
- `"5m"` — keep the model loaded for 5 minutes  
- `"0s"` — unload immediately after each request  

### **Image**  
Allows the agent to send an image as part of the request payload.  
This is used when working with multimodal models that support vision input.  
If no image is provided, this field remains empty.

### **Context**  
Defines the maximum context window (in tokens) available to the agent.  
This determines how much prior conversation or prompt history the model can retain.

Examples:  
- `2048` — standard context  
- `8192` or higher — extended‑context models

Warning: 
- If a model's context window is too low or the input to the model is too volumous the model is liable to crash.


<img width="887" height="562" alt="image" src="https://github.com/user-attachments/assets/3b7ccbc2-c5da-48b6-81de-89208ead7290" />

## Options

These fields control how the underlying model generates text. They correspond to common Ollama‑style sampling parameters and allow you to fine‑tune creativity, determinism, and output length.

### **Temperature**  
Controls randomness in the model’s output.  
Lower values make responses more deterministic; higher values increase creativity and variation.

Examples:  
- `0.0–0.3` — factual, stable, low‑variance  
- `0.7–1.0` — creative, exploratory  
- `>1.0` — highly random, less predictable  

### **Top K**  
Limits sampling to the top‑K most likely next tokens.  
A smaller K makes output more focused; a larger K increases diversity.

Examples:  
- `1` — greedy, deterministic  
- `100` — more open‑ended generation  

### **P (Top‑P)**  
Instead of selecting a fixed number of tokens (Top‑K), Top‑P selects from the smallest probability mass whose cumulative probability exceeds *P*.  
This allows dynamic control over diversity.

Examples:  
- `0.9` — balanced, natural language flow  
- `0.5` — more restrictive, precise  
- `0.95+` — more creative  

### **Seed**  
Sets a deterministic seed for reproducible outputs.  
If the same prompt, model, and seed are used, the model will generate identical text.

Examples:  
- `12345` — fixed reproducible seed  
- `null` — fully random generation  

### **Num Ctx**  
Defines the maximum context window (in tokens) available to the model.  
This determines how much conversation history or prompt content the model can retain.

Examples:  
- `2048` — standard context  
- `4096–8192` — extended context  

### **Num Predict**  
Sets the maximum number of tokens the model is allowed to generate in its response.

Examples:  
- `128` — short, concise answers  
- `512` — medium‑length responses  
- `2048+` — long‑form generation  

### **Stop**  
Defines one or more stop sequences that immediately end generation when encountered.  
Useful for enforcing structured output, JSON boundaries, or multi‑agent turn‑taking.


<img width="550" height="597" alt="image" src="https://github.com/user-attachments/assets/4add6c98-573d-43a9-b48a-7bb90a96659f" />

Export JSON Option:
The Export JSON feature provides an easy method to quickly:
- save or duplicate Agent templates

Import JSON Option:
The Import JSON feature provides an easy method to quickly:
- upload previously designed templates
- upload previously designed Agent templates

(The Agent Template is fully portable and can be injected into any OllamaClass.py implementation.)


<img width="930" height="153" alt="image" src="https://github.com/user-attachments/assets/9cd679a9-0f3b-4729-b489-d51e8a0cec52" />

### RAG PDF Upload
The system supports uploading PDF documents for use in Retrieval‑Augmented Generation (RAG) workflows. These PDFs are ingested, chunked, and embedded so that agents can reference them during reasoning and response generation.

<img width="930" height="562" alt="image" src="https://github.com/user-attachments/assets/9ad707ed-8954-4954-8979-348a408bb589" />
<img width="1852" height="80" alt="image" src="https://github.com/user-attachments/assets/b5b7fd6b-86bd-403e-a0fe-3e519a893914" />

### Conversation 

If the Agent Profile Template contains missing fields, invalid values, or malformed configuration data, the system will return a clear error message describing the error.

<img width="960" height="181" alt="image" src="https://github.com/user-attachments/assets/33ceb64b-fdb5-4667-a91f-e69a2a2c0c14" />

### Generation Details

Generattion Details:
- Conversations - How many conversations are to be generated
- Turns - How many turns occour in the dyadic conversation generation
- Reflects - How many times a model can reject an utterance

  
<img width="1920" height="1488" alt="image" src="https://github.com/user-attachments/assets/43c43b7c-7cd4-4723-b863-33087309e10e" />

- Press Ctrl+C in the terminal to stop the server.

After submitting a JSON configuration, all existing files are automatically replaced with the new profiles and parameters.

Run generate.py to execute the full generation pipeline.

The system is built using the CRRR architecture (Constrained Prompting → Retrieval → Reflection → Reflexion).
<img width="3000" height="4000" alt="Generate" src="https://github.com/user-attachments/assets/25858361-0ebc-42bb-93b9-5e9948b1993c" />

## Governance:

Every time an agent produces a component of its final response—whether it’s a retrieved context block, a reflexion pass, or a final utterance—the system stores that output as a generation ticket. These tickets provide a complete audit trail of how the agent constructed its answer.

Path = Server -> RAGOutput -> Gen

## Analysis

### Formating of Generated Conversations

Running Analysis.py
Analysis.py supports two input modes:

Synthetic corpora generated by the system

Natural corpora loaded as a ConvoKit dataset

Follow the instructions below depending on your workflow.

# Using synthetically generated corpora
If your corpus was generated by the system:

Run Analysis.py normally.

When prompted, paste the path to the folder containing your synthetic corpus JSON files.

No code changes are required.

# Using a ConvoKit corpus
If you want to analyse a ConvoKit dataset instead of synthetic data:

Open Analysis.py

Comment out lines 171–178, which handle synthetic‑corpus directory loading.

Add your ConvoKit corpus download (e.g., Corpus(filename=...) or download("corpus-name")) on line 178.

Unindent lines 179–180 so they execute directly when using a ConvoKit corpus.

This switches the pipeline from directory‑based synthetic loading to ConvoKit’s native corpus format.

### Comparison of Generated Conversations to a baseline

Run compareGraph.py

1. When prompted for the baseline:
   - Enter the minimum data points per turn
   - Paste the path to the baseline dataset

2. When prompted for the comparison:
   - Enter the minimum data points per turn
   - Paste the path to the comparison dataset
   - 
### ANOVA TEST

Run ANOVA.py

1. When prompted for the baseline:
   - Enter the minimum data points per turn
   - Paste the path to the baseline dataset

2. When prompted for the comparison:
   - Enter the minimum data points per turn
   - Paste the path to the comparison dataset

# Citation and Terms of Use

When generating synthetic data for psychological research, several ethical considerations must be addressed. The persona‑design process within the proposed system enables researchers to approximate the demographics and characteristics of real interviewees, allowing the tool to function as a proxy for natural interviews. To ensure this practice remains ethically sound, three guidelines are recommended:

1. **Declaration of Use.**  
   Any use of synthetic conversations must be explicitly disclosed. Clear declaration ensures that other researchers can accurately interpret the methodological choices and understand that synthetic data contributed to the reported findings.

2. **Data Storage and Transparency.**  
   Where appropriate, synthetic data should be stored separately from natural data and made publicly accessible. This separation allows independent verification, supports reproducibility, and prevents unintentional conflation of synthetic and natural corpora.

3. **Threshold of Natural Data.**  
   Synthetic data should only be introduced after a meaningful quantity of natural interviews has been collected. The system is intended to supplement not replace human generated data. Maintaining a threshold helps preserve ecological validity and prevents over‑reliance on synthetic corpora.

Together, these guidelines promote transparency, reproducibility, and responsible use of synthetic conversational data in psychological research.

---

**CC BY‑NC‑SA License**

This work is released under the *Creative Commons Attribution–NonCommercial–ShareAlike* license. This license permits redistribution, adaptation, and non‑commercial use, provided that appropriate attribution is given and any derivative works are distributed under the same license.

**Restrictions:**  
Users may not employ automated systems—including scrapers or AI models—to extract, analyse, or otherwise process this repository or its contents.

**Acceptance:**  
By downloading, installing, or using this software, you acknowledge and accept these terms.
