# -*- coding: utf-8 -*-
"""
408 知识凸包绘制
横轴：2009-2026 真题综合题考频（出现次数，来自历年考题分析汇总）
纵轴：综合难度（1-5，基于历年难度评级）
对四科分别求凸包，凸包顶点 = 该科"边界核心"知识点
"""
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
try:
    sys.path.insert(0, r"D:\Users\MECHREVO\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\python")
    from daimon_runtime import setup_plot
    setup_plot()
except Exception:
    # 回退：系统 Python 直接配置中文字体
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans SC"]
    matplotlib.rcParams["axes.unicode_minus"] = False

import matplotlib.pyplot as plt
import numpy as np

# (名称, 考频, 难度, 科目)  —— 坐标有 0.1 级微调以避免标注重叠
DATA = [
    # 数据结构
    ("图算法 DFS/BFS/Dijkstra", 5, 5.0, "DS"),
    ("灵活算法设计", 3, 5.0, "DS"),
    ("排序算法代码", 5, 4.0, "DS"),
    ("二叉树 / BST", 5, 3.7, "DS"),
    ("栈与队列应用", 3, 2.0, "DS"),
    # 计算机组成原理
    ("CPU 数据通路设计", 7, 5.0, "CO"),
    ("Cache 与存储层次", 5, 4.2, "CO"),
    ("指令流水线", 3, 4.0, "CO"),
    ("指令系统设计", 2, 4.0, "CO"),
    # 操作系统
    ("P/V 操作与进程同步", 6, 4.0, "OS"),
    ("内存管理与页面置换", 5, 3.0, "OS"),
    ("文件系统", 6, 2.9, "OS"),
    ("进程调度分析", 1, 3.0, "OS"),
    # 计算机网络
    ("TCP 连接与拥塞控制", 6, 3.3, "CN"),
    ("IP 子网划分/路由聚合", 6, 2.0, "CN"),
    ("时延计算", 5, 2.2, "CN"),
]

SUBJECTS = {
    "DS": ("数据结构 · 45分", "#c0392b"),
    "CO": ("组成原理 · 45分", "#1f6f8b"),
    "OS": ("操作系统 · 35分", "#6a8e3f"),
    "CN": ("计算机网络 · 25分", "#b8860b"),
}


def convex_hull(points):
    """单调链算法，points: [(x, y), ...]，返回凸包顶点（逆时针，不含重复终点）"""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


fig, ax = plt.subplots(figsize=(13, 8.5))

for sub, (label, color) in SUBJECTS.items():
    pts = [(f, d) for _, f, d, s in DATA if s == sub]
    names = {(f, d): n for n, f, d, s in DATA if s == sub}
    hull = convex_hull(pts)

    # 凸包多边形
    if len(hull) >= 3:
        poly = np.array(hull + [hull[0]])
        ax.fill(poly[:, 0], poly[:, 1], color=color, alpha=0.10, zorder=1)
        ax.plot(poly[:, 0], poly[:, 1], color=color, lw=2.0, alpha=0.85, zorder=2)

    hull_set = set(hull)
    for (f, d) in pts:
        is_vertex = (f, d) in hull_set and len(hull) >= 3
        ax.scatter(f, d, s=260 if is_vertex else 110,
                   color=color, edgecolor="white", linewidth=1.4,
                   marker="*" if is_vertex else "o",
                   alpha=0.95 if is_vertex else 0.75, zorder=3)
        name = names[(f, d)]
        weight = "bold" if is_vertex else "normal"
        size = 11.5 if is_vertex else 9.5
        ax.annotate(name, (f, d), textcoords="offset points",
                    xytext=(10, 8), fontsize=size, fontweight=weight,
                    color=color, zorder=4)

    # 图例代理
    ax.scatter([], [], color=color, marker="s", s=120, label=label)

ax.set_xlabel("考频：2009—2026 真题综合题出现次数 →", fontsize=13)
ax.set_ylabel("综合难度（★1—5）→", fontsize=13)
ax.set_title("考研 408 知识凸包：四科核心考点的边界\n"
             "（★ = 凸包顶点，即该科必须攻克的边界知识点）",
             fontsize=16, fontweight="bold", pad=14)
ax.set_xlim(0, 8)
ax.set_ylim(1.2, 5.7)
ax.set_xticks(range(0, 9))
ax.grid(alpha=0.25, linestyle="--")
ax.legend(loc="lower right", fontsize=11, framealpha=0.9)

fig.text(0.01, 0.01, "数据来源：408计算机统考历年真题（2009—2026）考频统计",
         fontsize=9, color="gray")

out = Path(__file__).parent / "408知识凸包.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print("saved:", out)

# 打印各科凸包顶点，供笔记撰写核对
for sub, (label, _) in SUBJECTS.items():
    pts = [(f, d) for _, f, d, s in DATA if s == sub]
    hull = convex_hull(pts)
    names = {(f, d): n for n, f, d, s in DATA if s == sub}
    print(f"\n[{label}] 凸包顶点：")
    for p in hull:
        print(f"  - {names.get(p, p)} (考频{p[0]}, 难度{p[1]})")
