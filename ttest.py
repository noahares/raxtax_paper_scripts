import pandas as pd
import scipy.stats as stats
import sys

# Load the TSV file
file_path = sys.argv[1]
df = pd.read_csv(file_path, sep="\t")

# Get unique ranks
ranks = df["Rank"].unique()

# Store results
results = []

# Perform paired t-test for each Rank
for rank in ranks:
    subset = df[df["Rank"] == rank]  # Filter by Rank

    # Get F1 scores for each classifier
    raxtax_f1 = subset[subset["Classifier"] == "raxtax"]["F1"].values
    sintax_f1 = subset[subset["Classifier"] == "sintax"]["F1"].values

    # Ensure both classifiers have the same number of data points
    if len(raxtax_f1) == len(sintax_f1) and len(raxtax_f1) > 1:
        stat, p_value = stats.wilcoxon(raxtax_f1, sintax_f1)
        results.append([rank, stat, p_value])
    else:
        results.append([rank, None, None])  # Not enough data for test


    # Count how often Raxtax F1 > Sintax F1
    wins = sum(raxtax_f1 > sintax_f1)
    losses = sum(raxtax_f1 < sintax_f1)
    n = wins + losses  # Only consider non-tied pairs

    if n > 0:
        p_value = stats.binom_test(wins, n, 0.5, alternative="two-sided")
    else:
        p_value = None  # Not enough data

    print(f"Sign Test p-value: {p_value}")

# Convert results to a DataFrame
results_df = pd.DataFrame(results, columns=["Rank", "Wilcoxon Statistic", "P-Value"])

# Print or save results
print(results_df)
# results_df.to_csv("wilcoxon_results.tsv", sep="\t", index=False)  # Uncomment to save results
