import json
import matplotlib.pyplot as plt
import numpy as np

def computeTurnAverages(dataset, minCount=20):
    turnScores = {}
    turnConversationCount = {}

    for messages in dataset.values():
        for turnIndex, msg in enumerate(messages, start=1):

            turnConversationCount[turnIndex] = turnConversationCount.get(turnIndex, 0) + 1

            if isinstance(msg, dict) and "score" in msg:
                score = msg["score"]
            elif isinstance(msg, list) and len(msg) >= 2:
                score = msg[:2]
            else:
                continue

            if (
                score is None
                or len(score) != 2
                or any(s is None for s in score)
            ):
                continue

            turnScores.setdefault(turnIndex, []).append(score)

    turnIndices = []
    pragmaticAvgScores = []
    semanticAvgScores = []

    for turnIndex in sorted(turnScores.keys()):
        scores = np.array(turnScores[turnIndex])

        if len(scores) < minCount:
            continue

        pragmaticAvgScores.append(np.mean(scores[:, 0]))
        semanticAvgScores.append(np.mean(scores[:, 1]))

        turnIndices.append(turnIndex-1)

    return (
        turnIndices,
        pragmaticAvgScores,
        semanticAvgScores
    )


paths = {
    "BaseLLM": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\BaseLLM.json",
    "PromptStruct": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\PromptStruct.json",
    "Rag": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\Rag.json",
    "ReAct": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\ReAct.json",
    "CRVR": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\CRRRMethodology.json",
    "CRVRS": r"C:\Users\jappo\OneDrive\Desktop\Dissertation\CRVRS.json"
}

datasets = {name: json.load(open(path, "r")) for name, path in paths.items()}

for name, data in datasets.items():
    trimmed = {}

    for convo_name, convo_turns in data.items():
        trimmed[convo_name] = convo_turns[:9]   # keep only first 5 turns

    datasets[name] = trimmed
    
colors = {
    "CRVRS": "tab:olive",
    "CRVR": "tab:purple",
    "ReAct": "tab:red",
    "Rag": "tab:green",
    "PromptStruct": "tab:orange",
    "BaseLLM": "tab:blue"
}

# raw pragmatic plot
plt.figure(figsize=(10, 6))

for name, data in datasets.items():
    turns, pragmaticAvgScores, semanticAvgScores = computeTurnAverages(data, minCount=0)
    plt.plot(turns, pragmaticAvgScores, marker='o', label=name, color=colors[name])

plt.xlabel("Turn Index")
plt.ylabel("Average Dialog-RPT Score")
plt.title("Dialog-RPT Average Score per Turn")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# raw semantic plot
plt.figure(figsize=(10, 6))

for name, data in datasets.items():
    turns, pragmaticAvgScores, semanticAvgScores = computeTurnAverages(data, minCount=0)
    plt.plot(turns, semanticAvgScores, marker='o', label=name, color=colors[name])

plt.xlabel("Turn Index")
plt.ylabel("Average SBERT Score")
plt.title("SBERT Average Score per Turn (Raw Data)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# trend pragmatic plot 
plt.figure(figsize=(10, 6))

for name, data in datasets.items():
    turns, pragmaticAvgScores, semanticAvgScores = computeTurnAverages(data, minCount=0)

    # Trend line only
    z = np.polyfit(turns[1:], pragmaticAvgScores[1:], 1)
    p = np.poly1d(z)
    plt.plot(turns, p(turns), linestyle='--', label=f"{name} Trend", color=colors[name])

plt.xlabel("Turn Index")
plt.ylabel("Average Dialog-RPT Score (Trend)")
plt.title("Dialog-RPT Average Score Trend Lines (All Methods)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Trend semantic plot
plt.figure(figsize=(10, 6))

for name, data in datasets.items():
    turns, pragmaticAvgScores, semanticAvgScores = computeTurnAverages(data, minCount=0)

    # Trend line only
    z = np.polyfit(turns, semanticAvgScores, 1)
    p = np.poly1d(z)
    plt.plot(turns, p(turns), linestyle='--', label=f"{name} Trend", color=colors[name])

plt.xlabel("Turn Index")
plt.ylabel("Average SBERT Score (Trend)")
plt.title("SBERT Average Score Trend Lines (All Methods)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
