# Cubazoid Solver 技术文档

## 1. 项目结构

```text
final project/
├─ cubazoid_solver.py          # 命令行入口（参数解析、批量/单例运行）
└─ cubazoid/
   ├─ __init__.py              # 对外导出 API
   ├─ types.py                 # 数据类型定义（Coord/Placement/PlacementOption）
   ├─ geometry.py              # 几何预处理：归一化、旋转、朝向生成、坐标转张量
   ├─ examples.py              # 组件库与测试案例（含 5/6/7 立方体案例）
   ├─ solver.py                # 两种求解后端（MRV 回溯 + Exact/DLX）
   ├─ visualization.py         # 3D 可视化动画
   └─ api.py                   # solve_and_visualize 统一调用入口
```

## 2. 核心算法

### 2.1 `mrv` 后端（默认）
- 思路：回溯搜索 + MRV（最小剩余值）选点。
- 关键点：
  - 预计算每个 piece 的所有合法放置；
  - 先做不可行快速判定（例如某块在空棋盘上无任何放置）；
  - 选择候选最少的空格展开分支；
  - 前向检查（剩余块是否仍有可行放置）；
  - 空洞连通分量剪枝；
  - 失败状态记忆化（含同型块计数压缩）。
- 优势：对当前问题规模（尤其 7x7x7）效果最好，工程上最稳。

### 2.2 `exact` 后端（DLX）
- 思路：将问题建模为 Exact Cover，使用 Algorithm X + 真正的 DLX 节点 `cover/uncover`。
- 当前实现特点：
  - 使用双向循环链表节点结构（列头/数据节点）；
  - 使用“同型组件计数”做对称性破坏，减少等价搜索；
  - 当前版本已移除 DLX 几何剪枝（保留纯 Exact Cover 路线）。
- 说明：DLX 在 Python 下对象操作开销较高，未必天然快于 MRV。

## 3. 命令行参数

`cubazoid_solver.py` 支持参数：

- `--all`：运行全部测试案例
- `--case <name>`：运行单个案例（默认 `hard_4x4x4_mixed_4blocks`）
- `--list-cases`：列出可用案例并退出
- `--include-large`：加入 5x5x5 / 6x6x6 / 7x7x7 大案例
- `--no-show`：关闭可视化窗口
- `--interval <ms>`：动画帧间隔（毫秒）
- `--backend {mrv,exact}`：选择求解后端（默认 `mrv`）

## 4. 常用命令

列出案例：

```powershell
python cubazoid_solver.py --list-cases --include-large
```

跑单个案例（MRV）：

```powershell
python cubazoid_solver.py --case search_7x7x7_mixed_balanced --include-large --backend mrv
```

跑单个案例（Exact/DLX）：

```powershell
python cubazoid_solver.py --case search_7x7x7_mixed_balanced --include-large --backend exact
```

批量运行（无窗口）：

```powershell
python cubazoid_solver.py --all --include-large --no-show
```

## 5. 7x7x7 性能记录（当前版本）

目标案例：`search_7x7x7_mixed_balanced`

- `mrv`（MRV + bitmask 放置判定）：约 **5.9s**（历史记录：`12.394s` / `12.459s`）
- `exact`（DLX，无几何剪枝）：约 **92.6s**（历史记录：`92.565s`）

结论（当前代码）：
- `mrv` 明显快于 `exact`；
- `exact` 仍可作为“方法学对比组”，用于报告中展示 Exact Cover/DLX 路线与启发式回溯路线的优劣差异。

## 6. 本轮修改摘要（2026-04-16）

本轮围绕“判题稳健性 + 搜索性能”做了以下更新：

- 无解返回语义统一：总体积不是完美立方时不再抛异常，统一由 `solve()` 返回 `None`；`--case reject_not_perfect_cube` 不再崩溃。
- 输入校验增强：
  - 若任一 piece 体素数不在 `[3,5]`，标记为不可行并返回 `None`；
  - 若 piece 非连通，发出 `UserWarning`（当前仍按“刚体组件”处理）。
- MRV 后端核心优化：
  - 预计算每个 placement 的 bitmask；
  - `_can_place` 从逐格循环改为按位与判冲突；
  - 记忆化状态键改为 `occupied_mask + 同型块计数`。
- 选点策略复核：尝试过 first-empty（左上角首空格）策略，但在 `search_7x7x7_mixed_balanced` 上实测明显变慢，因此已恢复为 MRV 选点（无残留）。

## 7. 复现实验建议

- 同一机器、同一 Python 版本下对比；
- 命令统一加 `--no-show`，避免图形窗口影响计时；
- 每个后端至少跑 3 次取中位数；
- 在报告中同时记录：
  - 解是否存在；
  - 总耗时；
  - 组件数量与立方体大小（n）。
