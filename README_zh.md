# 动手教程：如何用脚本绘制 M–M Bond 随时间演化图

> **仓库用途**  
> 这是一个**可独立运行的 demo**，专门演示 `plot_MM_bond_time.py` 的用法。  
> 仓库已包含**原始数值结果**（NPZ / CSV）。不需要 GPU、不需要 OVITO、不需要完整 MD 轨迹，约 **1–3 秒**即可复现论文风格图。

---

## 你会完成什么

1. 安装最小 Python 依赖  
2. 用 `--plot-only` 运行脚本  
3. 从原始数据重新生成 `MM_bond_time.png` / `.svg` / `.csv`  
4. 看懂每一列数据含义  
5. （进阶）了解如何从 `dump.xyz` 重新计算  

**参考图**（仓库已附带；你的运行结果应与此一致）：

![M–M bonding vs time](MM_bond_time.png)

英文完整版说明见 [`README.md`](README.md)。

---

## 仓库里有什么

| 文件 / 目录 | 说明 |
|-------------|------|
| `plot_MM_bond_time.py` | 主脚本：读数据 / 作图（也可从轨迹重算） |
| `MM_bond_time_data.npz` | **原始结果**（6 个温度 × 400 帧） |
| `MM_bond_time_data.csv` | 同上，表格格式，方便 Excel / pandas |
| `MM_bond_time.png` / `.svg` | 参考图 |
| `MM_bond_time_methods.md` | 方法细节（中文） |
| `example_gpumd_run/` | 示例 GPUMD 输入、`thermo.out` 等 |
| `requirements.txt` | 依赖列表 |

> 完整 `dump.xyz` 轨迹体积很大，**本 demo 不附带**。画图所需统计量已在 NPZ/CSV 中。

---

## 环境要求

- Python **3.10+**（已在 3.13 测试）
- Windows / macOS / Linux 均可
- **不需要** GPU
- 内存 4 GB 以上即可

依赖：

```text
numpy>=1.22
matplotlib>=3.5
```

---

## 三步跑通 Demo

### 1. 克隆仓库

```bash
git clone https://github.com/JiaaoWANG-ut/mm-bond-hands-on-tutorial.git
cd mm-bond-hands-on-tutorial
```

### 2. 安装依赖

**Windows PowerShell：**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS：**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

安装通常 **1–3 分钟**。

### 3. 运行并出图

```bash
python plot_MM_bond_time.py --plot-only
```

成功时终端会打印：

```text
Saved: .../MM_bond_time_data.csv
Saved: .../MM_bond_time.png
Saved: .../MM_bond_time.svg
```

打开 `MM_bond_time.png`，应看到 6 条温度曲线（1500–3000 K）、对数时间轴、误差阴影带。运行时间约 **1–3 秒**。

---

## 命令说明

```bash
python plot_MM_bond_time.py --plot-only   # 推荐：只用仓库里的 NPZ 出图
python plot_MM_bond_time.py              # 有 NPZ 就读缓存；否则尝试算轨迹
python plot_MM_bond_time.py --force      # 强制从 dump.xyz 重算（需 OVITO + 轨迹）
```

---

## 原始数据怎么读

### CSV 列含义

| 列名 | 含义 |
|------|------|
| `temperature_K` | 温度 (K) |
| `time_ps` | 时间 (ps) |
| `frame_index` | 原轨迹帧号 |
| `n_pure` | 满足 M–M bond 判据的金属原子数 |
| `n_err` | 不确定度 \(\sqrt{n\_pure}\) |

### 用 Python 查看 NPZ

```python
import numpy as np
d = np.load("MM_bond_time_data.npz", allow_pickle=True)
print(d["temperatures"])
print(d["3000_times_ps"][:5], d["3000_n_pure"][:5])
```

---

## 物理判据（脚本在算什么）

对每个金属原子 \(M \in \{\mathrm{Fe},\mathrm{Co},\mathrm{Ni}\}\)：

- O 近邻：\(r < 2.5\) Å → \(\mathrm{CN_O}\)
- 金属近邻：\(r < 3.0\) Å → \(\mathrm{CN_{metal}}\)

计入 M–M bond 的条件：

```text
CN_O = 0  且  CN_metal > 0
```

即第一壳层**没有氧**，但仍有金属邻居。详见 [`MM_bond_time_methods.md`](MM_bond_time_methods.md)。

**结果 sanity check：**

- 1500–2000 K：计数接近 0  
- 2500 K：后期上升  
- 3000 K：更早、更强上升（可达 ~2000+）

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 缺 `numpy` / `matplotlib` | 激活虚拟环境后 `pip install -r requirements.txt` |
| `--plot-only` 报缺 NPZ | 从 git 恢复 `MM_bond_time_data.npz` |
| `--force` 报缺 `ovito` | 安装 OVITO，或继续用 `--plot-only` |
| 报找不到 dump | 本仓库无完整轨迹，请用 `--plot-only` |
| PowerShell 无法 Activate | 执行一次 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## 进阶：从轨迹重算

1. `pip install ovito`  
2. 按下面布局放置轨迹：

```text
1500K/gpumd/dump.xyz.gz
...
3000K/gpumd/dump.xyz
```

3. `python plot_MM_bond_time.py --force`

示例输入见 `example_gpumd_run/`（使用前请修改 `run.in` 里的 `potential` 路径）。

---

## 与完整代码包的关系

完整 Methods 代码中，对应目录为：

```text
Methods/M-M bonds/
```

本仓库把它拆成**独立教学 / software demo**：最小依赖 + 原始数值数据 + 一条命令出图。
