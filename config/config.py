# -*- coding: utf-8 -*-
"""
反馈系统配置

该模块定义了反馈系统的全局配置参数。
"""

from typing import Dict, Any
import os
import json

class FeedbackSystemConfig:
    """
    反馈系统配置类
    
    管理反馈系统的全局配置参数。
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，如不指定则使用默认配置
        """
        # 默认配置
        self.config = {
            # 存储配置
            'storage': {
                'type': 'json',  # 存储类型：json, sqlite, version_control
                'json_storage_dir': 'data/feedback_storage',
                'sqlite_db_path': 'data/feedback.db',
                'enable_version_control': True
            },
            
            # 收集器配置
            'collector': {
                'human_feedback': {
                    'enabled': True,
                    'default_source': 'human.doctor'
                },
                'tool_feedback': {
                    'enabled': True,
                    'tools': ['imaging_system', 'lab_system', 'ehr_system']
                },
                'knowledge_feedback': {
                    'enabled': True,
                    'sources': ['medical_kg', 'literature_db']
                },
                'self_feedback': {
                    'enabled': True,
                    'assessment_types': ['consistency', 'completeness', 'correctness']
                }
            },
            
            # 处理器配置
            'processor': {
                'text_normalization': {
                    'enabled': True
                },
                'noise_filter': {
                    'enabled': True,
                    'min_content_length': 5,
                    'noise_patterns': [
                        r'(无意义|没有用|废话)',
                        r'(\d{1,2}:\d{2})',  # 时间格式
                        r'(请稍等|请等待|loading)',
                        r'(测试消息|test message)'
                    ]
                },
                'sentiment_analysis': {
                    'enabled': True
                }
            },
            
            # 融合器配置
            'fusion': {
                'default_method': 'graph_based',  # graph_based, attention_based, rl_based
                'graph_based': {
                    'relation_threshold': 0.5,
                    'max_iterations': 3
                },
                'attention_based': {
                    'attention_heads': 4,
                    'attention_dropout': 0.1
                },
                'rl_based': {
                    'learning_rate': 0.01,
                    'discount_factor': 0.9
                }
            },
            
            # 利用器配置
            'utilizer': {
                'planning_adjuster': {
                    'enabled': True
                },
                'execution_optimizer': {
                    'enabled': True
                },
                'knowledge_updater': {
                    'enabled': True
                }
            },
            
            # 接口配置
            'interface': {
                'api': {
                    'host': '0.0.0.0',
                    'port': 8000,
                    'debug': False
                },
                'protocols': {
                    'fhir_enabled': True,
                    'hl7_enabled': True
                }
            },
            
            # 日志配置
            'logging': {
                'level': 'INFO',
                'file': 'logs/feedback_system.log',
                'max_size': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5
            }
        }
        
        # 如果指定了配置文件，则加载
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self._merge_config(self.config, user_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def _merge_config(self, base_config: Dict[str, Any], user_config: Dict[str, Any]) -> None:
        """
        合并配置
        
        Args:
            base_config: 基础配置
            user_config: 用户配置
        """
        for key, value in user_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def save_config(self, config_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key_path: str, default=None) -> Any:
        """
        获取配置项
        
        Args:
            key_path: 配置项路径，如 'storage.type'
            default: 默认值，如配置项不存在则返回该值
            
        Returns:
            Any: 配置项值
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys:
            if key in config:
                config = config[key]
            else:
                return default
        
        return config
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key_path: 配置项路径，如 'storage.type'
            value: 配置项值
        """
        keys = key_path.split('.')
        config = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value

# 全局配置实例
config = FeedbackSystemConfig()