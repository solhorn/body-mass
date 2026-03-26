# -*- coding: utf-8 -*-
"""
Created on Sun Jan 25 13:13:24 2026

Body mass comparisons normalized to P16 baseline.
@author: solho
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, ttest_ind, mannwhitneyu

file_path = r"C:\Users\solho\OneDrive\Dokumenter\Master\Data\Extra Data\Pup_Weights.xlsx"
df = pd.read_excel(file_path, sheet_name="All")

# Keep only P15-P24.
df = df[(df["Age"] >= 15) & (df["Age"] <= 24)].copy()

weight_cols = [c for c in df.columns if c != "Age"]

for col in weight_cols:
    # Use the P16 value for each rat as baseline.
    base_vals = df.loc[df["Age"] == 16, col].dropna()
    if base_vals.empty:
        continue
    baseline = base_vals.iloc[0]
    df[col] = df[col] / baseline


def is_control(col: str) -> bool:
    col = col.lower()
    return any(x in col for x in ["control", "contro", "ctrl"])


def is_female(col: str) -> bool:
    col = col.lower()
    return any(k in col for k in ["jente", "female", "f_"])


def is_male(col: str) -> bool:
    col = col.lower()
    return any(k in col for k in ["gutt", "male", "m_"])


selected_days = [18, 20, 24]

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
    mean = float(np.mean(vals))
    sem = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
    return mean, sem


# Group columns by condition and sex.
noncontrol_females = [c for c in weight_cols if is_female(c) and not is_control(c)]
noncontrol_males = [c for c in weight_cols if is_male(c) and not is_control(c)]
control_females = [c for c in weight_cols if is_female(c) and is_control(c)]
control_males = [c for c in weight_cols if is_male(c) and is_control(c)]

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

plt.figure(figsize=(10, 7), dpi=300)

n_groups_per_day = 6
bar_width = 0.12

gap_within_category = 0.0
gap_between_categories = 0.04
day_gap = 0.25

order = [
    "noncontrol_female", "control_female",
    "noncontrol_male", "control_male",
    "noncontrol_avg", "control_avg",
]

group_offsets = np.array([
    0,
    bar_width + gap_within_category,
    bar_width * 2 + gap_within_category + gap_between_categories,
    bar_width * 3 + 2 * gap_within_category + gap_between_categories,
    bar_width * 4 + 2 * gap_within_category + 2 * gap_between_categories,
    bar_width * 5 + 3 * gap_within_category + 2 * gap_between_categories,
])

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
    "control_female": "SR female",
    "noncontrol_male": "Control male",
    "control_male": "SR male",
    "noncontrol_avg": "Control avg",
    "control_avg": "SR avg",
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

        # Check normality when sample size allows it.
        if len(vals_a) >= 3 and len(vals_b) >= 3:
            p_a = shapiro(vals_a)[1]
            p_b = shapiro(vals_b)[1]
            normal = (p_a > 0.05) and (p_b > 0.05)
        else:
            normal = False

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

        y_max = np.nanmax([
            plot_df.loc[(plot_df["day"] == day) & (plot_df["group"] == group_a), "mean"].values[0],
            plot_df.loc[(plot_df["day"] == day) & (plot_df["group"] == group_b), "mean"].values[0],
        ])

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
            fontsize=15,
        )

        print(
            f"Day {day:>2} | {group_a} vs {group_b}: "
            f"n={len(vals_a)}/{len(vals_b)} | p={p:.4f} ({test_name}, {'Normal' if normal else 'Non-normal'}) -> {stars}"
        )


plt.xticks(x_labels, [str(d) for d in selected_days])
plt.xlabel("Age (postnatal days)", fontsize=18)
plt.ylabel("Body mass (relative to P16)", fontsize=18)
plt.title("Body Mass Comparisons", fontsize=18)
plt.legend(fontsize=13, ncol=3, loc="upper left")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.axhline(1, color="black", linestyle="--", linewidth=1.5)

plt.tick_params(axis="x", labelsize=14)
plt.tick_params(axis="y", labelsize=14)

ax = plt.gca()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_linewidth(2)
ax.spines["left"].set_linewidth(2)
ax.tick_params(width=2)

plt.tight_layout()
plt.savefig("bodyweight_histogram_relative_P16_with_stats.png", dpi=300)
plt.show()
