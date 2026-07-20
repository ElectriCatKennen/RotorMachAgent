# RotorMachAgent

> 旋转机械智能设计 Agent —— 让 LLM 通过工具调用驱动 SOLIDWORKS/AutoCAD/Ansys 等工程软件，完成从设计输入到建模到输出的全链路协同

[![Status](https://img.shields.io/badge/status-WIP-orange)]()
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue)]()

---

## 项目定位

**RotorMachAgent** 是一个面向旋转机械（化工搅拌器、泵、涡轮等）的智能设计 Agent 工具层。它将工程软件的 API 包装为可被 LLM Agent 调用的工具，实现：

```
设计输入（自然语言/参数表/标准件规格）
        ↓  LLM Agent 调用工具
设计建模（SOLIDWORKS 原生参数化建模，保留特征树）
        ↓  工具输出
设计输出（.sldprt + 工程图 + BOM + 可选 CFD 网格）
```

**不依赖中间格式建模**。现有方案多走程序化建模路线，输出 STEP 等中性文件格式，丢失参数化特征树。RotorMachAgent 输出 SW 原生文件，工程师可在 SW 中继续编辑和二次开发。

## 核心差异化

| 卖点 | 说明 | 对比现有方案 |
|------|------|-------------|
| **SW 原生特征树** | 输出 .sldprt 保留草图/特征/约束，可继续编辑 | STEP 路线丢失特征树 |
| **Agent 工具层** | 工具化设计，不绑定具体 LLM，可被各类 Agent 调用 | 闭源 SaaS 不提供工具化接口 |
| **中文机械场景** | 适配中文版 SW 命名、GB 标准件、国标键槽/挡圈槽 | 现有方案普遍缺乏中文场景适配 |
| **CFD 联动** | 参数化几何 → Fluent 网格，仿真驱动设计 | 其他项目无仿真闭环 |

## 当前状态（WIP）

- ✅ 已验证：Python + pywin32 + comtypes 调用 SW API 完成阶梯轴建模
- ✅ 已完成：数据与代码分离（GB 标准数据提取为 JSON）
- ✅ 已完成：数据加载器（统一读取接口，包内数据）
- ✅ 已完成：平键模型（GB/T 1096，A/B/C 型）
- ✅ 已完成：标准直径系列圆整（GB/T 2822）
- ✅ 已完成：许用扭矩/弯矩计算、轴强度计算模块
- 🚧 进行中：参数化零件生成器（ShaftBuilder + 轴要素元类体系）
- ❌ 待做：MCP Server、工程图自动生成、多软件协同

**架构决策**：MVP 阶段不开发 GUI，仅提供 **MCP + CLI** 接口，面向 LLM Agent 调用。

详见 [使用指南](docs/使用指南.md)。

## 目录结构

```
RotorMachAgent/
├── README.md                       # 项目介绍（本文件）
├── CLA.md                          # 贡献者许可协议
├── CONTRIBUTING.md                 # 贡献指南
├── LICENSE                         # AGPL-3.0
├── requirements.txt                # Python 依赖
├── docs/                           # 公开文档（PPT式亮点呈现）
│   ├── 使用指南.md                 # 外部接口使用教程
│   ├── 应用场景.md                 # 使用场景与案例
│   ├── 技术栈.md                   # 技术栈概览
│   └── 参考标准.md                 # 引用的GB标准列表
├── tests/                          # 验证脚本（可作为使用示例）
│   ├── adapters/                   # 适配器测试
│   ├── calculations/               # 计算模块测试
│   └── standards/                  # 标准数据测试
├── src/                            # 源码（核心实现，开源）
│   ├── adapters/                   # 工程软件适配器（SW/ACAD/ANSYS）
│   ├── parts/                      # 参数化零件模板（轴/座/桨叶/罐体）
│   ├── assemblies/                 # 装配体构建与工程图
│   ├── calculations/               # 工程计算（功率/轴径/轴承/罐体）
│   ├── standards/                  # GB 标准件库（键/挡圈/螺纹/轴承）
│   ├── tools/                      # Agent 工具封装（MCP 协议）
│   ├── agents/                     # Agent 工作流与 MCP Server
│   └── data/                       # 包内数据（GB标准JSON，随包分发）
└── examples/                       # 示例（待建）
```

