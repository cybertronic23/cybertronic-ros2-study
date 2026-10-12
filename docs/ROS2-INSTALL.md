# ROS 2 Humble 安装部署记录

> **安装日期**：2026-10-12
> **系统环境**：Ubuntu 22.04.5 LTS (jammy) / amd64
> **ROS 2 版本**：Humble Hawksbill
> **包版本**：`0.10.0-1jammy.20260908.101832`

---

## 1. 前置检查

ROS 2 Humble **仅支持 Ubuntu 22.04 (jammy)**，且 `locale` 必须是 UTF-8。

| 检查项 | 要求 | 本机实测 |
|---|---|---|
| Ubuntu 版本 | 22.04 jammy | ✅ 22.04.5 LTS |
| 架构 | amd64 | ✅ amd64 |
| locale | UTF-8 | ✅ `en_US.UTF-8` |
| 磁盘可用 | ≥ 10 GB | ✅ 88 GB |
| universe 仓库 | 启用 | ✅ 已启用 |

```bash
# 复现检查
. /etc/os-release && echo $VERSION_CODENAME   # 应输出 jammy
locale | grep LANG                             # 应含 UTF-8
df -h / | tail -1
```

### 如果 locale 不是 UTF-8

```bash
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
# 需重新登录生效
```

---

## 2. 安装步骤

### 2.1 启用 universe 仓库

```bash
sudo add-apt-repository -y universe
```

### 2.2 添加 ROS 2 GPG 密钥

ROS 2 要求 apt 源必须签名，密钥来自 `ros/rosdistro` 仓库：

```bash
# 用 keyring 文件（新版推荐，比 apt-key 安全）
sudo curl -sSL --proto '=https' --tlsv1.2 \
  https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

sudo chmod 644 /usr/share/keyrings/ros-archive-keyring.gpg
```

**验证**（应输出 `OpenPGP Public Key ... RSA 4096 bits`，1167 字节）：

```bash
file /usr/share/keyrings/ros-archive-keyring.gpg
ls -la /usr/share/keyrings/ros-archive-keyring.gpg
```

> ⚠️ **踩坑记录 #1：`sudo curl` 连接被拒**
>
> 现象：`curl: (7) Failed to connect to raw.githubusercontent.com port 443 ... Connection refused`
>
> 根因：`sudo` 默认会**清除 `http_proxy`/`https_proxy` 环境变量**（安全策略），
> 导致 curl 绕过本地代理（Clash `127.0.0.1:7890`）直连 GitHub，而该域名在国内被墙。
>
> 解决：**用普通用户下载（走代理），再用 sudo 移动**：
>
> ```bash
> export https_proxy=http://127.0.0.1:7890
> curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /tmp/ros.key
> sudo cp /tmp/ros.key /usr/share/keyrings/ros-archive-keyring.gpg
> sudo chmod 644 /usr/share/keyrings/ros-archive-keyring.gpg
> ```
>
> 国内备选源（同一把密钥，1167 字节一致）：
> - 清华：`https://mirrors.tuna.tsinghua.edu.cn/rosdistro/ros.key`
> - 中科大：`https://mirrors.ustc.edu.cn/rosdistro/ros.key`

### 2.3 添加 apt 软件源

国内建议直接使用**清华镜像**（官方 `packages.ros.org` 在国内速度慢且不稳定）：

```bash
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/ jammy main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list
```

写入后**务必确认内容正确**：

```bash
cat /etc/apt/sources.list.d/ros2.list
# 应输出：
# deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/ jammy main
```

> ⚠️ **踩坑记录 #2：管道顺序写错导致内容错误**
>
> 错误写法（`tee` 读到的是 `$PW` 而非 `deb` 行）：
> ```bash
> echo "deb ..." | echo "$PW" | sudo tee ros2.list   # ❌ 文件内容变成了密码
> ```
> 正确写法（先落地到临时文件，再复制）：
> ```bash
> cat > /tmp/ros2.list <<'EOF'
> deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/ jammy main
> EOF
> sudo cp /tmp/ros2.list /etc/apt/sources.list.d/ros2.list
> ```
>
> **教训**：`sudo tee` 是管道的**终点**，它读取的是**上一个命令**的输出。
> 涉及敏感信息时，永远先写临时文件再 sudo 复制，并事后 `grep` 验证。

**可选：禁用官方源避免重复**

```bash
sudo rm -f /etc/apt/sources.list.d/ros-official.list
```

### 2.4 更新索引

```bash
sudo apt update
```

**实测输出**（清华镜像速度）：

```
Get:6 https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy InRelease [4,682 B]
Get:7 https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy/main amd64 Packages [1,842 kB]
Fetched 1,847 kB in 2s (956 kB/s)
```

验证源已生效：

```bash
apt-cache policy ros-humble-desktop
```

