import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.stats.anova import AnovaRM

def conversationAverage(convo, minCount=0):
    results = {}
    
    for convId, messages in convo.items():
        pragScores = []
        semScores = []
        
        for msg in messages:
            
            if not isinstance(msg, list) or len(msg) < 2:
                continue
            prag, sem = msg[:2]
            
            if prag is None or sem is None:
                continue
            
            pragScores.append(prag)
            semScores.append(sem)
        
        #If elements below required quantity discard
        if len(pragScores) < minCount:
            continue
        
        results[convId] = {
            "pragmatic_scores": pragScores,
            "semantic_scores": semScores,
            "pragmatic_avg": sum(pragScores) / len(pragScores) if pragScores else None,
            "semantic_avg": sum(semScores) / len(semScores) if semScores else None
        }
    return results

def buildLongDf(base, comp, comp2):
    #https://www.geeksforgeeks.org/python/how-to-perform-a-repeated-measures-anova-in-python/
    #RManova requires a consistent amount of data for comparison otherwise Imbalanced error: This implementation uses truncation
    n = min(len(base), len(comp), len(comp2))
    df = pd.DataFrame({
        "subject": list(range(n)) * 3,
        "condition": (["base"] * n) + (["comparison"] * n) + (["comparison2"] * n),
        "score": base[:n] + comp[:n] + comp2[:n]
    })
    df["subject"] = df["subject"].astype("category")
    df["condition"] = df["condition"].astype("category")
    return df

def getAvgConvo(results):
    pragScores = []
    semScores = []
    #Get Average scores for each conversation
    for key in results:
        pragScores.append(results[key]["pragmatic_avg"])
        semScores.append(results[key]["semantic_avg"])
    return pragScores, semScores

def calcRmanovaConversation(baseScores, baseMin, comparisonScores, compareMin, comparisonScores2, compareMin2):
    
    #Convert JSON into usable format
    baseResults = conversationAverage(baseScores, baseMin)
    compareResults = conversationAverage(comparisonScores, compareMin)
    compare2Results = conversationAverage(comparisonScores2, compareMin2)
    
    #Calculate average scores for each conversation
    basePragAvgScores, baseSemAvgScores = getAvgConvo(baseResults)
    comparePragAvgScores, compareSemAvgScores = getAvgConvo(compareResults)
    compare2PragAvgScores, compare2SemAvgScores = getAvgConvo(compare2Results)
    
    #Build dataframe
    pragDf = buildLongDf(basePragAvgScores, comparePragAvgScores, compare2PragAvgScores)
    semDf = buildLongDf(baseSemAvgScores, compareSemAvgScores, compare2SemAvgScores)
    
    #RMAnova 
    #https://statistics.laerd.com/statistical-guides/repeated-measures-anova-statistical-guide.php
    anovaPrag = AnovaRM(
        data=pragDf,
        depvar="score",
        subject="subject",
        within=["condition"]
    ).fit()
    
    #RMAnova 
    #https://statistics.laerd.com/statistical-guides/repeated-measures-anova-statistical-guide.php
    anovaSem = AnovaRM(
        data=semDf,
        depvar="score",
        subject="subject",
        within=["condition"]
    ).fit()
    
    return anovaPrag, anovaSem

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

baseData, baseMin, baseName = loadJsonFromUser("Enter path to base dataset: ")
compareData, compareMin, compareName = loadJsonFromUser("Enter path to comparison dataset: ")
compareData2, compareMin2, compareName2 = loadJsonFromUser("Enter path to comparison dataset: ")

anovaPrag, anovaSem = calcRmanovaConversation(baseData, baseMin, compareData, compareMin, compareData2, compareMin2)
print(anovaPrag)
print(anovaSem)
