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

- ✅ 已验证：Python + pywin32 + comtypes 调用 SW API 完成阶梯轴建模（旋转+拉伸切除+旋转切除）
- ✅ 已完成：7 份技术文档（01-07）
- ✅ 已完成：项目骨架搭建（10 个模块，45 个文件）
- 🚧 进行中：P1 单步指令开发（SolidWorksAdapter）
- ❌ 待做：参数化零件生成器、MCP Server、工程图自动生成

**架构决策**：MVP 阶段不开发 GUI，仅提供 **MCP + CLI** 接口，面向 LLM Agent 调用。

详见 [docs/04_开发规划.md](docs/04_开发规划.md)。

## 目录结构

```
RotorMachAgent/
├── README.md
├── CLA.md                          # 贡献者许可协议
├── CONTRIBUTING.md                  # 贡献指南
├── LICENSE                         # AGPL-3.0
├── requirements.txt                # Python 依赖
├── docs/                           # 技术文档
│   ├── 01_SW_API单步指令参考.md
│   ├── 02_SW_API指令间协同.md
│   ├── 03_从设计思路到最终零件.md
│   ├── 04_开发规划.md
│   ├── 05_待研究问题.md
│   ├── 06_基于API的测量与特征识别规划.md
│   └── 07_系统架构设计.md
├── tests/                          # 验证脚本
│   └── test_shaft_modeling.py
├── src/                            # 源码
│   ├── adapters/                   # 工程软件适配器（SW/ACAD/ANSYS）
│   ├── parts/                      # 参数化零件模板（轴/座/桨叶/罐体）
│   ├── assemblies/                 # 装配体构建与工程图
│   ├── products/                   # 产品系列批量生成
│   ├── calculations/               # 工程计算（功率/轴径/轴承/罐体）
│   ├── standards/                  # GB 标准件库（键/挡圈/螺纹/轴承）
│   ├── database/                   # 数据库管理（SQLite/PostgreSQL）
│   ├── tools/                      # Agent 工具封装（MCP 协议）
│   ├── agents/                     # Agent 工作流与 MCP Server
│   └── utils/                      # 通用工具（单位转换/参数校验/日志）
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
python tests/test_shaft_modeling.py
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

## 调研背景

立项前已调研现有方案，详见 [docs/05_待研究问题.md](docs/05_待研究问题.md)。关键发现：

- 开源生态缺一个"SW 原生 API + LLM Agent"的成熟工具
- 部分现有开源 SW 封装库处于早期阶段，API 覆盖不完整
- 部分闭源 SaaS 方案方向重合但不提供开源代码
- 学术研究方案多采用程序化建模路线

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

核心代码（`src/`）贡献需签署 [CLA.md](CLA.md)，文档/测试/示例贡献不受限制。

---

## 联系

- 作者：电猫哥
- 专注：旋转机械设计、AI 协同工程
- 商业授权咨询：见仓库 Issues
