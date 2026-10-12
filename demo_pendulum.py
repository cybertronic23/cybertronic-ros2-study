#!/usr/bin/env python3
"""
最小可运行示例：用 Gymnasium + MuJoCo 跑一个带物理仿真的机器人环境。
运行: python demo_pendulum.py
"""
import numpy as np
import mujoco
import gymnasium as gym

# ---- 1. 纯 MuJoCo 物理仿真 ----
print("=" * 60)
print("示例 1: MuJoCo 底层物理仿真")
print("=" * 60)

XML = """
<mujoco model="two_link_arm">
  <option timestep="0.002" gravity="0 0 -9.81">
    <flag contact="enable"/>
  </option>
  <worldbody>
    <geom type="plane" size="3 3 0.1" rgba="0.75 0.75 0.8 1"/>
    <light pos="0 0 3" dir="0 0 -1"/>
    <body name="link1" pos="0 0 0.1">
      <joint name="shoulder" type="hinge" axis="0 0 1" range="-3.14 3.14"/>
      <geom type="capsule" fromto="0 0 0 0.4 0 0" size="0.04"
            rgba="0.2 0.6 0.9 1" mass="1"/>
      <body name="link2" pos="0.4 0 0">
        <joint name="elbow" type="hinge" axis="0 0 1" range="-2.5 2.5"/>
        <geom type="capsule" fromto="0 0 0 0.3 0 0" size="0.035"
              rgba="0.9 0.4 0.2 1" mass="0.8"/>
        <site name="tip" pos="0.3 0 0" size="0.02" rgba="0 1 0 1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="shoulder_motor" joint="shoulder" ctrlrange="-5 5" gear="5"/>
    <motor name="elbow_motor" joint="elbow" ctrlrange="-5 5" gear="5"/>
  </actuator>
</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)

print(f"  模型: 2连杆机械臂 | 自由度 nq={model.nq} | 关节数={model.njnt}")
print(f"  时间步长 = {model.opt.timestep}s")

# 施加关节力矩，观察运动
rng = np.random.default_rng(0)
for i in range(2000):  # 4 秒仿真
    data.ctrl[:] = rng.uniform(-2.0, 2.0, size=model.nu)
    mujoco.mj_step(model, data)

tip = data.site_xpos[0] if model.nsite else [0, 0, 0]
print(f"  施加随机力矩 2000 步 (4.0s)")
print(f"  末端执行器位置: ({tip[0]:+.4f}, {tip[1]:+.4f}, {tip[2]:+.4f}) m")
print(f"  关节角度: shoulder={data.qpos[0]:+.3f} rad, elbow={data.qpos[1]:+.3f} rad")
print("  ✓ 物理仿真正常\n")

# ---- 2. Gymnasium 标准 RL 环境 ----
print("=" * 60)
print("示例 2: Gymnasium 强化学习环境交互")
print("=" * 60)

env = gym.make("Pendulum-v1")
obs, info = env.reset(seed=42)
print(f"  环境: Pendulum-v1 (倒立摆)")
print(f"  观测空间: {env.observation_space.shape} | 动作空间: {env.action_space.shape}")

returns, steps = [], 0
for episode in range(3):
    obs, _ = env.reset(seed=episode)
    total, steps = 0.0, 0
    while True:
        action = env.action_space.sample()  # 随机策略
        obs, reward, terminated, truncated, info = env.step(action)
        total += reward
        steps += 1
        if terminated or truncated:
            break
    returns.append(total)
    print(f"  第 {episode+1} 回合: {steps} 步, 累计奖励 = {total:.2f}")

env.close()
print(f"  平均奖励 = {np.mean(returns):.2f}")
print("  ✓ RL 环境交互正常\n")

print("=" * 60)
print("  🎉 所有示例运行成功！环境已就绪")
print("=" * 60)
