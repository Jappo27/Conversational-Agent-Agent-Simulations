import json
import os
import matplotlib.pyplot as plt
import numpy as np

def computeTurnAverages(dataset, minCount=20):
    turnScores = {}                 # turnIndex → list of [pragmatic, semantic]
    turnConversationCount = {}      # turnIndex → number of conversations reaching that turn

    for messages in dataset.values():
        for turnIndex, msg in enumerate(messages, start=0):

            turnConversationCount[turnIndex] = turnConversationCount.get(turnIndex, 0) + 1

            if isinstance(msg, list) and len(msg) >= 2:
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
    pragmaticStdDevs = []
    semanticStdDevs = []

    for turnIndex in sorted(turnScores.keys()):
        scores = np.array(turnScores[turnIndex])

        if len(scores) < minCount:
            continue

        pragmaticAvgScores.append(np.mean(scores[:, 0]))
        semanticAvgScores.append(np.mean(scores[:, 1]))

        pragmaticStdDevs.append(np.std(scores[:, 0]))
        semanticStdDevs.append(np.std(scores[:, 1]))

        turnIndices.append(turnIndex-1)

    return (
        turnIndices,
        pragmaticAvgScores,
        semanticAvgScores,
        pragmaticStdDevs,
        semanticStdDevs
    )

def load_json_from_user(prompt):
    while True:
        # Get minimum count and validate it is an integer >= 0
        try:
            Min = int(input("Enter the minimum amount of data points per turn: ").strip())
            if Min < 0:
                print("Minimum must be a non-negative integer.")
                continue
        except ValueError:
            print("Please enter a valid integer for the minimum.")
            continue

        # Get file path
        path = input(prompt).strip()

        # Validate file exists
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f), Min, os.path.basename(path)
        else:
            print(f"File not found: {path}. Try again.")

baseData, baseMin, base_name = load_json_from_user("Enter path to base dataset: ")
compareData, compareMin, compare_name = load_json_from_user("Enter path to comparison dataset: ")

(
    turns,
    pragmaticAvgScores,
    semanticAvgScores,
    pragmaticStdDevs,
    semanticStdDevs
) = computeTurnAverages(baseData, minCount=baseMin)

(
    compareTurns,
    comparePragmaticAvgScores,
    compareSemanticAvgScores,
    comparePragmaticStdDevs,
    compareSemanticStdDevs
) = computeTurnAverages(compareData, minCount=compareMin)


compareTurns = list(range(len(comparePragmaticAvgScores)))
shared_turns = sorted(set(turns).intersection(compareTurns))

# Filter base
turns_f = [t for t in turns if t in shared_turns]
pragmaticAvgScores_f = [prag for t, prag in zip(turns, pragmaticAvgScores) if t in shared_turns]
semanticAvgScores_f = [sem for t, sem in zip(turns, semanticAvgScores) if t in shared_turns]
pragmaticStdDevs_f = [std for t, std in zip(turns, pragmaticStdDevs) if t in shared_turns]
semanticStdDevs_f = [std for t, std in zip(turns, semanticStdDevs) if t in shared_turns]

# Filter compare
comparePragmaticAvgScores_f = [comparePragmaticAvgScores[t] for t in shared_turns]
compareSemanticAvgScores_f = [compareSemanticAvgScores[t] for t in shared_turns]
comparePragmaticStdDevs_f = [std for t, std in zip(turns, pragmaticStdDevs) if t in shared_turns]
compareSemanticStdDevs_f = [std for t, std in zip(turns, semanticStdDevs) if t in shared_turns]

# --- PRAGMATIC PLOT ---
plt.figure(figsize=(10, 6))

# Baseline with error bars
plt.errorbar(
    turns_f, pragmaticAvgScores_f, yerr=pragmaticStdDevs_f,
    marker='o', capsize=4, label=f"{base_name} Coherence"
)

# Comparison with error bars
plt.errorbar(
    shared_turns, comparePragmaticAvgScores_f, yerr=comparePragmaticStdDevs_f,
    marker='o', capsize=4, label=f"{compare_name} Coherence"
)

# Trend line for baseline
prag_coeffs = np.polyfit(turns_f, pragmaticAvgScores_f, 1)
prag_trend = np.poly1d(prag_coeffs)
plt.plot(turns_f, prag_trend(turns_f), '--', color='red', label=f"{base_name} Trend")

# Trend line for comparison
comp_prag_coeffs = np.polyfit(shared_turns, comparePragmaticAvgScores_f, 1)
comp_prag_trend = np.poly1d(comp_prag_coeffs)
plt.plot(shared_turns, comp_prag_trend(shared_turns), '--', color='orange', label=f"{compare_name} Trend")

# Axes + labels
ax = plt.gca()
ax.set_xticks(np.arange(min(turns_f), max(turns_f)+1, 1))
ax.set_xticks([], minor=True)

plt.xlabel("Turn Index")
plt.ylabel("Dialog-RPT Average Score")
plt.title("Dialog-RPT Average Score per Turn")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.ylim(0, 1)
plt.show()


# --- SEMANTIC PLOT ---
plt.figure(figsize=(10, 6))

# Baseline with error bars
plt.errorbar(
    turns_f, semanticAvgScores_f, yerr=semanticStdDevs_f,
    marker='o', capsize=4, label=f"{base_name} Semantic"
)

# Comparison with error bars
plt.errorbar(
    shared_turns, compareSemanticAvgScores_f, yerr=compareSemanticStdDevs_f,
    marker='o', capsize=4, label=f"{compare_name} Semantic"
)

# Trend line for baseline
sem_coeffs = np.polyfit(turns_f, semanticAvgScores_f, 1)
sem_trend = np.poly1d(sem_coeffs)
plt.plot(turns_f, sem_trend(turns_f), '--', color='red', label=f"{base_name} Trend")

# Trend line for comparison
comp_sem_coeffs = np.polyfit(shared_turns, compareSemanticAvgScores_f, 1)
comp_sem_trend = np.poly1d(comp_sem_coeffs)
plt.plot(shared_turns, comp_sem_trend(shared_turns), '--', color='orange', label=f"{compare_name} Trend")

# Axes + labels
ax = plt.gca()
ax.set_xticks(np.arange(min(turns_f), max(turns_f)+1, 1))
ax.set_xticks([], minor=True)

plt.xlabel("Turn Index")
plt.ylabel("SBERT Average Score")
plt.title("SBERT Average Score per Turn")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.ylim(0, 1)
plt.show()