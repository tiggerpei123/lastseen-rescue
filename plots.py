"""Charts for the README and the pitch deck (needs matplotlib)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK, MUTED, GRID = "#15191C", "#5F686E", "#DCD8CC"
BASE, BASE2, ACCENT, ACCENT2 = "#A7ADB2", "#7D858B", "#E8A317", "#F0C76A"
BG = "#FFFFFF"


def _style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def benchmark_chart(summary: dict, path: str, n: int):
    order = [("nearest", "Current practice", BASE),
             ("nearest_k9", "Current practice + dog", BASE2),
             ("lastseen_no_cctv", "LastSeen, no CCTV", ACCENT2),
             ("lastseen", "LastSeen", ACCENT)]
    metrics = [("first_victim_mean_s", "First victim found (mean)"),
               ("each_victim_mean_s", "Each victim found (mean)"),
               ("all_victims_median_s", "All victims found (median)")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), facecolor=BG)
    xmax = max(summary[k][m] for k, _, _ in order for m, _ in metrics) * 1.18
    for ax, (m, title) in zip(axes, metrics):
        names = [lab for _, lab, _ in order]
        vals = [summary[k][m] for k, _, _ in order]
        cols = [c for _, _, c in order]
        ax.barh(names, vals, color=cols, height=0.62)
        for i, v in enumerate(vals):
            ax.text(v + xmax * 0.015, i, f"{v:.0f} s", va="center", color=INK, fontsize=10)
        ax.set_xlim(0, xmax)
        ax.invert_yaxis()
        ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold")
        _style(ax)
        if ax is not axes[0]:
            ax.set_yticklabels([])
    axes[0].tick_params(axis="y", labelcolor=INK, labelsize=10)
    fig.suptitle(f"Seconds from crew entry, {n} simulated fires (simulation, not field data)",
                 x=0.01, ha="left", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def example_map(building, cfg, scenario, pmap_p, panels: list, path: str):
    """One scenario, two panels (current practice vs LastSeen).

    panels: list of (title, route, use_map) - route is the list of searched rooms in order.
    Rooms show the order in which they were searched (first 6 searches); dots are trapped people.
    """
    import matplotlib.colors as mcolors
    from matplotlib.patches import FancyArrow, Rectangle

    cmap = mcolors.LinearSegmentedColormap.from_list("ls", ["#F7F4EC", "#F0C76A", "#E8A317", "#B4521E"])
    w = cfg.room_spacing_m
    length = building.rooms[cfg.rooms_per_side - 1].door_x + w / 2
    fig, axes = plt.subplots(len(panels), 1, figsize=(12, 4.0 * len(panels)), facecolor=BG)
    ymap = {"N": 2.0, "S": -6.0}
    for ax, (title, route, use_map) in zip(axes, panels):
        ax.add_patch(Rectangle((0, -2), length, 4.0, facecolor="#EEF0F1", edgecolor="none"))
        ax.text(0.6, 0, "ENTRY", color=MUTED, fontsize=8, rotation=90, va="center", ha="center")
        for r in building.rooms:
            y0 = ymap[r.side]
            face = cmap(min(pmap_p[r.index] / 0.6, 1)) if use_map else "#F2F2F0"
            ax.add_patch(Rectangle((r.door_x - w / 2, y0), w, 4.0, facecolor=face, edgecolor="#FFFFFF", linewidth=2))
            ax.text(r.door_x - w / 2 + 0.3, y0 + 3.3, r.name, color=INK, fontsize=9)
            if use_map:
                ax.text(r.door_x + w / 2 - 0.3, y0 + 3.3, f"{pmap_p[r.index]:.0%}", ha="right", color=INK, fontsize=8)
        for v in scenario.victims:
            r = building.rooms[v.room]
            ax.plot(r.door_x - 1.0 + 1.0 * (v.vid % 3), ymap[r.side] + 0.9, marker="o", markersize=8,
                    color=INK, markeredgecolor="#FFFFFF", markeredgewidth=1.5)
            if use_map and v.seen_on_cctv:
                y = -1.1 + 0.7 * (v.vid % 4)
                ax.add_patch(FancyArrow(v.last_seen_x, y, 2.2 * v.heading, 0, width=0.12, head_width=0.5,
                                        head_length=0.6, color=ACCENT, length_includes_head=True))
        order = {}
        for k, i in enumerate(route[:6]):
            order.setdefault(i, []).append(str(k + 1))
        for i, ks in order.items():
            r = building.rooms[i]
            ax.text(r.door_x, ymap[r.side] + 2.0, " · ".join(ks), ha="center", va="center", fontsize=11,
                    fontweight="bold", color="#FFFFFF",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=INK, edgecolor="none"))
        ax.set_xlim(-0.5, length + 0.5)
        ax.set_ylim(-6.5, 6.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold")
    fig.text(0.01, 0.01, "Dark labels = order of the first 6 room searches · dots = trapped people · "
             "arrows = CCTV last-seen position and heading · % = LastSeen's starting probability",
             color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)
