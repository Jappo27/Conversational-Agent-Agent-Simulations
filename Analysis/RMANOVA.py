import json
import os
import numpy as np
import pandas as pd
from statsmodels.stats.anova import AnovaRM
from scipy.stats import f


def extractTurnScores(dataset):
    pragDict = {}
    semDict = {}

    for convId, messages in dataset.items():
        pragScores = []
        semScores = []

        for msg in messages:
            if isinstance(msg, list) and len(msg) >= 2:
                p, s = msg[:2]
                if p is not None and s is not None:
                    pragScores.append(p)
                    semScores.append(s)

        pragDict[convId] = pragScores
        semDict[convId] = semScores

    return pragDict, semDict


def buildBalancedLongDf(scoreDict, minCount):
    turnCounts = {}
    for scores in scoreDict.values():
        for turnIndex in range(len(scores)):
            turnCounts[turnIndex] = turnCounts.get(turnIndex, 0) + 1

    validTurns = [t for t, c in turnCounts.items() if c >= minCount]
    if not validTurns:
        raise ValueError("No turns meet the minimum count requirement.")

    validConversations = [
        convId for convId, scores in scoreDict.items()
        if all(turn < len(scores) for turn in validTurns)
    ]

    if len(validConversations) < 2:
        raise ValueError("Not enough conversations have all required turns.")

    # Build long-format dataframe
    rows = []
    for convId in validConversations:
        scores = scoreDict[convId]
        for turnIndex in validTurns:
            rows.append({
                "subject": convId,
                "condition": turnIndex,
                "score": scores[turnIndex]
            })

    df = pd.DataFrame(rows)
    df["subject"] = df["subject"].astype("category")
    df["condition"] = df["condition"].astype("category")
    df["score"] = df["score"].astype(float)

    return df


def computeCriticalF(anovaResult, alpha=0.05):
    table = anovaResult.anova_table
    factorName = table.index[0]

    df1 = table.loc[factorName, "Num DF"]
    df2 = table.loc[factorName, "Den DF"]

    fCrit = f.ppf(1 - alpha, df1, df2)
    return df1, df2, fCrit


def calcRmanovaAcrossConversations(dataset, minCount):
    pragDict, semDict = extractTurnScores(dataset)

    pragDf = buildBalancedLongDf(pragDict, minCount)
    semDf = buildBalancedLongDf(semDict, minCount)

    pragAnova = AnovaRM(
        data=pragDf,
        depvar="score",
        subject="subject",
        within=["condition"]
    ).fit()

    semAnova = AnovaRM(
        data=semDf,
        depvar="score",
        subject="subject",
        within=["condition"]
    ).fit()

    return pragAnova, semAnova


def loadJsonFromUser(prompt):
    while True:
        try:
            minCount = int(input("Enter minimum number of conversations per turn: ").strip())
            if minCount <= 0:
                print("Minimum count must be positive.")
                continue
        except ValueError:
            print("Please enter a valid integer.")
            continue

        path = input(prompt).strip()
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f), minCount
        else:
            print(f"File not found: {path}. Try again.")


data, minCount = loadJsonFromUser("Enter path to conversation JSON: ")
anovaPrag, anovaSem = calcRmanovaAcrossConversations(data, minCount)

print("\n=== Pragmatic RM-ANOVA ===")
print(anovaPrag)
df1, df2, fCrit = computeCriticalF(anovaPrag)
print(f"\nPragmatic F-critical (α=0.05): df1={df1}, df2={df2}, Fcrit={fCrit:.4f}")

print("\n=== Semantic RM-ANOVA ===")
print(anovaSem)
df1, df2, fCrit = computeCriticalF(anovaSem)
print(f"\nSemantic F-critical (α=0.05): df1={df1}, df2={df2}, Fcrit={fCrit:.4f}")
