# 🌍 Geo-MiniMind: 测绘与 GIS 垂直领域大模型全链路工程

> **From Data Pipeline to Model Training:** 从零构建地理空间信息与测绘工程专属的大语言模型（LLM）底层语料库与指令微调管线。

## 💡 项目背景
在通用大模型展现出强大能力的同时，针对**测绘工程、遥感图像处理、空间数据分析 (GIS)** 等高门槛垂直领域，依然面临着开源高质量训练语料极其匮乏的痛点。
本项目旨在打造一个**端到端 (End-to-End)** 的解决方案，涵盖从多源异构领域数据爬取、启发式清洗，到基于大模型 Self-Instruct 的微调数据蒸馏，最终为训练轻量级领域大模型（基于 MiniMind 架构）提供极高信息熵的“燃料”。

## 🚀 核心特性 (Features)

本项目目前开源了核心的 **Data-Centric AI (以数据为中心)** 预处理与提炼模块：

* **🛠️ 多源异构数据清洗管线 (`build_pt_data.py`)**
    * 集成了分布式网络爬虫与 `PyMuPDF` 无损解析引擎。
    * 支持对《工程测量规范》等国家标准 PDF、开源 GIS 官方手册及技术博客进行深度解析。
    * 内置严格的启发式清洗规则（Heuristic Filtering），自动剔除特殊符号、短行噪点并修复断行，构建纯净的 PT（Pre-training）预训练文本语料。
* **🧠 基于 Qwen API 的知识蒸馏 (`generate_sft_data.py`)**
    * 采用大模型知识蒸馏范式，设计专用的 Prompt Engineering 模板。
    * 对非结构化预训练长文本进行 Chunking（分块）处理，全自动榨取逻辑严密、格式标准的高质量 SFT（Supervised Fine-Tuning）领域问答对。
    * 具备强大的容错与**断点续传**机制，实现极低成本的结构化数据合成。
* **🔀 缓解灾难性遗忘的混合策略 (`mix_dataset.py`)**
    * 将生成的纯血测绘 QA 与开源通用中文指令集（如 Alpaca 51k）进行智能比例配料与 Shuffle（洗牌）。
    * 确保模型在涌现垂直领域专业能力的同时，保留基础的通用对话与逻辑推理底色。

## 📂 仓库结构 (Repository Structure)

```text
Geo-MiniMind/
├── Data_Pipeline
  ├── build_pt_data.py       # 阶段一：领域文本爬取与 PDF 抽取 (PT 语料构建)
  ├── generate_sft_data.py   # 阶段二：调用千问 API 批量合成专业 QA 对
  ├── mix_dataset.py         # 阶段三：垂直数据与通用数据的洗牌混合脚本
  ├── dataset/               # 存放最终数据集 (注意: 由于体积限制，几十MB的完整语料未上传 GitHub)
└── README.md
