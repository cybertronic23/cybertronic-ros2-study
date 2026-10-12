#!/usr/bin/env python3
"""
具身智能开发环境 - 一键验证脚本
用法: python check_env.py
"""
import sys
import platform
from importlib import metadata

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
results = []


def check(name, fn):
    try:
        detail = fn()
        results.append((True, name, detail or ""))
        print(f"  {GREEN}✓{RESET} {name:<28} {detail}")
    except Exception as e:
        results.append((False, name, str(e)))
        print(f"  {RED}✗{RESET} {name:<28} {str(e)[:90]}")


def ver(pkg):
    from importlib import metadata
    try:
        return metadata.version(pkg)
    except Exception:
        raise RuntimeError("未安装")


print("=" * 72)
print("  具身智能开发环境检查")
print("=" * 72)

print(f"\n{YELLOW}[系统]{RESET}")
check("Python", lambda: f"{sys.version.split()[0]} ({platform.machine()})")
check("平台", lambda: f"{platform.system()} {platform.release()}")

print(f"\n{YELLOW}[深度学习 / GPU]{RESET}")


def check_torch():
    import torch
    line = f"{torch.__version__}"
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        cap = torch.cuda.get_device_capability(0)
        line += f" | CUDA {torch.version.cuda} | {name} sm_{cap[0]}{cap[1]}"
    else:
        line += " | ⚠ CUDA 不可用(将退回CPU)"
    return line


def gpu_matmul():
    import torch
    if not torch.cuda.is_available():
        return "跳过（无CUDA）"
    x = torch.randn(2000, 2000, device="cuda")
    y = (x @ x).sum().item()
    return f"GPU矩阵乘 OK (sum={y:.2f})"


check("PyTorch", check_torch)
check("GPU 计算验证", gpu_matmul)
check("torchvision", lambda: ver("torchvision"))

print(f"\n{YELLOW}[仿真环境]{RESET}")
check("gymnasium", lambda: ver("gymnasium"))
check("MuJoCo", lambda: ver("mujoco"))
check("PyBullet", lambda: ver("pybullet"))


def mujoco_smoke():
    import mujoco
    m = mujoco.MjModel.from_xml_string(
        '<mujoco><worldbody><body><joint/><geom size=".1"/></body></worldbody></mujoco>'
    )
    d = mujoco.MjData(m)
    for _ in range(100):
        mujoco.mj_step(m, d)
    return f"100步仿真 OK (t={d.time:.3f}s)"


def pybullet_smoke():
    import pybullet as p
    c = p.connect(p.DIRECT)
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf") if False else None
    p.disconnect()
    return "连接 OK (无头模式)"


check("MuJoCo 运行", mujoco_smoke)
check("PyBullet 运行", pybullet_smoke)

print(f"\n{YELLOW}[数值 / 工具]{RESET}")
check("NumPy", lambda: ver("numpy"))
check("SciPy", lambda: ver("scipy"))
check("Matplotlib", lambda: ver("matplotlib"))

print("\n" + "=" * 72)
ok = sum(1 for r in results if r[0])
total = len(results)
failed = [r for r in results if not r[0]]

if not failed:
    print(f"  {GREEN}全部通过 {ok}/{total} — 环境就绪，可以开始开发！{RESET}")
else:
    print(f"  {YELLOW}通过 {ok}/{total}，以下需要处理：{RESET}")
    for _, name, detail in failed:
        print(f"    - {name}: {detail}")
print("=" * 72)
sys.exit(0 if not failed else 1)
