# 辐射功能全景 · 连线锚点

金样（连线精度以这两份为准，后画先对齐）：

1. 本地：`20261005.230909.Windows.Driver/hellowdf-inf-function-map.md` §2 内联 SVG
2. 飞书人工精调：<https://rigolportal.feishu.cn/docx/YUV4dM9N1oTG3ExKMYScQBgSnVh>

## 两类虚线

| 类型 | 条数 | 起点 | 终点 | 装饰 |
|------|------|------|------|------|
| 卡组 → 卫星 | 每簇外侧卡 1 条 | 该卫星全部卡的**簇心** | 卫星六边形**外边缘**（朝向簇心一侧） | 终点 `marker-end`，无菱形 |
| 卫星 → 中心 | 每颗卫星 1 条 | 卫星六边形**外边缘**（朝向中心一侧） | 中心六边形**外边缘**（朝向该卫星一侧） | 卫星侧锚点放 **4px 菱形**；中心侧 `marker-end` |

禁止中心↔中心、卫星↔卫星、卡中心直戳对方几何心。禁止线穿过任一六边形内部或压在卡片文字上。

## flat-top 六边形

与金样一致：上下为水平边。中心 `(cx, cy)`，半宽 `a`、半高 `b`（卫星常用 `a≈36`、`b≈42`；中心加大 `a≈66`、`b≈51`）。

六个顶点（顺时针从顶开始）：

`(cx, cy-b) → (cx+a, cy-b/2) → (cx+a, cy+b/2) → (cx, cy+b) → (cx-a, cy+b/2) → (cx-a, cy-b/2)`

`polygon points` 必须与上述一致；锚点从顶点反推，不要与 polygon 脱节。

## 射线 — 六边形交点

给定六边形中心 `C`、外参考点 `P`（簇心或另一颗六边形心），要从 **C 沿 `P→C` 方向** 走到边界（卫星←卡）或 **C 沿 `C→P` 方向**（卡→卫星、卫星→中心）时：

1. 单位方向 `u = normalize(P - C)` 或 `normalize(C - P)`，与连线 `M… L…` 一致。
2. 射线 `C + t·u`（`t>0`）与六条边线段求交，取 **最小正 t** 的交点为边锚点。
3. `path` 的对应端点用该交点坐标（整数四舍五入）。

边线段：顶点 `Vi` 到 `V(i+1)%6`。

无脚本时，先摆好六边形，再在目测象限内微调 1～2px，但终点仍须落在边上；与金样同方位的卫星应对齐相同象限的边（上/下/左肩/右肩），不要挤在尖角顶点。

## 卡组簇心

该卫星名下每个 `rect` 的中心 `(x+w/2, y+h/2)` 取算术平均。多列多行卡组仍只出一条线到卫星（不要每张卡一条）。

顶栏下的 Version 卡等：簇心指向 **上侧卫星** 时，线从簇心向上落到该卫星**底边或下肩边**，不要横穿顶栏胶囊。

## SVG marker

在 `<defs>` 内按虚线色各一个（id 建议带图前缀防冲突）：

```xml
<marker id="hfm-aB" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
  <path d="M0,0 L8,4 L0,8 Z" fill="#58A6FF"/>
</marker>
```

- 橙 `#F18F01`、紫 `#C4B5FD` 同理。
- `refX="7"` 使三角贴在六边形外缘，不插入填充区。
- 需要箭头的一端必须是**六边形外锚点**，不是中心。

虚线： `stroke-dasharray="5 4"` `stroke-width="1.6"` `fill="none"`。

卫星→中心线在卫星侧锚点追加菱形（边长 8，菱形尖对准中心）：

```xml
<polygon points="px,py-4 px+4,py px,py+4 px-4,py" fill="#58A6FF"/>
```

`fill` 与该案虚线色相同。

## 可选：本地算交点

需要批量改线时，在草稿里跑（不改变交卷 md 里的空行禁令）：

```python
def hex_flat_top(cy, a, b):
    cx = 0  # 调用时加回 cx
    return [
        (0, -b), (a, -b / 2), (a, b / 2), (0, b), (-a, b / 2), (-a, -b / 2)
    ]

def ray_hex_intersect(cx, cy, a, b, ux, uy, outward=True):
    verts = [(cx + vx, cy + vy) for vx, vy in hex_flat_top(cy, a, b)]
    best = None
    for i in range(6):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 6]
        # 射线 cx,cy + t*(ux,uy) 与边 x1,y1-x2,y2
        dx, dy = x2 - x1, y2 - y1
        det = ux * dy - uy * dx
        if abs(det) < 1e-9:
            continue
        t = ((x1 - cx) * dy - (y1 - cy) * dx) / det
        s = ((x1 - cx) * uy - (y1 - cy) * ux) / det
        if t > 1e-6 and 0 <= s <= 1 and (best is None or t < best[0]):
            best = (t, cx + t * ux, cy + t * uy)
    if best is None:
        raise ValueError("no hit")
    return round(best[1]), round(best[2])

def anchor_from_point(cx, cy, a, b, px, py, from_center=True):
    import math
    dx, dy = (px - cx, py - cy) if from_center else (cx - px, cy - py)
    L = math.hypot(dx, dy) or 1
    return ray_hex_intersect(cx, cy, a, b, dx / L, dy / L)
```

`from_center=True`：从中心指向外点（卡→卫星时在卫星上取点）；`False`：外点指向中心（卫星→中心起点）。

## 画完自检

- [ ] 任意缩放至 150%，无线条穿过六边形填色区
- [ ] 卡组线只连所属卫星，卫星线只连中心
- [ ] 同卫星仅一条对中心线，菱形在卫星肩线而非中心
- [ ] marker 箭头贴在边外缘，不插入玫红中心块