```text
ros-humble-desktop:
  Installed: (none)
  Candidate: 0.10.0-1jammy.20260908.101832
  Version table:
     0.10.0-1jammy.20260908.101832 500
        500 https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy/main amd64 Packages
```

可搜索的 `ros-humble` 包数：**3672 个**

### 2.5 安装 ROS 2

三种发行版可选：

| 发行版 | 包名 | 体积 | 内容 |
|---|---|---|---|
| **桌面版**（推荐学习） | `ros-humble-desktop` | 下载 ~1.7 GB / 装后 164 MB | 核心 + RViz2 + 仿真工具 + 示例 |
| ROS Base | `ros-humble-ros-base` | ~1 GB | 核心 + 通信库，无 GUI 工具 |
| 按需 | `ros-humble-<pkg>` | 按需 | 只装指定功能包 |

```bash
# 桌面版
sudo apt install -y ros-humble-desktop
```

**安装规模**：总事务 `1932` 个包（含 Ubuntu 系统依赖），其中纯 `ros-humble-*` 为 **282 个**。

> 💡 建议在稳定网络下执行，或使用 `screen`/`tmux` 保持会话：
> ```bash
> sudo apt install -y ros-humble-desktop > /tmp/ros_install.log 2>&1
> ```

### 2.6 初始化 rosdep

`rosdep` 用于解析 ROS 包的系统依赖（apt/pip 等），几乎所有 ROS 包教程都会用到：

```bash
sudo apt install -y python3-rosdep python3-colcon-common-extensions

# 首次需要初始化（会写入 /etc/ros/rosdep）
sudo rosdep init

# 更新本地缓存（需要网络，会访问 raw.githubusercontent.com）
rosdep update
```

> ⚠️ `rosdep update` 访问 `raw.githubusercontent.com`，若被墙可挂代理：
> ```bash
> export https_proxy=http://127.0.0.1:7890
> rosdep update
> ```

---

## 3. 环境变量配置

ROS 2 安装在 `/opt/ros/humble/`，每个新终端都需要加载环境才能找到 `ros2` 命令。

```bash
echo '' >> ~/.bashrc
echo '# ===== ROS 2 Humble =====' >> ~/.bashrc
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

> ⚠️ **踩坑记录 #3：`ros2` 在脚本 / 非交互 shell 中找不到**
>
> 现象：在终端里 `ros2` 正常，但写成脚本执行（`bash -c`、`bash script.sh`、
> 定时任务、CI）时报 `ros2: command not found`。
>
> 根因：Ubuntu 的 `~/.bashrc` **开头有非交互式早退**：
> ```bash
> # If not running interactively, don't do anything
> case $- in
>     *i*) ;;
>       *) return;;      # ← 非交互 shell 到这里就退出了
> esac
> ```
> 若把 `source /opt/ros/humble/setup.bash` 追加到 `.bashrc` **末尾**，
> 非交互 shell 根本执行不到那一行。
>
> 解决：把 source 放到**早退判断之前**：
> ```bash
> # 插入到 "If not running interactively" 这段之前
> # ===== ROS 2 Humble（放在早退前，非交互 shell 也可用）=====
> if [ -f "/opt/ros/humble/setup.bash" ]; then
>     source "/opt/ros/humble/setup.bash"
> fi
> ```
>
> 💡 同理适用于 `conda`、`uv`、`nvm` 等任何需要加载环境的工具。
> 脚本中更稳妥的写法是**显式 source**：
> ```bash
> #!/usr/bin/env bash
> source /opt/ros/humble/setup.bash
> ros2 topic list
> ```

> 💡 **进阶**：如果创建了 colcon 工作区，还需 source 工作区的 `install/setup.bash`：
> ```bash
> source ~/ros2_ws/install/setup.bash
> ```
> 注意顺序：**先 ROS 环境，后工作区环境**。

---

## 4. 验证安装 ✅（2026-10-13 实测通过）

### 4.1 命令可用性

```bash
source /opt/ros/humble/setup.bash
ros2 --help
```

**实测结果**：

```text
/opt/ros/humble/bin/ros2
✅ ros2 命令正常
```

**已安装 18 个 CLI 子命令**：

```
action    bag       component daemon    doctor    interface launch   lifecycle
multicast node      param     pkg       plugin    run       security service
topic     wtf
```

**可用接口统计**：

| 类型 | 数量 |
|---|---|
| 消息 (`msg/`) | **205** |
| 服务 (`srv/`) | **52** |
| 动作 (`action/`) | **4** |

### 4.2 turtlesim 冒烟测试（GUI）

```bash
ros2 run turtlesim turtlesim_node    # 终端 1：启动小海龟
ros2 run turtlesim turtle_teleop_key # 终端 2：方向键控制
```

**实测输出**：

```text
[INFO] [turtlesim]: Starting turtlesim with node name /turtlesim
[INFO] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
```

```bash
ros2 node list
# /turtlesim

