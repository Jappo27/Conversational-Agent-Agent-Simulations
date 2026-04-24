import json
import os
from scipy.stats import ttest_1samp, f, t
import numpy as np
import matplotlib.pyplot as plt

def computeTurnAverages(dataset, minCount=0):
    turnScores = {}
    turnConversationCount = {}

    for messages in dataset.values():
        for turnIndex, msg in enumerate(messages, start=0):
            turnConversationCount[turnIndex] = turnConversationCount.get(turnIndex, 0) + 1
            if isinstance(msg, list) and len(msg) >= 2:
                score = msg[:2]
            else:
                continue
            if score is None or len(score) != 2 or any(s is None for s in score):
                continue
            turnScores.setdefault(turnIndex, []).append(score)

    turnIndices = []
    pragmaticScores = []
    semanticScores = []

    for turnIndex in sorted(turnScores.keys()):
        scores = np.array(turnScores[turnIndex])
        if len(scores) < minCount:
            continue
        pragmaticScores.append(scores[:, 0])
        semanticScores.append(scores[:, 1])
        turnIndices.append(turnIndex - 1)

    return turnIndices, pragmaticScores, semanticScores

def calcOTTestConversation(baseAvgScores, comparisonAvgScores):
    sharedTurns = min(len(baseAvgScores), len(comparisonAvgScores))
    tList = []
    pList = []
    dfList = []
    for i in range(sharedTurns):
        a = np.array(comparisonAvgScores[i], dtype=float)
        popMean = np.mean(baseAvgScores[i])
        tStatistic, pValue = ttest_1samp(a, popMean, nan_policy='raise')
        df = len(a) - 1
        tList.append(tStatistic)
        pList.append(pValue)
        dfList.append(df)
    return tList, pList, dfList

def loadJsonFromUser(prompt):
    while True:
        try:
            minVal = int(input("Enter the minimum amount of data points per turn: ").strip())
            if minVal < 0:
                print("Minimum must be a non-negative integer.")
                continue
        except ValueError:
            print("Please enter a valid integer for the minimum.")
            continue
        path = input(prompt).strip()
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f), minVal, os.path.basename(path)
        else:
            print(f"File not found: {path}. Try again.")

def plotTTestResults(tStats, pValues, dfList, alpha=0.05):
    tStats = np.array(tStats, dtype=float)
    pValues = np.array(pValues, dtype=float)
    dfList = np.array(dfList, dtype=float)
    turns = np.arange(len(tStats))
    critVals = t.ppf(1 - alpha/2, dfList)
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax[0].plot(turns, tStats, marker='o', label="t-statistic", color="blue")
    ax[0].plot(turns, critVals, linestyle='--', color='red', label=f"+t_crit (α={alpha})")
    ax[0].plot(turns, -critVals, linestyle='--', color='red', label=f"-t_crit (α={alpha})")
    ax[0].axhline(0, color='black', linewidth=1)
    ax[0].set_ylabel("t-statistic")
    ax[0].set_title("Per-Turn One-Sample t-Test Results")
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)
    ax[1].plot(turns, pValues, marker='o', color="purple", label="p-value")
    ax[1].axhline(alpha, linestyle='--', color='red', label=f"α = {alpha}")
    ax[1].set_xlabel("Turn Index")
    ax[1].set_ylabel("p-value")
    ax[1].set_yscale("log")
    ax[1].legend()
    ax[1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

baseData, baseMin, baseName = loadJsonFromUser("Enter path to base dataset: ")
compareData, compareMin, compareName = loadJsonFromUser("Enter path to comparison dataset: ")

turns, pragmaticAvgScores, semanticAvgScores = computeTurnAverages(baseData, minCount=baseMin)
compareTurns, comparePragmaticAvgScores, compareSemanticAvgScores = computeTurnAverages(compareData, minCount=compareMin)

pragmaticTList, pragmaticPList, pragmaticDfList = calcOTTestConversation(pragmaticAvgScores, comparePragmaticAvgScores)
plotTTestResults(pragmaticTList, pragmaticPList, pragmaticDfList)

semanticTList, semanticPList, semanticDfList = calcOTTestConversation(semanticAvgScores, compareSemanticAvgScores)
plotTTestResults(semanticTList, semanticPList, semanticDfList)
