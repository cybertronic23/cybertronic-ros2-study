# cybertronic-ros2-study

About ROS2 study —— ROS 2 学习记录与具身智能相关代码、文档。

## 目录结构

```
.
├── README.md                 # 本文件
├── pyproject.toml            # Python 依赖声明
├── check_env.py              # 开发环境体检脚本（13 项检查）
├── demo_pendulum.py          # 可运行示例：MuJoCo 机械臂 + Gymnasium
├── docs/
│   ├── ENVIRONMENT.md        # 基础开发环境（Python/CUDA/仿真）
│   └── ROS2-INSTALL.md       # ROS 2 Humble 安装部署全过程
├── .venv -> /data/...        # 虚拟环境软链接（本地，已被 gitignore）
└── LICENSE
```

## 快速开始

```bash
cd /home/cyber/Documents/workspace/embodied-ai/my-repo/cybertronic-ros2-study
source .venv/bin/activate

python check_env.py       # 环境体检
python demo_pendulum.py   # 运行示例
```

ROS 2 环境（每个新终端）：

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

> ⚠️ `.venv` 是指向 `/data/opt/embodied-ai/.venv` 的**软链接**，不随仓库分发。
> 换机器后请参照 [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) 重建环境。

## 开发环境

| 项目 | 配置 |
|---|---|
| 系统 | Ubuntu 22.04.5 LTS |
| CPU / RAM | i7-7700HQ (4C8T) / 7.6 GB + 8 GB Swap |
| GPU | GTX 1050 Ti Mobile (4 GB, sm_61) |
| Python | 3.10.12（uv 虚拟环境） |
| PyTorch | 2.5.1+cu124（CUDA 可用） |
| 仿真 | MuJoCo 3.15.0 / PyBullet 3.2.7 / Gymnasium 1.4.0 |
| **ROS 2** | **Humble** `0.10.0-1jammy.20260908`（282 包 / 164 MB） |

**环境管理工具**：[uv](https://docs.astral.sh/uv/) 0.13.0（首选）+ Miniconda 26.7.1 + `rosdep` 0.27.0 + `colcon` 0.3.3

详见 [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)、[docs/ROS2-INSTALL.md](docs/ROS2-INSTALL.md)。

## 计划

- [x] ROS 2 Humble 安装与基础概念 → [docs/ROS2-INSTALL.md](docs/ROS2-INSTALL.md)
- [ ] Topic / Service / Action 通信实践
- [ ] TF2 坐标变换
- [ ] URDF 机器人建模
- [ ] Nav2 导航栈
- [ ] 仿真环境集成（Gazebo / MuJoCo）

## License

MIT
