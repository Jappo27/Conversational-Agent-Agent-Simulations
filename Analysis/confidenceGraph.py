import json
import os
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

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
        turnScores,
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
        path = r"C:\Users\jappo\OneDrive\Desktop\Conversational-Agent-Agent-Simulations\Analysis\DATA\BaseLLM.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f), Min, os.path.basename(path)
        else:
            print(f"File not found: {path}. Try again.")

baseData, baseMin, base_name = load_json_from_user("Enter path to base dataset: ")

(
    turns,
    turnScores,
    pragmaticAvgScores,
    semanticAvgScores,
    pragmaticStdDevs,
    semanticStdDevs
) = computeTurnAverages(baseData, minCount=baseMin)
