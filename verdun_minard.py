"""
Verdun 1916 - a Minard-style figurative chart.
Band width = casualties per day (French above the axis, German below).
Lower panel = cumulative casualties (Minard's temperature panel, re-imagined).

DATA SOURCES
- Feb-Aug monthly casualties: Alistair Horne, "The Price of Glory" (as tabulated on wereldoorlog1418.nl)
- Totals: French 377,231 / German 337,000 (Mémorial de Verdun; History.com; Wikipedia)
- Sep-Dec: NOT available month by month -> derived as (official total - Feb-Aug sum)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

D = lambda m, d: mdates.date2num(date(1916, m, d))
TAN, BLACK = "#d8b48a", "#1a1a1a"

# ---- monthly data (month, days in period, French, German) ----
months = [
    ("Feb", 9, 24000, 25363),   # battle starts 21 Feb
    ("Mar", 31, 65000, 56244),
    ("Apr", 30, 42000, 38299),
    ("May", 31, 59000, 54309),
    ("Jun", 30, 67000, 51567),
    ("Jul", 31, 31000, 25969),
    ("Aug", 31, 27000, 30572),
]
FR_TOTAL, DE_TOTAL = 377231, 337000
fr_h, de_h = sum(m[2] for m in months), sum(m[3] for m in months)      # 315,000 / 282,323
rest_days = (date(1916, 12, 18) - date(1916, 9, 1)).days + 1           # 109 days
fr_rest, de_rest = FR_TOTAL - fr_h, DE_TOTAL - de_h                     # derived

# ---- band-width control points (casualties per day) ----
mids = [D(2, 25), D(3, 16), D(4, 15), D(5, 16), D(6, 15), D(7, 16), D(8, 16)]
xs = [D(2, 21)] + mids + [D(9, 1), D(12, 18)]
fr = [months[0][2] / months[0][3]] + [m[2] / m[1] for m in months] + [fr_rest / rest_days] * 2
de = [months[0][3] / months[0][1]] + [m[3] / m[1] for m in months] + [de_rest / rest_days] * 2
fr = [months[0][2] / months[0][1]] + fr[1:]
de = [months[0][3] / months[0][1]] + de[1:]
fr_k = [v / 1000 for v in fr]
de_k = [v / 1000 for v in de]

# ---- cumulative casualties ----
ends = [D(2, 21), D(2, 29), D(3, 31), D(4, 30), D(5, 31), D(6, 30), D(7, 31), D(8, 31), D(12, 18)]
cf, cd, a, b = [0], [0], 0, 0
for m in months:
    a += m[2]; b += m[3]; cf.append(a); cd.append(b)
cf.append(FR_TOTAL); cd.append(DE_TOTAL)

events = [
    (D(2, 21), "21–25 Feb  German offensive;\nFort Douaumont falls (25 Feb)"),
    (D(6, 7),  "7 Jun  Fort Vaux falls"),
    (D(7, 1),  "1 Jul  Somme offensive begins"),
    (D(8, 18), "18 Aug  French retake Fleury"),
    (D(10, 24), "24 Oct  French counter-attack,\nDouaumont retaken"),
    (D(12, 18), "18 Dec  Battle ends"),
]

plt.rcParams["font.family"] = "serif"
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(16, 9), sharex=True,
                              gridspec_kw={"height_ratios": [3, 1.35], "hspace": 0.12})
fig.patch.set_facecolor("#fbf7ef")
for a_ in (ax, ax2):
    a_.set_facecolor("#fbf7ef")

# ribbons
ax.fill_between(xs, 0, fr_k, color=TAN, lw=0, label="French losses")
ax.fill_between(xs, 0, [-v for v in de_k], color=BLACK, lw=0, label="German losses")
ax.axhline(0, color="white", lw=0.8)
# hatch the derived Sep-Dec segment
ax.fill_between(xs[-2:], 0, fr_k[-2:], facecolor="none", hatch="///", edgecolor="#fbf7ef", lw=0)
ax.fill_between(xs[-2:], 0, [-v for v in de_k[-2:]], facecolor="none", hatch="///", edgecolor="#777", lw=0)

# value labels (monthly totals)
for k, ((name, _, f, g), x) in enumerate(zip(months, mids)):
    i = k + 1
    if k == 0:
        x, ha = D(2, 22), "left"
        yf, yg = fr_k[0] + 0.12, -de_k[0] - 0.15
    else:
        ha, yf, yg = "center", fr_k[i] + 0.12, -de_k[i] - 0.3
    ax.text(x, yf, f"{f:,}", ha=ha, va="bottom", fontsize=9)
    ax.text(x, yg, f"{g:,}", ha=ha, va="top", fontsize=9)
xm = (D(9, 1) + D(12, 18)) / 2
ax.text(xm, fr_k[-1] + 0.12, f"{fr_rest:,}\n(Sep–Dec, derived)", ha="center", va="bottom", fontsize=9)
ax.text(xm, -de_k[-1] - 0.12, f"{de_rest:,}\n(Sep–Dec, derived)", ha="center", va="top", fontsize=9)

# events
for x, label in events:
    for a_ in (ax, ax2):
        a_.axvline(x, color="#777", lw=0.7, ls=":", zorder=0)
ys = [3.7, 3.7, 4.7, 3.7, 4.7, 3.7]
for (x, label), y in zip(events, ys):
    ax.text(x, y, label, fontsize=8.5, ha="left" if x < D(12, 1) else "right", va="bottom",
            rotation=0)

ax.set_ylim(-3.6, 5.9)
ax.set_yticks([])
for s in ("top", "right", "left", "bottom"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="x", length=0)

fig.suptitle("CARTE FIGURATIVE des pertes quotidiennes des armées française et allemande "
             "à la bataille de VERDUN, 21 février – 18 décembre 1916",
             fontsize=15, fontweight="bold", x=0.01, ha="left", y=0.99)
ax.text(D(9, 5), -2.1,
        "Band width = casualties per day (killed, wounded,\nmissing, captured). Labels = casualties in the month.\n"
        "Feb = 21–29 Feb only. Hatched = Sep–18 Dec: no monthly\nfigures published; averaged from the official totals.",
        fontsize=8.5, va="top", ha="left", style="italic")
ax.legend(loc="lower left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.0))

# lower panel: cumulative
ax2.plot(ends, cf, color="#b98a52", lw=2.4, marker="o", label="French (cumulative)")
ax2.plot(ends, cd, color=BLACK, lw=2.4, marker="o", label="German (cumulative)")
ax2.plot(ends[-2:], cf[-2:], color="#b98a52", lw=2.4, ls="--")
ax2.plot(ends[-2:], cd[-2:], color=BLACK, lw=2.4, ls="--")
ax2.text(ends[-1] + 2, cf[-1], f"{FR_TOTAL:,}", va="center", fontsize=9)
ax2.text(ends[-1] + 2, cd[-1] - 12000, f"{DE_TOTAL:,}", va="center", fontsize=9)
ax2.set_ylim(0, 420000)
ax2.set_yticks([0, 100000, 200000, 300000])
ax2.set_yticklabels(["0", "100k", "200k", "300k"], fontsize=9)
ax2.set_title("TABLEAU GRAPHIQUE des pertes cumulées", loc="left", fontsize=12, style="italic")
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)
ax2.grid(axis="y", color="#ddd", lw=0.6)
ax2.legend(loc="upper left", frameon=False, fontsize=9)
ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax2.set_xlim(D(2, 1), D(12, 31))

fig.text(0.01, 0.0,
         "Sources: A. Horne, The Price of Glory (monthly Feb–Aug); Mémorial de Verdun; History.com; Wikipedia (totals: "
         "France 377,231, Germany 337,000). Event dates: standard histories.",
         fontsize=8, color="#555")
fig.savefig("/mnt/user-data/outputs/verdun_minard.png", dpi=170, bbox_inches="tight",
            facecolor=fig.get_facecolor())
