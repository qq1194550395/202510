# 数据集转换工具 v2.0 / Dataset Converter v2.0

🚀 **专业级数据集处理工具套件** - 一个功能完整、界面现代化的桌面应用程序，专为计算机视觉项目的数据集管理而设计。

🚀 **Professional Dataset Processing Toolkit** - A comprehensive desktop application designed for computer vision dataset management with modern UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

---

## 📖 目录 / Table of Contents

### 🇨🇳 中文文档
- [主要特性](#主要特性)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [项目结构](#项目结构)
- [核心功能](#核心功能)
- [使用示例](#使用示例)
- [支持的数据格式](#支持的数据格式)
- [界面特色](#界面特色)
- [更新日志](#更新日志)
- [贡献指南](#贡献指南)

### 🇺🇸 English Documentation
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation Guide](#installation-guide)
- [Project Structure](#project-structure)
- [Core Functions](#core-functions)
- [Usage Examples](#usage-examples)
- [Supported Data Formats](#supported-data-formats)
- [Interface Features](#interface-features)
- [Version History](#version-history)
- [Contributing](#contributing)

---

# 🇨🇳 中文文档

## ✨ 主要特性

### 🔄 格式转换
- **5种主流格式支持**: YOLO检测、YOLO分割、VOC、JSON、自定义格式
- **智能转换**: 支持矩形框和多边形标注的混合处理
- **无损转换**: 保持标注精度和完整性
- **批量处理**: 高效处理大规模数据集

### 📊 数据分析
- **全面统计**: 图片数量、标注分布、类别统计
- **质量评估**: 自动检测数据问题，生成健康度评分
- **可视化展示**: 直观的标注可视化和数据集预览
- **详细报告**: 生成专业的HTML分析报告

### 🛠️ 数据处理
- **自动修复**: 智能修复坐标错误、重复文件等问题
- **数据增强**: 7种图像增强方法，支持自定义组合
- **数据整理**: 批量重命名、数据集划分、多数据集合并
- **格式标准化**: 统一文件命名和目录结构

### 🎨 现代化界面
- **Material Design**: 现代化的用户界面设计
- **响应式布局**: 支持滚动，适配不同屏幕尺寸
- **统一风格**: 所有窗口采用一致的设计语言
- **用户友好**: 直观的操作流程和清晰的状态反馈

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PyQt5 5.15+
- Pillow 10.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/dataset-converter.git
cd dataset-converter
```

2. **安装依赖**
```bash
pip install -r dataset_converter/requirements.txt
```

3. **启动程序**
```bash
python dataset_converter/main.py
```

## 📦 安装指南

### 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 建议 4GB 以上
- **存储**: 至少 100MB 可用空间

### 方法1: 直接安装（推荐）

1. **下载项目**
```bash
git clone https://github.com/your-username/dataset-converter.git
cd dataset-converter
```

2. **安装Python依赖**
```bash
pip install -r dataset_converter/requirements.txt
```

3. **启动程序**
```bash
python dataset_converter/main.py
```

### 方法2: 虚拟环境安装

1. **创建虚拟环境**
```bash
python -m venv dataset_converter_env

# Windows
dataset_converter_env\Scripts\activate

# macOS/Linux  
source dataset_converter_env/bin/activate
```

2. **安装依赖并启动**
```bash
pip install -r dataset_converter/requirements.txt
python dataset_converter/main.py
```

### 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| PyQt5 | ≥5.15.0 | GUI界面框架 |
| Pillow | ≥10.0.0 | 图像处理 |
| pyyaml | ≥6.0 | 配置文件解析 |
| lxml | ≥5.1.0 | XML文件处理 |

### 常见问题

#### Q: 提示"No module named 'PyQt5'"
**A**: 安装PyQt5依赖
```bash
pip install PyQt5>=5.15.0
```

#### Q: 提示"No module named 'PIL'"  
**A**: 安装Pillow依赖
```bash
pip install Pillow>=10.0.0
```

#### Q: Windows上PowerShell执行策略错误
**A**: 使用CMD而不是PowerShell，或者设置执行策略
```cmd
# 使用CMD运行
python dataset_converter/main.py
```

#### Q: 程序启动后界面显示不完整
**A**: 确保屏幕分辨率至少为1200x800，程序会自动调整布局

### 验证安装

运行以下命令验证安装是否成功：

```bash
python -c "
import sys
print(f'Python版本: {sys.version}')

try:
    import PyQt5
    print('✓ PyQt5 已安装')
except ImportError:
    print('✗ PyQt5 未安装')

try:
    from PIL import Image
    print('✓ Pillow 已安装')
except ImportError:
    print('✗ Pillow 未安装')

try:
    import yaml
    print('✓ PyYAML 已安装')
except ImportError:
    print('✗ PyYAML 未安装')

print('安装验证完成！')
"
```

## 📁 项目结构

```
dataset_converter/
├── 📄 README.md                    # 项目说明文档
├── 📄 requirements.txt             # 依赖包列表
├── 📄 main.py                      # 程序入口
├── 📁 src/                         # 源代码目录
│   ├── 📁 core/                    # 核心功能模块
│   │   ├── 📄 base_parser.py       # 基础解析器
│   │   ├── 📄 converter.py         # 格式转换器
│   │   ├── 📄 yolo_parser.py       # YOLO检测解析器
│   │   ├── 📄 yolo_seg_parser.py   # YOLO分割解析器
│   │   ├── 📄 voc_parser.py        # VOC格式解析器
│   │   ├── 📄 json_parser.py       # JSON格式解析器
│   │   ├── 📄 dataset_analyzer.py  # 数据集分析器
│   │   ├── 📄 dataset_validator.py # 数据集验证器
│   │   ├── 📄 data_augmentation.py # 数据增强器
│   │   ├── 📄 dataset_organizer.py # 数据集整理器
│   │   ├── 📄 annotation_visualizer.py # 标注可视化器
│   │   ├── 📄 dataset_comparator.py # 数据集比较器
│   │   ├── 📄 annotation_fixer.py  # 标注修复器
│   │   └── 📄 dataset_exporter.py  # 数据集导出器
│   ├── 📁 gui/                     # 图形界面模块
│   │   ├── 📄 styles.py            # 统一样式管理
│   │   ├── 📄 home_window.py       # 主窗口
│   │   ├── 📄 converter_panel.py   # 转换面板
│   │   ├── 📄 analysis_panel.py    # 分析面板
│   │   ├── 📄 splitting_panel.py   # 分割面板
│   │   └── 📁 widgets/             # 自定义控件
│   └── 📁 utils/                   # 工具函数
│       ├── 📄 file_utils.py        # 文件操作工具
│       ├── 📄 xml_utils.py         # XML处理工具
│       ├── 📄 label_utils.py       # 标签处理工具
│       └── 📄 logger.py            # 日志工具
├── 📁 data/                        # 数据目录
│   ├── 📁 input/                   # 输入数据
│   └── 📁 output/                  # 输出数据
├── 📁 configs/                     # 配置文件
│   └── 📄 config.yaml              # 主配置文件
└── 📁 resources/                   # 资源文件
    └── 🖼️ icon.png                 # 应用图标
```

## 🎯 核心功能

### 1. 数据集格式转换
- **YOLO检测** ↔ **VOC** ↔ **JSON**
- **YOLO分割** ↔ **JSON**
- **YOLO分割** → **YOLO检测** (保留矩形框)
- 支持自定义标签映射和批量转换

### 2. 数据集分析
- 📈 **统计分析**: 全面的数据集统计信息
- 🔍 **质量检查**: 自动检测和评估数据质量
- 📊 **可视化**: 标注可视化和数据集预览
- 📋 **报告生成**: 专业的HTML分析报告

### 3. 数据集处理
- 🔧 **自动修复**: 修复坐标错误、重复文件等问题
- 🎨 **数据增强**: 亮度、对比度、旋转、翻转等增强
- 📂 **数据整理**: 重命名、划分、合并数据集
- ⚖️ **数据比较**: 多数据集对比分析

### 4. 数据导出
- 📦 **ZIP打包**: 完整数据集打包导出
- 🏷️ **COCO格式**: 导出为COCO标准格式
- ⚙️ **训练配置**: 生成YOLO训练配置文件
- 📄 **详细报告**: HTML格式的分析报告

## 💡 使用示例

### 数据准备

#### YOLO检测格式示例
```
# 文件: image1.txt
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.2
```

#### YOLO分割格式示例
```
# 文件: image2.txt
0 0.5 0.5 0.3 0.4                           # 矩形框
1 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2           # 四边形
2 0.7 0.7 0.8 0.7 0.8 0.8 0.7 0.8 0.75 0.75 # 五边形
```

### GUI使用步骤

1. **启动程序**
   ```bash
   python dataset_converter/main.py
   ```

2. **选择功能**
   - 点击"数据集格式转换"

3. **设置路径**
   - 点击"选择输入目录" - 选择包含标注文件的目录
   - 点击"选择输出目录" - 选择转换结果保存目录

4. **选择转换格式**
   - **检测格式转换**: 使用第一行按钮
     - YOLO检测 → VOC
     - VOC → YOLO检测
     - JSON → VOC
     - YOLO检测 → JSON
   
   - **分割格式转换**: 使用第二行按钮
     - YOLO分割 → JSON
     - JSON → YOLO检测
     - JSON → YOLO分割
     - YOLO分割 → YOLO检测

5. **可选: 加载标签字典**
   - 点击"加载标签字典"
   - 选择标签映射文件 (格式: `类别名 类别ID`)

6. **开始转换**
   - 点击"开始转换"
   - 查看日志输出了解转换进度

### 基本转换
1. 启动程序，选择"数据集格式转换"
2. 选择输入目录（包含图片和标注文件）
3. 选择输出目录
4. 点击对应的转换按钮（如"YOLO检测 → JSON"）
5. 查看转换日志和结果

### 数据集分析
1. 选择"数据集分析"面板
2. 选择数据集目录
3. 点击"统计分析"查看详细统计
4. 点击"质量检查"评估数据质量
5. 点击"生成报告"创建HTML报告

### 数据增强
1. 在分析面板中选择数据集
2. 选择需要的增强方法（亮度、对比度等）
3. 设置增强倍数
4. 点击"开始增强"生成增强数据

### 命令行使用 (高级)

```python
from pathlib import Path
from dataset_converter.src.core.converter import convert

# YOLO分割 → JSON
convert(
    input_dir=Path("input_data"),
    input_format="yolo_seg", 
    output_dir=Path("output_data"),
    output_format="json"
)
```

## 🔧 支持的数据格式

### YOLO检测格式
```
# 每行格式: class_id center_x center_y width height (归一化坐标)
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.2
```

### YOLO分割格式
```
# 矩形框: class_id center_x center_y width height
0 0.5 0.5 0.3 0.4
# 多边形: class_id x1 y1 x2 y2 ... xn yn
1 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2
```

### JSON格式
```json
{
  "file_name": "image.jpg",
  "width": 800,
  "height": 600,
  "annotations": [
    {"label": "cat", "bbox": [100, 100, 200, 200]},
    {"label": "dog", "polygon": [0.1, 0.1, 0.2, 0.1, 0.2, 0.2]}
  ]
}
```

## 🎨 界面特色

- **现代化设计**: Material Design风格界面
- **统一风格**: 所有窗口采用一致的设计语言
- **响应式布局**: 支持滚动，适配不同屏幕尺寸
- **直观操作**: 颜色编码的按钮（绿色=执行，橙色=警告，蓝色=主要）
- **实时反馈**: 详细的日志输出和进度显示

## 📝 更新日志

### [2.0.0] - 2024-01-07

#### 🎉 重大更新
- 完全重构的现代化界面设计
- 新增YOLO分割格式支持
- 完整的数据集分析和处理功能

#### ✨ 新增功能

**格式转换**
- 新增YOLO分割格式解析器 (`yolo_seg_parser.py`)
- 支持矩形框和多边形混合标注
- 扩展JSON解析器支持分割标注
- 新增12种转换路径

**数据分析**
- 数据集统计分析器 (`dataset_analyzer.py`)
- 数据质量验证器 (`dataset_validator.py`)
- 标注可视化器 (`annotation_visualizer.py`)
- 数据集比较器 (`dataset_comparator.py`)
- HTML报告生成功能

**数据处理**
- 自动修复器 (`annotation_fixer.py`)
- 数据增强器 (`data_augmentation.py`)
- 数据集整理器 (`dataset_organizer.py`)
- 多格式导出器 (`dataset_exporter.py`)

**界面优化**
- 统一样式管理系统 (`styles.py`)
- Material Design风格界面
- 响应式布局和滚动支持
- 三个主要功能面板：转换、分析、分割

#### 🔧 改进

**用户体验**
- 重新设计的主窗口布局
- 颜色编码的功能按钮
- 实时进度显示和日志输出
- 直观的状态反馈

**技术架构**
- 模块化的核心功能设计
- 统一的解析器接口
- 可扩展的插件架构
- 改进的错误处理机制

**性能优化**
- 优化大文件处理性能
- 改进内存使用效率
- 支持批量操作
- 异步处理支持

#### 🐛 修复
- 修复YOLO坐标解析精度问题
- 修复JSON文件编码问题
- 修复界面在不同分辨率下的显示问题
- 修复文件路径处理的跨平台兼容性

### [1.0.0] - 2023-12-01

#### ✨ 初始版本
- 基础的YOLO、VOC、JSON格式转换功能
- 简单的PyQt5 GUI界面
- 基本的文件选择和转换操作
- 日志输出功能

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 强大的GUI框架
- [Pillow](https://pillow.readthedocs.io/) - Python图像处理库
- [Material Design](https://material.io/design) - 现代化设计指南

## 📞 联系方式

如果您有问题或建议，请通过以下方式联系我们：

- 📧 邮箱: your-email@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/dataset-converter/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your-username/dataset-converter/discussions)

### 注意事项

1. **文件命名**: 标注文件必须与图片文件同名
2. **坐标格式**: YOLO格式使用归一化坐标 (0-1)
3. **多边形要求**: 至少需要3个点 (6个坐标值)
4. **格式兼容**: YOLO分割格式向下兼容YOLO检测格式

---

⭐ 如果这个项目对你有帮助，请给它一个星标！

---

# 🇺🇸 English Documentation

## ✨ Key Features

### 🔄 Format Conversion
- **5 mainstream formats**: YOLO Detection, YOLO Segmentation, VOC, JSON, Custom formats
- **Smart conversion**: Mixed processing of bounding boxes and polygon annotations
- **Lossless conversion**: Maintains annotation precision and completeness
- **Batch processing**: Efficient handling of large-scale datasets

### 📊 Data Analysis
- **Comprehensive statistics**: Image count, annotation distribution, class statistics
- **Quality assessment**: Automatic problem detection with health scoring
- **Visualization**: Intuitive annotation visualization and dataset preview
- **Detailed reports**: Professional HTML analysis reports

### 🛠️ Data Processing
- **Auto-repair**: Smart fixing of coordinate errors, duplicate files, etc.
- **Data augmentation**: 7 image enhancement methods with custom combinations
- **Data organization**: Batch renaming, dataset splitting, multi-dataset merging
- **Format standardization**: Unified file naming and directory structure

### 🎨 Modern Interface
- **Material Design**: Modern user interface design
- **Responsive layout**: Scroll support, adapts to different screen sizes
- **Unified style**: Consistent design language across all windows
- **User-friendly**: Intuitive operation flow and clear status feedback

## 🚀 Quick Start

### Requirements
- Python 3.8+
- PyQt5 5.15+
- Pillow 10.0+

### Installation

1. **Clone the project**
```bash
git clone https://github.com/your-username/dataset-converter.git
cd dataset-converter
```

2. **Install dependencies**
```bash
pip install -r dataset_converter/requirements.txt
```

3. **Launch the application**
```bash
python dataset_converter/main.py
```

## 📦 Installation Guide

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 or higher
- **Memory**: 4GB+ recommended
- **Storage**: At least 100MB available space

### Method 1: Direct Installation (Recommended)

1. **Download the project**
```bash
git clone https://github.com/your-username/dataset-converter.git
cd dataset-converter
```

2. **Install Python dependencies**
```bash
pip install -r dataset_converter/requirements.txt
```

3. **Launch the application**
```bash
python dataset_converter/main.py
```

### Method 2: Virtual Environment Installation

1. **Create virtual environment**
```bash
python -m venv dataset_converter_env

# Windows
dataset_converter_env\Scripts\activate

# macOS/Linux  
source dataset_converter_env/bin/activate
```

2. **Install dependencies and launch**
```bash
pip install -r dataset_converter/requirements.txt
python dataset_converter/main.py
```

### Dependencies Overview

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | ≥5.15.0 | GUI framework |
| Pillow | ≥10.0.0 | Image processing |
| pyyaml | ≥6.0 | Configuration file parsing |
| lxml | ≥5.1.0 | XML file processing |

### Common Issues

#### Q: "No module named 'PyQt5'" error
**A**: Install PyQt5 dependency
```bash
pip install PyQt5>=5.15.0
```

#### Q: "No module named 'PIL'" error  
**A**: Install Pillow dependency
```bash
pip install Pillow>=10.0.0
```

#### Q: PowerShell execution policy error on Windows
**A**: Use CMD instead of PowerShell, or set execution policy
```cmd
# Use CMD to run
python dataset_converter/main.py
```

#### Q: Incomplete interface display after startup
**A**: Ensure screen resolution is at least 1200x800, the program will automatically adjust layout

### Installation Verification

Run the following command to verify successful installation:

```bash
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import PyQt5
    print('✓ PyQt5 installed')
except ImportError:
    print('✗ PyQt5 not installed')

try:
    from PIL import Image
    print('✓ Pillow installed')
except ImportError:
    print('✗ Pillow not installed')

try:
    import yaml
    print('✓ PyYAML installed')
except ImportError:
    print('✗ PyYAML not installed')

print('Installation verification complete!')
"
```

## 📁 Project Structure

```
dataset_converter/
├── 📄 README.md                    # Project documentation
├── 📄 requirements.txt             # Dependencies list
├── 📄 main.py                      # Application entry point
├── 📁 src/                         # Source code directory
│   ├── 📁 core/                    # Core functionality modules
│   │   ├── 📄 base_parser.py       # Base parser
│   │   ├── 📄 converter.py         # Format converter
│   │   ├── 📄 yolo_parser.py       # YOLO detection parser
│   │   ├── 📄 yolo_seg_parser.py   # YOLO segmentation parser
│   │   ├── 📄 voc_parser.py        # VOC format parser
│   │   ├── 📄 json_parser.py       # JSON format parser
│   │   ├── 📄 dataset_analyzer.py  # Dataset analyzer
│   │   ├── 📄 dataset_validator.py # Dataset validator
│   │   ├── 📄 data_augmentation.py # Data augmentor
│   │   ├── 📄 dataset_organizer.py # Dataset organizer
│   │   ├── 📄 annotation_visualizer.py # Annotation visualizer
│   │   ├── 📄 dataset_comparator.py # Dataset comparator
│   │   ├── 📄 annotation_fixer.py  # Annotation fixer
│   │   └── 📄 dataset_exporter.py  # Dataset exporter
│   ├── 📁 gui/                     # GUI modules
│   │   ├── 📄 styles.py            # Unified style management
│   │   ├── 📄 home_window.py       # Main window
│   │   ├── 📄 converter_panel.py   # Conversion panel
│   │   ├── 📄 analysis_panel.py    # Analysis panel
│   │   ├── 📄 splitting_panel.py   # Splitting panel
│   │   └── 📁 widgets/             # Custom widgets
│   └── 📁 utils/                   # Utility functions
│       ├── 📄 file_utils.py        # File operation utilities
│       ├── 📄 xml_utils.py         # XML processing utilities
│       ├── 📄 label_utils.py       # Label processing utilities
│       └── 📄 logger.py            # Logging utilities
├── 📁 data/                        # Data directory
│   ├── 📁 input/                   # Input data
│   └── 📁 output/                  # Output data
├── 📁 configs/                     # Configuration files
│   └── 📄 config.yaml              # Main configuration
└── 📁 resources/                   # Resource files
    └── 🖼️ icon.png                 # Application icon
```

## 🎯 Core Functions

### 1. Dataset Format Conversion
- **YOLO Detection** ↔ **VOC** ↔ **JSON**
- **YOLO Segmentation** ↔ **JSON**
- **YOLO Segmentation** → **YOLO Detection** (keep bounding boxes)
- Support for custom label mapping and batch conversion

### 2. Dataset Analysis
- 📈 **Statistical analysis**: Comprehensive dataset statistics
- 🔍 **Quality check**: Automatic detection and assessment of data quality
- 📊 **Visualization**: Annotation visualization and dataset preview
- 📋 **Report generation**: Professional HTML analysis reports

### 3. Dataset Processing
- 🔧 **Auto-repair**: Fix coordinate errors, duplicate files, etc.
- 🎨 **Data augmentation**: Brightness, contrast, rotation, flip, etc.
- 📂 **Data organization**: Rename, split, merge datasets
- ⚖️ **Data comparison**: Multi-dataset comparison analysis

### 4. Data Export
- 📦 **ZIP packaging**: Complete dataset packaging and export
- 🏷️ **COCO format**: Export to COCO standard format
- ⚙️ **Training config**: Generate YOLO training configuration files
- 📄 **Detailed reports**: HTML format analysis reports

## 💡 Usage Examples

### Data Preparation

#### YOLO Detection Format Example
```
# File: image1.txt
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.2
```

#### YOLO Segmentation Format Example
```
# File: image2.txt
0 0.5 0.5 0.3 0.4                           # Bounding box
1 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2           # Quadrilateral
2 0.7 0.7 0.8 0.7 0.8 0.8 0.7 0.8 0.75 0.75 # Pentagon
```

### GUI Usage Steps

1. **Launch the application**
   ```bash
   python dataset_converter/main.py
   ```

2. **Select function**
   - Click "Dataset Format Conversion"

3. **Set paths**
   - Click "Select Input Directory" - Choose directory containing annotation files
   - Click "Select Output Directory" - Choose directory to save conversion results

4. **Choose conversion format**
   - **Detection format conversion**: Use first row buttons
     - YOLO Detection → VOC
     - VOC → YOLO Detection
     - JSON → VOC
     - YOLO Detection → JSON
   
   - **Segmentation format conversion**: Use second row buttons
     - YOLO Segmentation → JSON
     - JSON → YOLO Detection
     - JSON → YOLO Segmentation
     - YOLO Segmentation → YOLO Detection

5. **Optional: Load label dictionary**
   - Click "Load Label Dictionary"
   - Select label mapping file (format: `class_name class_id`)

6. **Start conversion**
   - Click "Start Conversion"
   - Check log output for conversion progress

### Basic Conversion
1. Launch the application, select "Dataset Format Conversion"
2. Select input directory (containing images and annotation files)
3. Select output directory
4. Click the corresponding conversion button (e.g., "YOLO Detection → JSON")
5. View conversion logs and results

### Dataset Analysis
1. Select "Dataset Analysis" panel
2. Select dataset directory
3. Click "Statistical Analysis" to view detailed statistics
4. Click "Quality Check" to assess data quality
5. Click "Generate Report" to create HTML report

### Data Augmentation
1. In the analysis panel, select dataset
2. Choose desired augmentation methods (brightness, contrast, etc.)
3. Set augmentation multiplier
4. Click "Start Augmentation" to generate augmented data

### Command Line Usage (Advanced)

```python
from pathlib import Path
from dataset_converter.src.core.converter import convert

# YOLO Segmentation → JSON
convert(
    input_dir=Path("input_data"),
    input_format="yolo_seg", 
    output_dir=Path("output_data"),
    output_format="json"
)
```

## 🔧 Supported Data Formats

### YOLO Detection Format
```
# Format: class_id center_x center_y width height (normalized coordinates)
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.2
```

### YOLO Segmentation Format
```
# Bounding box: class_id center_x center_y width height
0 0.5 0.5 0.3 0.4
# Polygon: class_id x1 y1 x2 y2 ... xn yn
1 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2
```

### JSON Format
```json
{
  "file_name": "image.jpg",
  "width": 800,
  "height": 600,
  "annotations": [
    {"label": "cat", "bbox": [100, 100, 200, 200]},
    {"label": "dog", "polygon": [0.1, 0.1, 0.2, 0.1, 0.2, 0.2]}
  ]
}
```

## 🎨 Interface Features

- **Modern design**: Material Design style interface
- **Unified style**: Consistent design language across all windows
- **Responsive layout**: Scroll support, adapts to different screen sizes
- **Intuitive operation**: Color-coded buttons (green=execute, orange=warning, blue=primary)
- **Real-time feedback**: Detailed log output and progress display

## 📝 Version History

### [2.0.0] - 2024-01-07

#### 🎉 Major Updates
- Complete redesign with modern interface
- Added YOLO segmentation format support
- Comprehensive dataset analysis and processing features

#### ✨ New Features

**Format Conversion**
- New YOLO segmentation format parser (`yolo_seg_parser.py`)
- Support for mixed bounding box and polygon annotations
- Extended JSON parser with segmentation annotation support
- Added 12 conversion pathways

**Data Analysis**
- Dataset statistical analyzer (`dataset_analyzer.py`)
- Data quality validator (`dataset_validator.py`)
- Annotation visualizer (`annotation_visualizer.py`)
- Dataset comparator (`dataset_comparator.py`)
- HTML report generation functionality

**Data Processing**
- Auto-repair tool (`annotation_fixer.py`)
- Data augmentation engine (`data_augmentation.py`)
- Dataset organizer (`dataset_organizer.py`)
- Multi-format exporter (`dataset_exporter.py`)

**Interface Improvements**
- Unified style management system (`styles.py`)
- Material Design interface
- Responsive layout with scroll support
- Three main functional panels: conversion, analysis, splitting

#### 🔧 Improvements

**User Experience**
- Redesigned main window layout
- Color-coded functional buttons
- Real-time progress display and log output
- Intuitive status feedback

**Technical Architecture**
- Modular core functionality design
- Unified parser interface
- Extensible plugin architecture
- Improved error handling mechanisms

**Performance Optimization**
- Optimized large file processing performance
- Improved memory usage efficiency
- Support for batch operations
- Asynchronous processing support

#### 🐛 Bug Fixes
- Fixed YOLO coordinate parsing precision issues
- Fixed JSON file encoding problems
- Fixed interface display issues on different resolutions
- Fixed cross-platform compatibility for file path handling

### [1.0.0] - 2023-12-01

#### ✨ Initial Release
- Basic YOLO, VOC, JSON format conversion functionality
- Simple PyQt5 GUI interface
- Basic file selection and conversion operations
- Log output functionality

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Powerful GUI framework
- [Pillow](https://pillow.readthedocs.io/) - Python imaging library
- [Material Design](https://material.io/design) - Modern design guidelines

## 📞 Contact

If you have questions or suggestions, please contact us through:

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/dataset-converter/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/dataset-converter/discussions)

### Important Notes

1. **File naming**: Annotation files must have the same name as image files
2. **Coordinate format**: YOLO format uses normalized coordinates (0-1)
3. **Polygon requirements**: At least 3 points required (6 coordinate values)
4. **Format compatibility**: YOLO segmentation format is backward compatible with YOLO detection format

---

⭐ If this project helps you, please give it a star!