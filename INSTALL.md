# 安装指南

## 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 建议 4GB 以上
- **存储**: 至少 100MB 可用空间

## 安装步骤

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

## 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| PyQt5 | ≥5.15.0 | GUI界面框架 |
| Pillow | ≥10.0.0 | 图像处理 |
| pyyaml | ≥6.0 | 配置文件解析 |
| lxml | ≥5.1.0 | XML文件处理 |

## 常见问题

### Q: 提示"No module named 'PyQt5'"
**A**: 安装PyQt5依赖
```bash
pip install PyQt5>=5.15.0
```

### Q: 提示"No module named 'PIL'"  
**A**: 安装Pillow依赖
```bash
pip install Pillow>=10.0.0
```

### Q: Windows上PowerShell执行策略错误
**A**: 使用CMD而不是PowerShell，或者设置执行策略
```cmd
# 使用CMD运行
python dataset_converter/main.py
```

### Q: 程序启动后界面显示不完整
**A**: 确保屏幕分辨率至少为1200x800，程序会自动调整布局

## 验证安装

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

## 卸载

如果需要卸载，只需删除项目文件夹：

```bash
# 如果使用了虚拟环境，先删除虚拟环境
rm -rf dataset_converter_env  # Linux/macOS
rmdir /s dataset_converter_env  # Windows

# 删除项目文件夹
rm -rf dataset-converter  # Linux/macOS
rmdir /s dataset-converter  # Windows
```

## 获取帮助

如果遇到安装问题：

1. 检查Python版本: `python --version`
2. 检查pip版本: `pip --version`  
3. 更新pip: `pip install --upgrade pip`
4. 查看错误日志并在GitHub Issues中报告问题

---

🎉 安装完成后，你就可以开始使用这个强大的数据集转换工具了！