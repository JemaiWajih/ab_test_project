"""
utils.py - reusable helpers for A/B test analysis
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint


def conversion_rate(df, group_col="test group", conv_col="converted"):
    return df.groupby(group_col)[conv_col].mean()
"""Return conversion rate (mean) per group as a Series."""


def group_sizes(df, group_col="test group"):
    return df.groupby(group_col).size().rename("n_users")
"""Return count of users per group"""


def confidence_interval(successes, nobs, alpha=0.05, method="wilson"):
    lower, upper = proportion_confint(successes, nobs, alpha=alpha, method=method)
    return lower, upper
"""Return (lower, upper) confidence interval for proportion"""

def plot_conversion_rates(rates, cis, save_path=None):
    """
    Bar chart of conversion rates with 95% CI error bars.
    rates : dict {group_name: rate}
    cis : dict {group_name: (lower, upper)}
    """

    groups = list(rates.keys())
    values = [rates[g] * 100 for g in groups ]
    errors = [ 
        [(rates[g] - cis[g][0]) * 100, (cis[g][1] - rates[g]) * 100]
        for g in groups 
    ]
    yerr = np.array(errors).T  # shape (2, n_groups)

    colors = ["#5B6EE1", "#E15B5B"]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(groups, values, color=colors, width=0.4,
                  yerr=yerr, capsize=8, error_kw={"linewidth": 1.5, "ecolor": "#333"})

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + yerr[1][bars.patches.index(bar)] + 0.2,
                f"{val:.2f}%" , ha="center" , va="bottom" , fontsize=11, fontweight="bold")

    ax.set_ylabel("Conversion rate (%)", fontsize=12)
    ax.set_title("Conversion rate by group with 95% confidence intervals", fontsize=13)
    ax.set_ylim(0, max(values) * 1.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle='-', alpha=0.4)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"Saved --> {save_path}")
    plt.show()


def print_summary(group_stats):
    print(f"\n{'Group':<12} {'N users' :>10} {'Conversions':>14} {'Rate':>10}")
    print("_" * 50)
    for group, row in group_stats.iterrows():
        print(f"{group:<12} {int(row['n_users'])}"
              f"{int(row['conversions']):>14,} {row['rate']*100:>9.2f}%")

    print()

    