## 快速开始

### 环境要求

- **操作系统**：Windows 10/11（SW COM 接口限制）
- **Python**：3.10+（推荐 3.11）
- **SOLIDWORKS**：2023+（已验证 2023 SP5.0）

### 安装（推荐 conda）

```bash
# 1. 创建 conda 环境
conda create -n rotormachagent python=3.11
conda activate rotormachagent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证 SW API 连接
python tests/adapters/test_solidworks_adapter.py

# 4. 验证标准数据加载
python tests/standards/test_data_loader.py
```

### 关键依赖

| 依赖 | 用途 | 必需性 |
|------|------|-------|
| `pywin32` | Windows COM 接口（Dispatch） | 必需 |
| `comtypes` | COM vtable 调用（FeatureCut3 等多参数方法） | 必需 |
| `pandas` | 数据处理（BOM/规格表） | 必需 |
| `scipy` | 科学计算（数值积分、优化） | 必需 |
| `sympy` | 符号计算（公式推导） | 必需 |
| `openpyxl` | Excel 读写（参数表、BOM） | 必需 |
| `python-mcp` | MCP 协议（Agent 工具调用） | 必需 |
| `pyautogui` | UI 自动化（无 COM 接口的软件） | 可选 |
| `Pillow` | 图像处理 | 可选 |

### 常见问题

**Q: comtypes 加载 sldworks.tlb 失败？**
A: 设置环境变量 `PYTHONUTF8=1` 后重试。中文 Windows 可能遇到编码问题。

**Q: pywin32 Dispatch 报"找不到 SldWorks.Application"？**
A: 先打开一次 SOLIDWORKS GUI 让它注册 COM 组件，或以管理员身份运行 Python。

**Q: 数据加载器找不到 JSON 文件？**
A: 数据文件位于 `src/data/`，随包分发。确保 Python 路径包含项目根目录。

## 调研背景

立项前已调研现有方案。关键发现：

- 开源生态缺一个"SW 原生 API + LLM Agent"的成熟工具
- 部分现有开源 SW 封装库处于早期阶段，API 覆盖不完整
- 部分闭源 SaaS 方案方向重合但不提供开源代码
- 学术研究方案多采用程序化建模路线

> 本项目"代码开源，思路不开源"。公开文档仅呈现亮点和使用方法，内部设计思路、架构决策、算法推导详见源码。

---

## License — AGPL-3.0 + 双重许可

**AGPL-3.0** 开源，同时保留**商业许可证**分发权利。如需闭源集成或商业 SaaS，请联系获取商业许可证。

| 场景 | 允许？ |
|------|-------|
| 个人学习/研究 | ✅ |
| 开源项目集成 | ✅（需 AGPL-3.0） |
| 企业内部修改使用 | ⚠️ 修改需开源 |
| 闭源/SaaS 商业集成 | ❌ 需商业 License |

SOLIDWORKS 是 Dassault Systèmes 的注册商标。本项目不分发 SOLIDWORKS，使用者需自备许可证。

---

## 贡献指南

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

本项目采用分层参与策略：
- **用户反馈**：欢迎通过 Issues 提交使用体验和建议
- **代码贡献**：仅接受理念相符者的贡献，需签署 [CLA.md](CLA.md)
- **文档/测试/示例**：不受限制，欢迎任何形式的改进

CLA 检查已通过 GitHub Actions 自动配置，仅对 `src/` 目录的变更触发。

---

## 联系

- 作者：电猫哥
- 专注：旋转机械设计、AI 协同工程

### 项目定位

本项目以**兴趣驱动**为主，目前主要满足个人设计需求，开发方向完全取决于维护者个人偏好。在项目成熟前，**没有商业化打算**。

### 参与方式

- **用户反馈**：欢迎通过 Issues 提交使用体验和建议
- **代码贡献**：需先在 Issues 中讨论设计方案，获得维护者认可后再提交 PR
- **商业授权咨询**：见仓库 Issues，暂不接受私下商业合作邀请

> 所有商业合作咨询请通过 GitHub Issues 公开讨论，不接受私下 cold email。