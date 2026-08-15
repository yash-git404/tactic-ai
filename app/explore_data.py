"""
Day 2 - Task: Explore the CSV files you downloaded from Kaggle.

Steps before running:
1. Put your downloaded CSV files inside the `data/` folder
2. Run: python app/explore_data.py
"""

import os
import pandas as pd

DATA_FOLDER = "data"


def explore_all_csvs():
    csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

    if not csv_files:
        print(f"❌ No CSV files found in '{DATA_FOLDER}/' folder.")
        print("Make sure you've downloaded and placed the Kaggle CSVs there.")
        return

    print(f"Found {len(csv_files)} CSV file(s): {csv_files}\n")
    print("=" * 60)

    for file in csv_files:
        path = os.path.join(DATA_FOLDER, file)
        print(f"\n📄 FILE: {file}")
        print("-" * 60)

        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(f"⚠️ Could not read this file: {e}")
            continue

        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"\nColumn names:\n{list(df.columns)}")
        print(f"\nFirst 3 rows:\n{df.head(3)}")
        print(f"\nMissing values per column:\n{df.isnull().sum()}")
        print("=" * 60)


if __name__ == "__main__":
    explore_all_csvs()
