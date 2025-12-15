# YOLO格式转换使用示例

## 数据准备

### YOLO检测格式示例
```
# 文件: image1.txt
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.2
```

### YOLO分割格式示例
```
# 文件: image2.txt
0 0.5 0.5 0.3 0.4                           # 矩形框
1 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2           # 四边形
2 0.7 0.7 0.8 0.7 0.8 0.8 0.7 0.8 0.75 0.75 # 五边形
```

## GUI使用步骤

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

## 命令行使用 (高级)

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

## 注意事项

1. **文件命名**: 标注文件必须与图片文件同名
2. **坐标格式**: YOLO格式使用归一化坐标 (0-1)
3. **多边形要求**: 至少需要3个点 (6个坐标值)
4. **格式兼容**: YOLO分割格式向下兼容YOLO检测格式