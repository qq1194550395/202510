# 数据集转换工具（Dataset Converter）

一个使用 PyQt5 构建的桌面应用，专注于常见检测数据格式之间的相互转换：YOLO ↔ VOC ↔ JSON。

## 主要特性

- 支持 YOLO、VOC、JSON 三种格式互转
- 可扩展的解析器与统一的转换器接口
- 简洁的 GUI：输入/输出路径选择、格式选择、日志输出
- 模块化代码组织，便于维护与扩展

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## 目录结构

```
dataset_converter/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── converter.py
│   │   ├── yolo_parser.py
│   │   ├── voc_parser.py
│   │   ├── json_parser.py
│   │   └── base_parser.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   ├── xml_utils.py
│   │   └── logger.py
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py
│       ├── ui_mainwindow.py
│       └── widgets/
│           ├── path_selector.py
│           └── format_combo.py
├── data/
│   ├── input/
│   └── output/
├── configs/
│   └── config.yaml
└── resources/
    └── icon.png
```

## 扩展解析器

- 在 `src/core/base_parser.py` 继承 `BaseParser`
- 在 `converter.py` 注册新解析器与目标格式写出逻辑

## 免责声明

示例代码仅用于结构演示，实际转换规则需根据项目数据进行适配与测试。