# -*- coding: utf-8 -*-
"""
XML通信协议实现

该模块实现了基于XML格式的通信协议，用于反馈系统中的数据交换。
XML格式提供了更丰富的数据结构和验证机制，适合处理复杂的医疗反馈数据。
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Any, Dict, List, Optional, Union
import io

from .base_protocol import BaseProtocol

class XMLProtocol(BaseProtocol):
    """
    XML协议实现类，基于XML格式进行数据交换。
    
    该类实现了将反馈数据编码为XML格式和从XML格式解码反馈数据的功能，
    并提供了数据验证和模式定义等功能。
    """
    
    def __init__(self, schema_path: str = None):
        """
        初始化XML协议
        
        Args:
            schema_path: XML Schema文件路径，用于验证数据格式
        """
        self.schema_path = schema_path
        self.version = "1.0.0"
    
    def encode(self, data: Dict[str, Any]) -> bytes:
        """
        将数据编码为XML字节流
        
        Args:
            data: 要编码的数据
            
        Returns:
            bytes: 编码后的XML字节流
        """
        try:
            # 验证数据格式
            if not self.validate(data):
                raise ValueError("数据格式不符合协议规范")
            
            # 创建XML根元素
            root = ET.Element("feedback")
            
            # 添加基本属性
            ET.SubElement(root, "id").text = str(data.get("id", ""))
            ET.SubElement(root, "source").text = data.get("source", "")
            ET.SubElement(root, "timestamp").text = str(data.get("timestamp", 0))
            
            # 添加内容
            content_elem = ET.SubElement(root, "content")
            self._dict_to_xml(data.get("content", {}), content_elem)
            
            # 添加元数据
            if "metadata" in data:
                metadata_elem = ET.SubElement(root, "metadata")
                self._dict_to_xml(data.get("metadata", {}), metadata_elem)
            
            # 转换为格式化的XML字符串
            xml_str = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")
            return xml_str.encode("utf-8")
        except Exception as e:
            raise ValueError(f"编码数据失败: {str(e)}")
    
    def decode(self, data: bytes) -> Dict[str, Any]:
        """
        将XML字节流解码为数据
        
        Args:
            data: 要解码的XML字节流
            
        Returns:
            Dict[str, Any]: 解码后的数据
        """
        try:
            # 解析XML
            root = ET.fromstring(data.decode("utf-8"))
            
            # 提取基本信息
            result = {
                "id": self._get_element_text(root, "id"),
                "source": self._get_element_text(root, "source"),
                "timestamp": float(self._get_element_text(root, "timestamp") or 0),
                "content": {},
                "metadata": {}
            }
            
            # 提取内容
            content_elem = root.find("content")
            if content_elem is not None:
                result["content"] = self._xml_to_dict(content_elem)
            
            # 提取元数据
            metadata_elem = root.find("metadata")
            if metadata_elem is not None:
                result["metadata"] = self._xml_to_dict(metadata_elem)
            
            # 验证解码后的数据格式
            if not self.validate(result):
                raise ValueError("解码后的数据格式不符合协议规范")
            
            return result
        except Exception as e:
            raise ValueError(f"解码数据失败: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否符合协议规范
        
        Args:
            data: 要验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        # 基本字段验证
        required_fields = ["id", "source", "timestamp", "content"]
        for field in required_fields:
            if field not in data:
                return False
        
        # 类型验证
        if not isinstance(data.get("id"), str):
            return False
        if not isinstance(data.get("source"), str):
            return False
        if not isinstance(data.get("timestamp"), (int, float)):
            return False
        if not isinstance(data.get("content"), dict):
            return False
        if "metadata" in data and not isinstance(data.get("metadata"), dict):
            return False
        
        # 如果有XML Schema，可以进行更详细的验证
        if self.schema_path:
            try:
                # 这里应该实现基于XML Schema的验证
                # 为简化示例，这里省略具体实现
                pass
            except Exception:
                return False
        
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取协议的数据模式定义
        
        Returns:
            Dict[str, Any]: 协议的数据模式定义
        """
        # 返回简化的模式描述
        return {
            "type": "xml",
            "schema_path": self.schema_path,
            "required_fields": ["id", "source", "timestamp", "content"],
            "optional_fields": ["metadata"]
        }
    
    def get_version(self) -> str:
        """
        获取协议的版本号
        
        Returns:
            str: 协议的版本号
        """
        return self.version
    
    def _dict_to_xml(self, data: Dict[str, Any], parent_elem: ET.Element) -> None:
        """
        将字典转换为XML元素
        
        Args:
            data: 要转换的字典
            parent_elem: 父XML元素
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # 嵌套字典
                child = ET.SubElement(parent_elem, key)
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                # 列表
                list_elem = ET.SubElement(parent_elem, key)
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(list_elem, "item")
                    item_elem.set("index", str(i))
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem.text = str(item)
            else:
                # 基本类型
                child = ET.SubElement(parent_elem, key)
                child.text = str(value)
    
    def _xml_to_dict(self, elem: ET.Element) -> Dict[str, Any]:
        """
        将XML元素转换为字典
        
        Args:
            elem: 要转换的XML元素
            
        Returns:
            Dict[str, Any]: 转换后的字典
        """
        result = {}
        
        # 处理子元素
        for child in elem:
            # 检查是否为列表项
            if child.tag == "item" and "index" in child.attrib:
                # 列表项处理在父元素中进行
                continue
            
            # 检查是否有子元素
            if len(child) > 0:
                # 检查是否为列表
                if all(item.tag == "item" and "index" in item.attrib for item in child):
                    # 处理列表
                    items = []
                    for item in child:
                        if len(item) > 0:
                            items.append(self._xml_to_dict(item))
                        else:
                            items.append(item.text)
                    result[child.tag] = items
                else:
                    # 处理嵌套字典
                    result[child.tag] = self._xml_to_dict(child)
            else:
                # 处理基本类型
                result[child.tag] = child.text
        
        return result
    
    def _get_element_text(self, elem: ET.Element, tag: str) -> Optional[str]:
        """
        获取元素的文本内容
        
        Args:
            elem: 父元素
            tag: 子元素标签
            
        Returns:
            Optional[str]: 文本内容，如果元素不存在则返回None
        """
        child = elem.find(tag)
        return child.text if child is not None else None