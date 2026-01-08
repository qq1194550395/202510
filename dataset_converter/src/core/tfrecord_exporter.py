"""
TensorFlow Record 导出器
"""
import tensorflow as tf
from pathlib import Path
from typing import List
from .base_parser import ImageAnnotation
import json


class TFRecordExporter:
    """TensorFlow Record 格式导出器"""
    
    def __init__(self):
        self.format_name = "tfrecord"
    
    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        """导出为TFRecord格式"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 分别创建训练和验证集
        train_file = output_dir / "train.tfrecord"
        val_file = output_dir / "val.tfrecord"
        
        # 简单划分：80%训练，20%验证
        split_idx = int(len(annotations) * 0.8)
        train_annotations = annotations[:split_idx]
        val_annotations = annotations[split_idx:]
        
        # 写入训练集
        self._write_tfrecord(train_annotations, train_file)
        print(f"训练集TFRecord已保存: {train_file} ({len(train_annotations)}张图片)")
        
        # 写入验证集
        self._write_tfrecord(val_annotations, val_file)
        print(f"验证集TFRecord已保存: {val_file} ({len(val_annotations)}张图片)")
        
        # 生成标签映射文件
        self._create_label_map(annotations, output_dir)
    
    def _write_tfrecord(self, annotations: List[ImageAnnotation], output_file: Path):
        """写入TFRecord文件"""
        with tf.io.TFRecordWriter(str(output_file)) as writer:
            for ann in annotations:
                if not ann.image_path.exists():
                    continue
                    
                # 读取图片数据
                image_data = ann.image_path.read_bytes()
                
                # 提取标注信息
                xmins, ymins, xmaxs, ymaxs, labels = [], [], [], [], []
                for box in ann.boxes:
                    xmins.append(box.xmin / ann.width)  # 归一化
                    ymins.append(box.ymin / ann.height)
                    xmaxs.append(box.xmax / ann.width)
                    ymaxs.append(box.ymax / ann.height)
                    labels.append(box.label.encode('utf-8'))
                
                # 创建TF Example
                example = tf.train.Example(features=tf.train.Features(feature={
                    'image/encoded': tf.train.Feature(
                        bytes_list=tf.train.BytesList(value=[image_data])),
                    'image/format': tf.train.Feature(
                        bytes_list=tf.train.BytesList(value=[b'jpeg'])),
                    'image/filename': tf.train.Feature(
                        bytes_list=tf.train.BytesList(value=[ann.image_path.name.encode('utf-8')])),
                    'image/height': tf.train.Feature(
                        int64_list=tf.train.Int64List(value=[ann.height])),
                    'image/width': tf.train.Feature(
                        int64_list=tf.train.Int64List(value=[ann.width])),
                    'image/object/bbox/xmin': tf.train.Feature(
                        float_list=tf.train.FloatList(value=xmins)),
                    'image/object/bbox/ymin': tf.train.Feature(
                        float_list=tf.train.FloatList(value=ymins)),
                    'image/object/bbox/xmax': tf.train.Feature(
                        float_list=tf.train.FloatList(value=xmaxs)),
                    'image/object/bbox/ymax': tf.train.Feature(
                        float_list=tf.train.FloatList(value=ymaxs)),
                    'image/object/class/text': tf.train.Feature(
                        bytes_list=tf.train.BytesList(value=labels)),
                }))
                
                writer.write(example.SerializeToString())
    
    def _create_label_map(self, annotations: List[ImageAnnotation], output_dir: Path):
        """创建标签映射文件"""
        # 收集所有标签
        all_labels = set()
        for ann in annotations:
            for box in ann.boxes:
                all_labels.add(box.label)
        
        # 创建标签映射
        label_map = {label: idx + 1 for idx, label in enumerate(sorted(all_labels))}
        
        # 保存为JSON格式
        label_file = output_dir / "label_map.json"
        with open(label_file, 'w', encoding='utf-8') as f:
            json.dump(label_map, f, ensure_ascii=False, indent=2)
        
        print(f"标签映射已保存: {label_file}")
        print(f"标签数量: {len(label_map)}")