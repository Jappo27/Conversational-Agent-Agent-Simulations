import json
import os
from scipy.stats import f_oneway, f
import numpy as np
import matplotlib.pyplot as plt

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
    pragmaticScores = []
    semanticScores = []

    for turnIndex in sorted(turnScores.keys()):
        scores = np.array(turnScores[turnIndex])

        if len(scores) < minCount:
            continue

        pragmaticScores.append(scores[:, 0])
        semanticScores.append(scores[:, 1])
        turnIndices.append(turnIndex-1)

    return (
        turnIndices,
        pragmaticScores,
        semanticScores
    )

def calcOWANOVAConversation(baseAvgScores, comparisonAvgScores, comparisonAvgScores2):
    shared_turns = min(len(baseAvgScores), len(comparisonAvgScores), len(comparisonAvgScores2))

    f_list = []
    p_list = []

    for i in range(shared_turns):
        g1 = np.array([baseAvgScores[i]], dtype=float)[0]
        g2 = np.array([comparisonAvgScores[i]], dtype=float)[0]
        g3 = np.array([comparisonAvgScores2[i]], dtype=float)[0]
        
        f, p = f_oneway(g1, g2, g3)
        f_list.append(f)
        p_list.append(p)

    return np.array(f_list), np.array(p_list)


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

def plot_anova_results(f_stats, p_values, n_groups=3, n_samples_per_group=20, alpha=0.05):
    """
    Plots F-statistic and p-value time series with significance baselines.
    
    Parameters:
        f_stats (array-like): F-statistic values per turn
        p_values (array-like): p-values per turn
        n_groups (int): number of groups in the ANOVA
        n_samples_per_group (int): samples per group
        alpha (float): significance level (default 0.05)
    """

    f_stats = np.array(f_stats)
    p_values = np.array(p_values)
    turns = np.arange(1, len(f_stats) + 1)

    # Degrees of freedom
    df_between = n_groups - 1
    df_within = n_groups * (n_samples_per_group - 1)

    # F-critical value
    F_crit = f.ppf(1 - alpha, df_between, df_within)

    # --- Plotting ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # 1. F-statistic plot
    axes[0].plot(turns, f_stats, marker='o', color='blue', label="F-statistic")
    axes[0].axhline(y=F_crit, color='red', linestyle='--', alpha=0.7,
                    label=f"F-critical (α={alpha}, df={df_between},{df_within}) = {F_crit:.2f}")
    axes[0].set_ylabel("F-statistic")
    axes[0].set_title("ANOVA F-statistic per Turn")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    # 2. p-value plot
    axes[1].plot(turns, p_values, marker='o', color='purple', label="p-value")
    axes[1].axhline(y=alpha, color='red', linestyle='--', alpha=0.7,
                    label=f"p = {alpha}")
    axes[1].set_yscale('log')
    axes[1].set_xlabel("Turn")
    axes[1].set_ylabel("p-value (log scale)")
    axes[1].set_title("ANOVA p-value per Turn")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.show()


baseData, baseMin, base_name = load_json_from_user("Enter path to base dataset: ")
compareData, compareMin, compare_name = load_json_from_user("Enter path to comparison dataset: ")
compareData2, compareMin2, compare_name2 = load_json_from_user("Enter path to comparison dataset: ")

(
    turns,
    pragmaticAvgScores,
    semanticAvgScores
) = computeTurnAverages(baseData, minCount=baseMin)

(
    compareTurns,
    comparePragmaticAvgScores,
    compareSemanticAvgScores
) = computeTurnAverages(compareData, minCount=compareMin)

(
    compareTurns2,
    comparePragmaticAvgScores2,
    compareSemanticAvgScores2
) = computeTurnAverages(compareData2, minCount=compareMin2)


Pragmaticf_statistic, Pragmaticp_value = calcOWANOVAConversation(pragmaticAvgScores, comparePragmaticAvgScores, comparePragmaticAvgScores2)
plot_anova_results(Pragmaticf_statistic, Pragmaticp_value)
Semanticf_statistic, Semanticp_value = calcOWANOVAConversation(semanticAvgScores, compareSemanticAvgScores, compareSemanticAvgScores2)
plot_anova_results(Semanticf_statistic, Semanticp_value)