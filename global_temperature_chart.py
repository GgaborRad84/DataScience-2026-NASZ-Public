"""
Global surface temperature, 1880-2025 (NASA GISTEMP v4, land+ocean, anomaly vs 1951-1980).
Panels: (1) warming stripes  (2) annual anomalies + 11-yr mean  (3) decadal means.
Data: global_temperature_gistemp.csv  (GISTEMP annual means via datahub.io/core/global-temp)
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib import cm

d = pd.read_csv("global_temperature_gistemp.csv")
d["smooth"] = d.anomaly_c.rolling(11, center=True).mean()
cmap = plt.get_cmap("RdBu_r")
norm = TwoSlopeNorm(vmin=-0.6, vcenter=0.0, vmax=1.3)
col = [cmap(norm(v)) for v in d.anomaly_c]

# decadal means (2020s = 2020-2025 only)
d["dec"] = d.year // 10 * 10
dec = d.groupby("dec").anomaly_c.agg(["mean", "count"]).reset_index()

delta = dec.set_index("dec")["mean"][2020] - dec.set_index("dec")["mean"][1900]   # 2020-25 vs 1900s

# linear trend 1975-2025
s = d[d.year >= 1975]
slope = np.polyfit(s.year, s.anomaly_c, 1)
trend = np.polyval(slope, s.year)

BG, INK, MUTED = "#fbfaf7", "#1b1b1b", "#6b6b6b"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": MUTED})
fig = plt.figure(figsize=(15, 9.6), facecolor=BG)
gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 3.4, 1.7], width_ratios=[40, 1], hspace=0.22, wspace=0.02,
                      left=0.06, right=0.95, top=0.855, bottom=0.07)
ax0 = fig.add_subplot(gs[0, 0]); ax1 = fig.add_subplot(gs[1, 0], sharex=ax0); ax2 = fig.add_subplot(gs[2, 0])
cax = fig.add_subplot(gs[1, 1])
for a in (ax0, ax1, ax2, cax): a.set_facecolor(BG)

# 1 stripes
ax0.bar(d.year, 1, width=1.0, color=col, align="center")
ax0.set_xlim(1879.5, 2025.5); ax0.set_ylim(0, 1); ax0.axis("off")

# 2 annual anomalies
ax1.bar(d.year, d.anomaly_c, width=0.86, color=col)
ax1.plot(d.year, d.smooth, color=INK, lw=2.2, label="11-year centred average")
ax1.plot(s.year, trend, color=INK, lw=1.2, ls=(0, (4, 3)), label=f"Linear trend 1975–2025: +{slope[0]*10:.2f} °C per decade")
ax1.axhline(0, color=MUTED, lw=0.8)
ax1.set_ylim(-0.7, 1.75); ax1.set_ylabel("Anomaly vs 1951–1980 (°C)", color=INK)
ax1.set_yticks(np.arange(-0.5, 1.51, 0.5)); ax1.grid(axis="y", color="#e3e0da", lw=0.7); ax1.set_axisbelow(True)
for sp in ("top", "right"): ax1.spines[sp].set_visible(False)
ax1.tick_params(labelbottom=False, length=0)
ax1.set_xlim(1879.5, 2025.5)

def note(y, xt, yt, txt):
    v = d.set_index("year").anomaly_c[y]
    ax1.annotate(txt, (y, v), xytext=(xt, yt), ha="center", va="center", fontsize=9.5, color=INK,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=1))
note(1909, 1933, -0.6, "1909: −0.49 °C, coldest year")
note(1944, 1944, 0.52, "1944: +0.20")
note(1998, 1990, 0.95, "1998: +0.61\n(strong El Niño)")
note(2024, 2003, 1.62, "2024: +1.29, warmest year on record")
note(2025, 2012, 1.36, "2025: +1.19, 2nd warmest")
ax1.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 0.99))

# colourbar
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
cb = fig.colorbar(sm, cax=cax); cb.outline.set_visible(False)
cb.set_ticks([-0.5, 0, 0.5, 1.0]); cb.ax.tick_params(labelsize=9, length=2, colors=MUTED)
cb.set_label("°C vs 1951–1980", fontsize=9, color=MUTED)

# 3 decades
xl = [f"{x}s" if c == 10 else f"{x}–{str(x+c-1)[-2:]}" for x, c in zip(dec.dec, dec["count"])]
dcol = [cmap(norm(v)) for v in dec["mean"]]
ax2.bar(range(len(dec)), dec["mean"], width=0.72, color=dcol)
for i, v in enumerate(dec["mean"]):
    ax2.text(i, v + (0.05 if v >= 0 else -0.05), f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top",
             fontsize=9.5, color=INK)
ax2.set_xticks(range(len(dec))); ax2.set_xticklabels(xl, fontsize=10)
ax2.axhline(0, color=MUTED, lw=0.8); ax2.set_ylim(-0.6, 1.4)
ax2.set_yticks([-0.5, 0, 0.5, 1.0]); ax2.grid(axis="y", color="#e3e0da", lw=0.7); ax2.set_axisbelow(True)
ax2.set_ylabel("Decade mean (°C)", color=INK)
for sp in ("top", "right"): ax2.spines[sp].set_visible(False)
ax2.tick_params(axis="x", length=0)
ax2.set_title("Average by decade (2020s = 2020–2025 only)", loc="left", fontsize=11, color=INK, pad=6)

# header / footer
fig.text(0.06, 0.945, f"The 2020s are already about {delta:.1f} °C warmer than the 1900s", fontsize=22, fontweight="bold", color=INK, ha="left")
fig.text(0.06, 0.905, "Global mean surface temperature, land and ocean, 1880–2025. Each stripe / bar is one year, "
         "coloured by its departure from the 1951–1980 average.", fontsize=11.5, color=MUTED, ha="left")
fig.text(0.06, 0.035, "Source: NASA GISS Surface Temperature Analysis (GISTEMP v4), annual means (Jan–Dec), as redistributed by datahub.io/core/global-temp (CC-BY 4.0).",
         fontsize=8.5, color=MUTED, ha="left")
fig.text(0.06, 0.015, "Anomalies are relative to 1951–1980, not to pre-industrial (1850–1900), so they are not directly comparable with the 1.5 °C Paris Agreement threshold.",
         fontsize=8.5, color=MUTED, ha="left")
fig.savefig("global_temperature_chart.png", dpi=170, facecolor=BG)
print("trend per decade:", round(slope[0]*10, 3), "| delta 2020-25 vs 1900s:", round(delta, 2))
