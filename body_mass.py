# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 09:15:30 2025

@author: solho
"""

from math import comb
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, shapiro, ttest_ind

file_path = r"C:\Users\solho\OneDrive\Dokumenter\Master\Data\Extra Data\Pup_Weights.xlsx"
df = pd.read_excel(file_path, sheet_name="All")


def is_control(col):
    return any(x in col.lower() for x in ["control", "contro", "ctrl"])


def is_female(col):
    return any(k in col.lower() for k in ["jente", "female", "f"])


def is_male(col):
    return any(k in col.lower() for k in ["gutt", "male", "m"])


selected_days = [16, 18, 20, 24]

colors = {
    "noncontrol_female": "lightcoral",
    "control_female": "#B22222",
    "noncontrol_male": "#5AA9E6",
    "control_male": "#1D3557",
    "noncontrol_avg": "#4CAF50",
    "control_avg": "darkgreen",
}


def mean_sem_for_day(df, cols, day):
    vals = df.loc[df["Age"] == day, cols].values.flatten()
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return np.nan, np.nan
    mean = np.mean(vals)
    sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
    return mean, sem


def permutation_pvalue(x, y, n_perm=10000, rng=None):
    """Permutation test for difference in means."""
    rng = np.random.default_rng(rng)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    z = np.concatenate([x, y])
    n_x = len(x)
    t_obs = np.mean(x) - np.mean(y)

    total_perm = comb(len(z), n_x)
    if total_perm <= n_perm:
        t_values = []
        idx_all = np.arange(len(z))
        for combi in combinations(idx_all, n_x):
            combi = np.array(combi)
            rest = np.setdiff1d(idx_all, combi, assume_unique=True)
            t_values.append(np.mean(z[combi]) - np.mean(z[rest]))
        t_values = np.array(t_values)
    else:
        t_values = np.array(
            [
                np.mean(rng.choice(z, n_x, replace=False))
                - np.mean(rng.choice(z, len(z) - n_x, replace=False))
                for _ in range(n_perm)
            ]
        )

    p = (np.sum(np.abs(t_values) >= abs(t_obs)) + 1) / (t_values.size + 1)
    return t_obs, p


noncontrol_females = [c for c in df.columns if c != "Age" and is_female(c) and not is_control(c)]
noncontrol_males = [c for c in df.columns if c != "Age" and is_male(c) and not is_control(c)]
control_females = [c for c in df.columns if c != "Age" and is_female(c) and is_control(c)]
control_males = [c for c in df.columns if c != "Age" and is_male(c) and is_control(c)]

records = []
for day in selected_days:
    for group_name, cols in [
        ("noncontrol_female", noncontrol_females),
        ("control_female", control_females),
        ("noncontrol_male", noncontrol_males),
        ("control_male", control_males),
        ("noncontrol_avg", noncontrol_females + noncontrol_males),
        ("control_avg", control_females + control_males),
    ]:
        mean, sem = mean_sem_for_day(df, cols, day)
        records.append({"day": day, "group": group_name, "mean": mean, "sem": sem})

plot_df = pd.DataFrame(records)
print(plot_df.to_string(index=False))

plt.figure(figsize=(10, 6), dpi=300)

n_groups_per_day = 6
bar_width = 0.12
gap_within_category = 0
gap_between_categories = 0.04
day_gap = 0.25

order = [
    "noncontrol_female",
    "control_female",
    "noncontrol_male",
    "control_male",
    "noncontrol_avg",
    "control_avg",
]

group_offsets = np.array(
    [
        0,
        bar_width + gap_within_category,
        bar_width * 2 + gap_within_category + gap_between_categories,
        bar_width * 3 + 2 * gap_within_category + gap_between_categories,
        bar_width * 4 + 2 * gap_within_category + 2 * gap_between_categories,
        bar_width * 5 + 3 * gap_within_category + 2 * gap_between_categories,
    ]
)

x_positions = []
for i, day in enumerate(selected_days):
    start = i * (bar_width * 6 + day_gap + 2 * gap_between_categories)
    x_positions.extend(start + group_offsets)

x_labels = [
    i * (bar_width * 6 + day_gap + 2 * gap_between_categories)
    + (bar_width * 6 + 2 * gap_within_category + 2 * gap_between_categories) / 2
    for i in range(len(selected_days))
]

labels_map = {
    "noncontrol_female": "Control female",
    "control_female": "SD female",
    "noncontrol_male": "Control male",
    "control_male": "SD male",
    "noncontrol_avg": "Control avg",
    "control_avg": "SD avg",
}

for idx, group_name in enumerate(order):
    subset = plot_df[plot_df["group"] == group_name]
    positions = [x_positions[i * n_groups_per_day + idx] for i in range(len(selected_days))]
    label_name = labels_map.get(group_name, group_name.replace("_", " ").capitalize())

    plt.bar(
        positions,
        subset["mean"],
        yerr=subset["sem"],
        capsize=4,
        color=colors[group_name],
        edgecolor="black",
        width=bar_width,
        alpha=0.85,
        label=label_name,
    )


group_cols = {
    "noncontrol_female": noncontrol_females,
    "control_female": control_females,
    "noncontrol_male": noncontrol_males,
    "control_male": control_males,
    "noncontrol_avg": noncontrol_females + noncontrol_males,
    "control_avg": control_females + control_males,
}

comparisons = [
    ("noncontrol_female", "control_female"),
    ("noncontrol_male", "control_male"),
    ("noncontrol_avg", "control_avg"),
]

for group_a, group_b in comparisons:
    idx_a = order.index(group_a)
    idx_b = order.index(group_b)

    for i, day in enumerate(selected_days):
        vals_a = df.loc[df["Age"] == day, group_cols[group_a]].values.flatten()
        vals_b = df.loc[df["Age"] == day, group_cols[group_b]].values.flatten()
        vals_a = vals_a[~np.isnan(vals_a)]
        vals_b = vals_b[~np.isnan(vals_b)]

        if len(vals_a) < 2 or len(vals_b) < 2:
            continue

        # Use permutation test for very small samples.
        if len(vals_a) < 3 or len(vals_b) < 3:
            test_name = "Permutation"
            _, p = permutation_pvalue(vals_a, vals_b)
            normal = False
        else:
            p_a = shapiro(vals_a)[1]
            p_b = shapiro(vals_b)[1]
            normal = (p_a > 0.05) and (p_b > 0.05)

            if normal:
                test_name = "t-test"
                _, p = ttest_ind(vals_a, vals_b, equal_var=False, nan_policy="omit")
            else:
                test_name = "MWU"
                _, p = mannwhitneyu(vals_a, vals_b, alternative="two-sided")

        if p < 0.001:
            stars = "***"
        elif p < 0.01:
            stars = "**"
        elif p < 0.05:
            stars = "*"
        else:
            stars = "ns"

        x1 = x_positions[i * n_groups_per_day + idx_a]
        x2 = x_positions[i * n_groups_per_day + idx_b]
        y_max = np.nanmax(
            [
                plot_df.loc[
                    (plot_df["day"] == day) & (plot_df["group"] == group_a), "mean"
                ].values[0],
                plot_df.loc[
                    (plot_df["day"] == day) & (plot_df["group"] == group_b), "mean"
                ].values[0],
            ]
        )

        ymin, ymax_total = plt.ylim()
        yrange = ymax_total - ymin
        y = y_max + 0.03 * yrange

        plt.plot(
            [x1, x1, x2, x2],
            [y, y + 0.015 * yrange, y + 0.015 * yrange, y],
            color="black",
            linewidth=1.2,
        )
        plt.text(
            (x1 + x2) / 2,
            y + 0.02 * yrange,
            stars,
            ha="center",
            va="bottom",
            fontsize=12,
            color="black",
        )

        print(
            f"Day {day:>2} | {group_a} vs {group_b}: "
            f"n={len(vals_a)}/{len(vals_b)} | p={p:.4f} "
            f"({test_name}, {'Normal' if normal else 'Non-normal'}) -> {stars}"
        )


plt.xticks(x_labels, [str(d) for d in selected_days])
plt.xlabel("Age (postnatal days)", fontsize=16)
plt.ylabel("Body mass (g)", fontsize=16)
plt.title("Body Mass Comparisons", fontsize=18)
plt.legend(fontsize=12, ncol=3, loc="upper left")
plt.grid(axis="y", linestyle="--", alpha=0.5)

ax = plt.gca()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_linewidth(2)
ax.spines["left"].set_linewidth(2)
ax.tick_params(width=2)

ymin = plot_df["mean"].min() - 0.1
ymax = plot_df["mean"].max() + 0.2
plt.ylim(ymin, ymax)

plt.tight_layout()
plt.savefig("bodyweight_histogram_with_stats.png", dpi=300)
plt.show()
