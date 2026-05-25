import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


CSV_PATH = "results/csv/parameter_tuning_results.csv"


def create_heatmap():
    df = pd.read_csv(CSV_PATH)

    pivot = df.pivot(
        index="k_max",
        columns="iterations",
        values="cost",
    )

    plt.figure(figsize=(8, 5))

    plt.imshow(pivot.values, aspect="auto")

    plt.xticks(range(len(pivot.columns)), pivot.columns)
    plt.yticks(range(len(pivot.index)), pivot.index)

    plt.xlabel("Iterations")
    plt.ylabel("k_max")
    plt.title("Parameter Heatmap (Cost)")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            plt.text(
                j,
                i,
                f"{pivot.values[i, j]:.0f}",
                ha="center",
                va="center",
            )

    plt.colorbar(label="Cost")

    output_path = Path("results/figures/parameter_heatmap.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    create_heatmap()