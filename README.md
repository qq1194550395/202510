# 数据集转换工具 v2.0（Dataset Converter）

🚀 **专业级数据集处理工具套件** - 一个功能完整、界面现代化的桌面应用程序，专为计算机视觉项目的数据集管理而设计。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

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

## 📁 项目结构

```
dataset_converter/
├── 📄 README.md                    # 项目说明文档
├── 📄 requirements.txt             # 依赖包列表
├── 📄 main.py                      # 程序入口
├── 📄 FEATURES.md                  # 详细功能说明
├── 📄 USAGE_EXAMPLE.md             # 使用示例
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

## 🔄 版本历史

### v2.0 (当前版本)
- ✨ 新增YOLO分割格式支持
- 🎨 全新的现代化界面设计
- 📊 完整的数据集分析功能
- 🛠️ 自动修复和数据增强
- 📤 多格式导出和报告生成
- 🔍 数据集比较和可视化

### v1.0
- 🔄 基础的YOLO、VOC、JSON格式转换
- 🖥️ 简单的GUI界面
- 📁 基本的文件管理功能

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


---

⭐ 如果这个项目对你有帮助，请给它一个星标！