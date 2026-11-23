"""
AI Adoption & Enablement: the strategy read-out.

Questions it answers:
  Adoption:    Who is using the assistant, and does usage follow the content we ship?
  Value:       How much support demand does live content absorb today, and how much is left?
  Priorities:  Which topics should ship next, ranked by hours recoverable and gated by risk?
  Governance:  What is holding high-risk topics back, and does ownership change delivery?

Usage (from the repo root):  python analysis/analyze.py
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

INK, MUTED, GRID = "#1f2937", "#6b7280", "#e5e7eb"
ACCENT, ALERT, CALM, OK, AMBER = "#4338ca", "#dc2626", "#cbd5e1", "#16a34a", "#d97706"
STATUS_COLORS = {"Live": OK, "In review": AMBER, "Drafting": "#93c5fd", "Not started": CALM}
TIER_COLORS = {1: ALERT, 2: AMBER, 3: ACCENT}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})


def title(ax, text, sub=None):
    ax.set_title(text, loc="left", color=INK, fontweight="bold", pad=20 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=MUTED, fontsize=9)


def save(fig, name):
    fig.savefig(IMG / name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


t = pd.read_csv(ROOT / "data" / "topics.csv")
a = pd.read_csv(ROOT / "data" / "adoption.csv", parse_dates=["week_start"])
c = pd.read_csv(ROOT / "data" / "controls.csv")
t["curator"] = t["curator"].fillna("")
t["hours_q"] = t["tickets_90d"] * t["deflection_rate"] * t["avg_handle_min"] / 60  # support hours recoverable per quarter
t["live"] = t["status"] == "Live"
F = {}

# ------------------------------------------------------------------ value
F["value"] = {
    "topics": int(len(t)), "live": int(t["live"].sum()),
    "enablement_rate_pct": round(t["live"].mean() * 100),
    "demand_covered_pct": round(t.loc[t["live"], "tickets_90d"].sum() / t["tickets_90d"].sum() * 100),
    "hours_recovered_q": round(t.loc[t["live"], "hours_q"].sum()),
    "hours_available_q": round(t.loc[~t["live"], "hours_q"].sum()),
    "tickets_deflected_q": round((t.loc[t["live"], "tickets_90d"] * t.loc[t["live"], "deflection_rate"]).sum()),
}

# ------------------------------------------------------------- governance
tier1 = t[t["risk_tier"] == 1]
open_controls = c[c["status"] == "Open"].merge(t[["topic_id", "risk_tier"]], on="topic_id")
cur = t.groupby(t["curator"] != "")["live"].agg(["sum", "count"])
F["governance"] = {
    "tier1_topics": int(len(tier1)), "tier1_live": int(tier1["live"].sum()),
    "tier1_tickets_90d": int(tier1["tickets_90d"].sum()),
    "tier1_hours_q": round(tier1["hours_q"].sum()),
    "open_controls_tier1": int((open_controls["risk_tier"] == 1).sum()),
    "curator_assigned_pct": round((t["curator"] != "").mean() * 100),
    "live_rate_with_curator_pct": round(cur.loc[True, "sum"] / cur.loc[True, "count"] * 100),
    "live_rate_without_curator_pct": round(cur.loc[False, "sum"] / cur.loc[False, "count"] * 100),
    "unowned_topics": int((t["curator"] == "").sum()),
    "unowned_hours_q": round(t.loc[t["curator"] == "", "hours_q"].sum()),
}

# --------------------------------------------------------------- adoption
last = a[a["week_start"] == a["week_start"].max()].copy()
last["active_rate"] = last["active_users"] / last["headcount"]
last["resolution_rate"] = last["resolved_by_assistant"] / last["queries"]
dept = t.groupby("department").agg(topics=("topic_id", "count"), live=("live", "sum"))
dept["live_share"] = dept["live"] / dept["topics"]
last = last.set_index("department").join(dept)
F["adoption"] = {
    "employees": int(last["headcount"].sum()),
    "weekly_active": int(last["active_users"].sum()),
    "weekly_active_pct": round(last["active_users"].sum() / last["headcount"].sum() * 100),
    "resolution_rate_pct": round(last["resolved_by_assistant"].sum() / last["queries"].sum() * 100),
    "helpful_pct": round(a["helpful_votes"].sum() / a["total_votes"].sum() * 100),
    "corr_live_share_active_rate": round(float(np.corrcoef(last["live_share"], last["active_rate"])[0, 1]), 2),
    "leaders": last.sort_values("active_rate", ascending=False).head(2).index.tolist(),
    "laggards": last.sort_values("active_rate").head(3).index.tolist(),
    "leader_active_pct": round(last["active_rate"].max() * 100),
    "laggard_active_pct": round(last.sort_values("active_rate").head(3)["active_rate"].mean() * 100),
}

# ----------------------------------------------------------------- backlog
backlog = t[~t["live"]].sort_values("hours_q", ascending=False)
backlog["wave"] = np.where(backlog["risk_tier"] == 1, "Wave 2: govern first",
                           np.where(backlog["curator"] != "", "Wave 1: ship now", "Wave 1: assign curator"))
F["backlog"] = {
    "wave1_topics": int((backlog["risk_tier"] > 1).sum()),
    "wave1_hours_q": round(backlog.loc[backlog["risk_tier"] > 1, "hours_q"].sum()),
    "wave2_topics": int((backlog["risk_tier"] == 1).sum()),
    "wave2_hours_q": round(backlog.loc[backlog["risk_tier"] == 1, "hours_q"].sum()),
    "top5": backlog.head(5)[["topic", "department", "risk_tier", "status", "curator"]].assign(hours_q=backlog.head(5)["hours_q"].round()).to_dict("records"),
}

# ================================================================= charts
# 1. Adoption by department over time
piv = a.assign(rate=a["active_users"] / a["headcount"] * 100).pivot(index="week_start", columns="department", values="rate")
fig, ax = plt.subplots(figsize=(9.5, 4.3))
order = piv.iloc[-1].sort_values(ascending=False).index
palette = dict(zip(order, [ACCENT, "#6366f1", "#0891b2", "#22d3ee", AMBER, "#f97316", ALERT]))
ys = {}
for d in order:  # space end labels at least 5 points apart, top to bottom
    y = piv[d].iloc[-1]
    if ys:
        y = min(y, min(ys.values()) - 5)
    ys[d] = y
for d in order:
    ax.plot(piv.index, piv[d], color=palette[d], linewidth=2.2 if d in (order[0], order[-1]) else 1.4)
    ax.text(piv.index[-1] + pd.Timedelta(days=3), ys[d], f"{d} {piv[d].iloc[-1]:.0f}%", color=palette[d], fontsize=8, va="center")
ax.set_ylabel("Weekly active users (% of headcount)")
ax.set_ylim(0, 100)
ax.grid(axis="y", color=GRID)
title(ax, "Adoption follows the content", "Teams whose topics are live use the assistant about 7× more than teams still waiting on content")
save(fig, "adoption_by_department.png")

# 2. Department readiness (status mix)
mix = t.pivot_table(index="department", columns="status", values="topic_id", aggfunc="count").fillna(0)
mix = mix.reindex(columns=["Live", "In review", "Drafting", "Not started"], fill_value=0)
mix = mix.loc[(mix["Live"] / mix.sum(axis=1)).sort_values().index]
fig, ax = plt.subplots(figsize=(8.5, 4))
left = np.zeros(len(mix))
for s in mix.columns:
    ax.barh(mix.index, mix[s], left=left, color=STATUS_COLORS[s], label=s, height=0.6)
    left += mix[s].values
ax.legend(frameon=False, fontsize=8, ncol=4, loc="lower right", bbox_to_anchor=(1, -0.25))
ax.set_xlabel("Knowledge-base topics")
title(ax, "Readiness by department", "Business Technology is fully live; Finance, People and Legal have nothing live yet")
save(fig, "department_readiness.png")

# 3. Backlog ranked by value, colored by risk tier
bl = backlog.head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.barh([f"{r.topic}  ({r.department})" for r in bl.itertuples()], bl["hours_q"], color=[TIER_COLORS[x] for x in bl["risk_tier"]])
for i, (h, cur_) in enumerate(zip(bl["hours_q"], bl["curator"])):
    ax.text(h + 0.6, i, f"{h:.0f}h" + ("" if cur_ else " · no curator"), va="center", fontsize=8, color=MUTED)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=TIER_COLORS[k], label=v) for k, v in
                   ((1, "Tier 1: compliance & personal data"), (2, "Tier 2: operational & access"), (3, "Tier 3: general"))],
          frameon=False, fontsize=8, loc="lower right")
ax.set_xlabel("Support hours recoverable per quarter once live")
ax.tick_params(axis="y", labelsize=8)
title(ax, "What to ship next", "Not-yet-live topics ranked by support hours they would recover")
save(fig, "enablement_backlog.png")

# 4. Ownership effect + tier gating
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
own = t.assign(owner=np.where(t["curator"] != "", "Curator assigned", "No curator")).pivot_table(
    index="owner", columns="status", values="topic_id", aggfunc="count").fillna(0).reindex(columns=["Live", "In review", "Drafting", "Not started"], fill_value=0)
left = np.zeros(len(own))
for s in own.columns:
    ax1.barh(own.index, own[s], left=left, color=STATUS_COLORS[s], label=s, height=0.55)
    left += own[s].values
ax1.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
title(ax1, "Ownership drives delivery",
      f"{F['governance']['live_rate_with_curator_pct']}% of curated topics are live vs {F['governance']['live_rate_without_curator_pct']}% without a curator")
tiers = t.groupby("risk_tier").agg(live=("live", "sum"), n=("topic_id", "count"), tix=("tickets_90d", "sum"))
x = np.arange(3)
ax2.bar(x, tiers["n"], color=CALM, width=0.55, label="Topics")
ax2.bar(x, tiers["live"], color=OK, width=0.55, label="Live")
ax2.legend(frameon=False, fontsize=8, loc="upper left")
for i, r in enumerate(tiers.itertuples()):
    ax2.text(i, r.n + 0.3, f"{int(r.live)} of {r.n} live", ha="center", fontsize=9, color=INK)
ax2.set_xticks(x, ["Tier 1\nCompliance & PII", "Tier 2\nOperational", "Tier 3\nGeneral"])
ax2.set_ylabel("Topics")
title(ax2, "High-risk topics are gated", f"Tier 1 holds {F['governance']['tier1_tickets_90d']} tickets a quarter; none of it is live")
save(fig, "governance.png")

print(json.dumps(F, indent=2, default=str))
print(last[["active_rate", "resolution_rate", "live_share"]].round(2))
print(backlog[["topic", "department", "risk_tier", "status", "curator", "hours_q", "wave"]].round(1).to_string())
