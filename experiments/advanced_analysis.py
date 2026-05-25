import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


CSV_PATH = "results/csv/singlecenter_comparison.csv"


def load_data():
    return pd.read_csv(CSV_PATH)


def create_average_summary(df):
    def extract_group(instance_name):
        if "n10" in instance_name:
            return "n10"
        if "n50" in instance_name:
            return "n50"
        if "n100" in instance_name:
            return "n100"
        return "unknown"

    df["group"] = df["instance"].apply(extract_group)

    summary = (
        df.groupby("group")
        .agg(
            avg_baseline=("baseline_truck_only_cost", "mean"),
            avg_grasp=("grasp_tspd_cost", "mean"),
            avg_improvement=("improvement_percent", "mean"),
            avg_runtime=("runtime_seconds", "mean"),
        )
        .round(2)
    )

    output_path = "results/csv/average_summary.csv"
    summary.to_csv(output_path)

    print(summary)
    print(f"\nSaved: {output_path}")


def plot_average_improvement(df):
    def extract_group(instance_name):
        if "n10" in instance_name:
            return "n10"
        if "n50" in instance_name:
            return "n50"
        if "n100" in instance_name:
            return "n100"
        return "unknown"

    df["group"] = df["instance"].apply(extract_group)

    grouped = (
        df.groupby("group")["improvement_percent"]
        .mean()
        .reindex(["n10", "n50", "n100"])
    )

    plt.figure(figsize=(7, 5))
    plt.bar(grouped.index, grouped.values)

    plt.ylabel("Average Improvement (%)")
    plt.title("Average Improvement by Dataset Size")

    output_path = "results/figures/average_improvement.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def plot_runtime_scaling(df):
    def extract_group(instance_name):
        if "n10" in instance_name:
            return "n10"
        if "n50" in instance_name:
            return "n50"
        if "n100" in instance_name:
            return "n100"
        return "unknown"

    df["group"] = df["instance"].apply(extract_group)

    grouped = (
        df.groupby("group")["runtime_seconds"]
        .mean()
        .reindex(["n10", "n50", "n100"])
    )

    plt.figure(figsize=(7, 5))
    plt.plot(grouped.index, grouped.values, marker="o")

    plt.ylabel("Average Runtime (s)")
    plt.title("Runtime Scaling by Dataset Size")

    output_path = "results/figures/runtime_scaling.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def main():
    df = load_data()

    create_average_summary(df)
    plot_average_improvement(df)
    plot_runtime_scaling(df)

    print("\nAdvanced analysis completed.")


if __name__ == "__main__":
    main()