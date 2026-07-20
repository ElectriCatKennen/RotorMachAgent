# Contributing to RotorMachAgent

感谢您对 RotorMachAgent 的关注！本项目采用分层参与策略，欢迎不同类型的贡献。

## 快速链接

- [CLA (Contributor License Agreement)](CLA.md) — 核心代码贡献必需
- [开发规划](docs/开发规划.md) — 查看路线图
- [Open Issues](../../issues) — 提交反馈和建议

## 参与方式

### 1. 用户反馈（无需签署 CLA）

这是最重要的参与方式！我们非常重视用户的使用体验和建议。

1. **Bug 报告**：
   - 搜索 [现有 issues](../../issues) 避免重复
   - 提交新 issue，包含：
     - SW 版本和 Python 版本
     - 最小可复现脚本
     - 预期行为 vs 实际行为
     - 错误信息（原文，非截图）

2. **功能建议**：
   - 提交带 `enhancement` 标签的 issue
   - 描述使用场景（不仅仅是解决方案）
   - 引用相关标准（GB、ISO、API 文档）

3. **使用体验分享**：
   - 在 Issues 或 Discussions 中分享您的使用感受
   - 提出改进建议

### 2. 代码贡献（需签署 CLA）

本项目仅接受理念相符者的代码贡献。贡献前需在 Issues 中讨论设计方案，获得维护者认可。

1. **讨论设计方案**：
   - 在 Issues 中提出您的想法
   - 等待维护者确认理念相符并批准实施

2. **开发流程**：
   - **Fork** 仓库
   - 创建 **feature 分支**：`git checkout -b feature/your-feature`
   - 进行修改
   - **测试** 修改（至少在 SW 上运行验证）
   - **Commit** 并使用清晰的提交信息（见下方格式）
   - **Push** 到您的 fork：`git push origin feature/your-feature`
   - 提交 **Pull Request**

### 3. 文档/测试/示例贡献（无需签署 CLA）

文档、测试和示例贡献不受限制，欢迎任何形式的改进。

### 理念相符标准

- 认同本项目"旋转机械设计 + AI 协同"的定位
- 理解并尊重维护者的设计决策
- 以解决实际工程问题为导向
- 接受项目的 AGPL-3.0 开源协议

## 提交信息格式

```
<type>: <short description>

[可选的详细描述]
```

类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试添加
- `chore`: 维护工作

示例：
```
feat: add shaft keyway generator with GB/T 1096 lookup
fix: FeatureRevolve parameter order (was causing 302.7° rotation)
docs: add SW API measurement method reference
```

## CLA 要求

| 贡献类型 | 是否需要 CLA | 原因 |
|---------|-------------|------|
| `src/`（核心代码） | **是** | 双重许可（AGPL-3.0 + 商业许可）需要版权授权 |
| `docs/`（文档） | 否 | 文档不属于双重许可核心 |
| `tests/`（测试用例） | 否 | 测试不属于双重许可核心 |
| `examples/`（示例） | 否 | 示例不属于双重许可核心 |
| Bug 报告 / 建议 | 否 | 不属于可版权化贡献 |

如果您的 PR 修改了 `src/` 目录，将被要求确认接受 CLA。详见 [CLA.md](CLA.md)。

## 开发环境设置

### 前置条件

- Windows 10/11
- Python 3.10+（推荐：3.11）
- SOLIDWORKS 2023+
- conda（推荐）

### 设置步骤

```bash
# 创建 conda 环境
conda create -n rotormachagent python=3.11
conda activate rotormachagent

# 安装依赖
pip install -r requirements.txt

# 验证 SW API 连接
python tests/adapters/test_sw_adapter_single_step.py

# 验证标准数据加载
python tests/standards/test_data_loader.py
```

### 已知问题

- **comtypes 编码**：中文 Windows 可能产生 `mbcs` 编码错误。运行前设置 `PYTHONUTF8=1`。
- **COM 注册**：如果 `Dispatch('SldWorks.Application')` 失败，先打开一次 SW GUI 注册 COM 组件。

## 代码风格

- Python 3.10+ 语法
- 函数和变量使用 `snake_case`
- 类名使用 `PascalCase`
- 常量使用 `UPPER_SNAKE_CASE`
- 提交前运行 `ruff check .` 和 `ruff format .`
- 公共 API 添加函数级文档字符串和类型注释

## 项目结构

```
src/
├── tools/          # Agent 工具封装（测量、建模、导出）
├── adapters/       # 工程软件适配器（SW、AutoCAD、Ansys）
├── parts/          # 参数化零件模板（轴、座、桨叶、罐体）
├── calculations/   # 工程计算（功率、轴径、轴承）
├── standards/      # GB 标准件库（键、挡圈、螺纹、轴承）
└── agents/         # Agent 工作流与 MCP Server
```

添加新工具时：
1. 创建 `src/tools/<tool_name>.py`
2. 遵循现有工具接口模式
3. 在 `tests/` 中添加测试
4. 更新文档

## 疑问？

一般问题请在 [Discussions](../../discussions) 中提问，Bug 和功能请求请提交 [Issue](../../issues)。
