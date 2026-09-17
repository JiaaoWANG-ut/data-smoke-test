# M–M Bond 时间演化统计方法

**体系**：ternay-FeCoNi-2（Fe / Co / Ni / O 四元纳米体系）  
**分析脚本**：`plot_MM_bond_time.py`  
**生成日期**：2026-07-01

---

## 1. 数据来源

| 温度 (K) | 轨迹文件 |
|---------|---------|
| 1500 | `{T}K/gpumd/dump.xyz.gz` |
| 1600 | `{T}K/gpumd/dump.xyz.gz` |
| 1800 | `{T}K/gpumd/dump.xyz.gz` |
| 2000 | `{T}K/gpumd/dump.xyz` |
| 2500 | `{T}K/gpumd/dump.xyz.gz` |
| 3000 | `{T}K/gpumd/dump.xyz` |

- 模拟软件：GPUMD  
- 每条轨迹共 **2500 帧**  
- 输出间隔：`dump_exyz 2000`，`time_step 1 fs` → 相邻帧间隔 **2 ps**  
- 总模拟时长：**2–5000 ps**  
- 读取工具：OVITO Python (`ovito.io.import_file`)  
- 对 `.gz` 轨迹采用 **顺序逐帧读取**，避免 gzip 随机跳帧解析错误

---

## 2. 帧采样

从每条轨迹的 2500 帧中 **均匀抽取 400 帧**：

```
frame_index = round(linspace(0, 2499, 400))
```

- 6 条温度曲线 × 400 帧 = **2400 个统计点**  
- 时间轴取各帧 GPUMD 属性 `Time`（单位 fs），换算为 ps：

```
t (ps) = Time × 1.0 / 1000
```

---

## 3. M–M Bond 定义

对每一帧、每一个金属原子 **M ∈ {Fe, Co, Ni}**，统计其第一配位壳层：

| 符号 | 含义 | 截断半径 |
|------|------|---------|
| CN_O | M 的 O 近邻数 | r < **2.5 Å** |
| CN_metal | M 的金属近邻数（Fe/Co/Ni） | r < **3.0 Å** |

**判定为 M–M bond 原子的条件**（金属纯配位壳层）：

```
CN_O = 0   且   CN_metal > 0
```

即：第一壳层 **不含 O**，且 **至少有一个金属邻居**。

**单帧统计量** `n_pure`：满足上述条件的金属原子 **总数**（Fe + Co + Ni 合并计数）。

近邻搜索使用 OVITO `CutoffNeighborFinder`，自动考虑 **周期性边界条件 (PBC)**。

---

## 4. 不确定度（误差带）

对每个采样帧，计数 `N = n_pure` 视为 Poisson 过程，标准差取：

```
σ = √N        (N > 0)
σ = 0         (N = 0)
```

作图中误差带为 **[N − σ, N + σ]**，下界截断为 0。  
阴影透明度 α = 0.42。

---

## 5. 作图设置

| 项目 | 设置 |
|------|------|
| 横轴 | 时间 (ps)，**对数坐标** |
| 纵轴 | M–M bond count，**线性坐标** |
| 曲线 | 6 条，对应 1500–3000 K |
| 配色 | `coolwarm`：低温蓝 → 高温红 |
| 图例 | 左上角 |
| 风格 | Nature 风格（Arial/Helvetica，细轴线，600 dpi） |
| 输出尺寸 | 4.6 × 2.8 inch |

---

## 6. 输出文件说明

| 文件 | 说明 |
|------|------|
| `MM_bond_time.png` | 位图 (600 dpi) |
| `MM_bond_time.svg` | 矢量图 |
| `MM_bond_time_data.csv` | 原始数据（长表，2400 行） |
| `MM_bond_time_data.npz` | NumPy 压缩格式，内容与 CSV 一致 |
| `MM_bond_time_methods.md` | 本文档 |
| `plot_MM_bond_time.py` | 分析/作图可复现脚本 |

### CSV 列说明

| 列名 | 类型 | 说明 |
|------|------|------|
| `temperature_K` | int | 模拟温度 (K) |
| `time_ps` | float | 帧时间 (ps) |
| `frame_index` | int | 轨迹中的帧序号 (0–2499) |
| `n_pure` | int | 满足 M–M bond 判据的原子数 |
| `n_err` | float | Poisson 不确定度 σ = √n_pure |

---

## 7. 复现命令

```bash
# 从缓存 NPZ 重绘（快速）
python3 plot_MM_bond_time.py --plot-only

# 从 dump.xyz 重新计算全部轨迹（约 5 min）
python3 plot_MM_bond_time.py --force
```

依赖：`numpy`, `matplotlib`, `ovito`

---

## 8. 结果概览

| 温度 (K) | n_pure 范围 | 非零帧数 / 400 |
|---------|------------|---------------|
| 1500 | 0 | 0 |
| 1600 | 0–1 | 2 |
| 1800 | 0–2 | 6 |
| 2000 | 0–6 | 119 |
| 2500 | 0–648 | 395 |
| 3000 | 2–2408 | 400 |

低温下 M–M bond 计数接近 0，符合氧化物界面占主导、金属纯配位壳层极少的物理图像；2500 K 及以上随时间显著增加，反映高温合金化与金属配位环境扩展。