ros2 topic list
# /parameter_events
# /rosout
# /turtle1/cmd_vel
# /turtle1/color_sensor
# /turtle1/pose
```

✅ GUI 窗口正常弹出，节点与话题全部发现。

> 💡 若遇到 `Warning: Ignoring XDG_SESSION_TYPE=wayland`，可在 Wayland 下显式指定：
> ```bash
> QT_QPA_PLATFORM=wayland ros2 run turtlesim turtlesim_node
> ```

### 4.3 rosdep 数据更新

```bash
rosdep update
```

**实测结果**：

```text
Add distro "humble"
Add distro "jazzy" / "kilted" / "lyrical" / "rolling"
updated cache in /home/cyber/.ros/rosdep/sources.cache
```

本地缓存：**11 个文件**

> ⚠️ `rosdep update` 访问 `raw.githubusercontent.com`，国内需挂代理：
> ```bash
> export https_proxy=http://127.0.0.1:7890
> rosdep update
> ```

### 4.4 安装规模实测

| 指标 | 实测值 |
|---|---|
| `ros-humble-*` 已安装包数 | **282 个** |
| 实际安装体积（dpkg） | **164.3 MB** |
| `/opt/ros/humble` 占用 | 199 MB |
| apt 下载缓存 `/var/cache/apt/archives` | 1.5 GB |
| 根分区变化 | 88 G → 84 G（含依赖下载与缓存） |
| `ros-humble-desktop` 版本 | `0.10.0-1jammy.20260908.101832` |
| `rosdep` | 0.27.0 |
| `colcon` | 0.3.3 |

> 📌 **三个"包数"的区别**（避免混淆）：
>
> | 数字 | 含义 |
> |---|---|
> | 1932 | `apt install ros-humble-desktop` 时的**总事务数**，含 Ubuntu 系统依赖（`Inst`+`Conf` 行） |
> | **282** | 纯 `ros-humble-*` 已安装包（另有 2 个可选 RMW 实现为 `not-installed`） |
> | 3672 | `apt-cache search ros-humble` 可搜索到的**仓库内全部候选包** |
>
> 💡 **澄清体积**：网上常说 desktop 版"约 3 GB"，指的是**下载量**（含依赖 `.deb`）。
> 解压后实际只占 **164 MB**。磁盘紧张时可 `sudo apt clean` 释放 1.5 GB 缓存。

---

## 5. 常见问题排查

### 5.1 `ros2: command not found`

```bash
# 确认环境已加载
source /opt/ros/humble/setup.bash
which ros2
```
未写入 `~/.bashrc` 则按第 3 节配置。

### 5.2 `E: The repository ... does not have a Release file`

```bash
# 检查源文件内容是否正确
cat /etc/apt/sources.list.d/ros2.list
# 检查 GPG 密钥是否存在
ls -la /usr/share/keyrings/ros-archive-keyring.gpg
# 重新 update
sudo apt update
```

### 5.3 `GPG error: ... NO_PUBKEY`

密钥没装上或文件名与 `signed-by` 不匹配：

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
sudo apt update
```

### 5.4 `sudo` 下网络请求失败（代理失效）

`sudo` 会清除代理环境变量。解决：
- 方案 A：非 sudo 下载 → `sudo cp` 移动
- 方案 B：保留代理给 sudo
  ```bash
  sudo -E apt update        # -E 保留环境变量
  ```

### 5.5 中文乱码 / RViz 显示异常

```bash
sudo apt install -y fonts-wqy-microhei fonts-wqy-zenhei
```

---

## 6. 卸载（如需）

```bash
sudo apt remove --purge ros-humble-*
sudo rm /etc/apt/sources.list.d/ros2.list
sudo rm /usr/share/keyrings/ros-archive-keyring.gpg
sudo apt update
# 并从 ~/.bashrc 删除 source 行
```

---

## 7. 参考资料

- [ROS 2 Humble 安装文档（官方）](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)
- [清华大学 ROS 镜像](https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/)
- [rosdep 使用指南](https://docs.ros.org/en/humble/How-To-Guides/Using-rosdep.html)
- [colcon 构建工具](https://colcon.readthedocs.io/)

---

## 附：完整安装命令速查

```bash
# 1. 前置
sudo add-apt-repository -y universe

# 2. GPG 密钥（走代理下载）
export https_proxy=http://127.0.0.1:7890
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /tmp/ros.key
unset https_proxy
sudo cp /tmp/ros.key /usr/share/keyrings/ros-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/ros-archive-keyring.gpg

# 3. apt 源（清华镜像）
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null <<'EOF'
deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/ jammy main
EOF

# 4. 更新并安装
sudo apt update
sudo apt install -y ros-humble-desktop

# 5. rosdep
sudo apt install -y python3-rosdep python3-colcon-common-extensions
sudo rosdep init
rosdep update

# 6. 环境变量
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc

# 7. 验证
ros2 run turtlesim turtlesim_node
```
