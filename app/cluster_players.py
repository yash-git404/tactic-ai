"""
Day 6 - Task: Cluster players into style groups using K-means.

Run: python app/cluster_players.py
Output: a chart showing clusters, and updated player_profiles.csv with a Cluster column.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

CLEANED_FOLDER = "data/cleaned"
CHARTS_FOLDER = "docs/charts"

SCORE_COLUMNS = [
    "Goals_Score",
    "Appearances_Score",
    "Attack_Score",
    "Experience_Score",
    "Discipline_Score",
]

N_CLUSTERS = 4


def run_clustering():
    profiles = pd.read_csv(f"{CLEANED_FOLDER}/player_profiles.csv")

    # Only cluster players with a meaningful number of appearances,
    # otherwise players with 1 match dominate with noisy/extreme scores
    active_players = profiles[profiles["Appearances"] >= 3].copy()

    X = active_players[SCORE_COLUMNS].values

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    active_players["Cluster"] = kmeans.fit_predict(X)

    # Merge cluster labels back into full profile table
    profiles = profiles.merge(
        active_players[["Player Name", "Cluster"]], on="Player Name", how="left"
    )
    profiles.to_csv(f"{CLEANED_FOLDER}/player_profiles.csv", index=False)

    print(f"✅ Clustered {active_players.shape[0]} players into {N_CLUSTERS} groups\n")

    # Show what each cluster looks like on average, to help interpret them
    cluster_summary = active_players.groupby("Cluster")[SCORE_COLUMNS + ["Goals", "Appearances"]].mean().round(1)
    print("Cluster averages (helps interpret what each group represents):")
    print(cluster_summary)

    # Visualize clusters in 2D using PCA (reduces 5 dimensions down to 2 for plotting)
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(
        coords[:, 0], coords[:, 1],
        c=active_players["Cluster"], cmap="Set2", alpha=0.6, s=25
    )
    plt.title("Player Style Clusters (visualized in 2D)")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.legend(*scatter.legend_elements(), title="Cluster")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_FOLDER}/player_clusters.png")
    plt.close()
    print(f"\n✅ Cluster visualization saved to {CHARTS_FOLDER}/player_clusters.png")

    return active_players, cluster_summary


if __name__ == "__main__":
    run_clustering()
