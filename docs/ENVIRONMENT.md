# 具身智能开发环境 (Embodied AI Dev Environment)

> 本机环境搭建完成于 2026-10-11

## 硬件配置

| 项目 | 配置 |
|---|---|
| CPU | Intel i7-7700HQ (4C8T) |
| 内存 | 7.6 GB + **8 GB Swap** |
| GPU | GTX 1050 Ti Mobile (4 GB, sm_61) |
| 驱动 | 580.178.04 / CUDA 13.0 |
| 系统盘 | 116 GB (88 GB 可用) |
| 数据盘 | `/data` 916 GB |

## 目录结构

```
项目仓库（代码与文档，本仓库）
/home/cyber/Documents/workspace/embodied-ai/my-repo/cybertronic-ros2-study/
├── check_env.py         # 环境一键验证
├── demo_pendulum.py     # 可运行示例
├── pyproject.toml       # 依赖声明
├── docs/ENVIRONMENT.md  # 本文件
└── .venv -> /data/...   # 软链接（已 gitignore）

/data/opt/               # 环境与大数据（不进版本库）
├── miniconda3/          # Miniconda 26.7.1 (base: Python 3.14)
├── uv-cache/            # uv 包缓存 5.2 GB
└── embodied-ai/.venv/   # Python 3.10.12 虚拟环境 5.6 GB（含 PyTorch CUDA）
```

> **注意**：`.venv` 是软链接，指向 `/data/opt/embodied-ai/.venv`。
> 虚拟环境不入库（`.gitignore` 已忽略），换机器需重建。

## 快速开始

```bash
cd /home/cyber/Documents/workspace/embodied-ai/my-repo/cybertronic-ros2-study
source .venv/bin/activate

python check_env.py       # 验证环境
python demo_pendulum.py   # 运行示例
```

## 已安装组件

### 基础工具链
- `build-essential` / `cmake` / `gcc 11.4`
- `python3-dev` / `python3-venv` / `pip`

### Python 环境管理（两套并存）
| 工具 | 版本 | 用途 |
|---|---|---|
| **uv** | 0.13.0 | 项目虚拟环境（首选，速度快） |
| **Miniconda** | 26.7.1 | 需要隔离 Python 版本时用 |

### 已装 Python 包
| 包 | 版本 | 说明 |
|---|---|---|
| gymnasium | 1.4.0 | RL 环境标准接口（Gym 继任者） |
| mujoco | 3.15.0 | DeepMind 物理引擎 |
| pybullet | 3.2.7 | 机器人仿真引擎 |
| numpy | 2.2.6 | 数值计算 |
| torch | 2.5.1+cu124 | 深度学习框架 |
| torchvision | 0.20.1 | 计算机视觉 |

### 镜像配置
- **pip**: 清华 TUNA (`~/.config/pip/pip.conf`)
- **conda**: 清华 TUNA (`~/.condarc`)
- **uv**: 清华 TUNA (`UV_DEFAULT_INDEX`)

## 常用命令

```bash
# 新增依赖（用 uv，装在项目 venv）
uv pip install <包名>

# 新建其他项目的虚拟环境
cd /path/to/project
uv venv --python /usr/bin/python3.10
source .venv/bin/activate

# conda 创建独立环境
conda create -n myenv python=3.11 -y
conda activate myenv
```

## 已知限制

1. **GPU 架构为 Pascal (sm_61)** — 部分新版框架已放弃支持：
   - PyTorch ≤ 2.5.x ✅ / 2.6+ ⚠️
   - **Isaac Lab / Isaac Sim ❌** (需 RTX 架构 sm_75+)
   - **Genesis ❌** (需更新架构)
2. **4 GB 显存** — 无法微调大模型，需云端
3. **推荐方案**：本地开发调试 + 云端 (AutoDL/vast.ai) 训练

## 适合本机的方向

- ✅ 经典 RL 算法 (PPO/SAC/DDPG)
- ✅ MuJoCo / PyBullet 仿真
- ✅ ROS 2 + Gazebo 机器人开发
- ✅ 模仿学习 / 行为克隆（小模型）
- ✅ 模型推理验证
