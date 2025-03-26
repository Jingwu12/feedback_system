# -*- coding: utf-8 -*-
"""
反馈处理器

该模块负责对收集到的原始反馈进行预处理，包括格式转换、噪声过滤、标准化等操作。
"""

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
import re
import json
from datetime import datetime

from ...models.feedback_model import FeedbackModel
from ...models.metadata_model import MetadataModel
from ...models.content_model import ContentModel, TextContent, StructuredContent

class FeedbackProcessor(ABC):
    """
    反馈处理器基类
    
    定义反馈处理的通用接口，所有具体处理器都应继承此类。
    """
    
    @abstractmethod
    def process(self, feedback: FeedbackModel) -> FeedbackModel:
        """
        处理反馈
        
        Args:
            feedback: 原始反馈
            
        Returns:
            FeedbackModel: 处理后的反馈
        """
        pass

class TextNormalizationProcessor(FeedbackProcessor):
    """
    文本标准化处理器
    
    对文本反馈进行标准化处理，包括去除多余空格、统一标点符号等。
    """
    
    def __init__(self):
        """
        初始化文本标准化处理器
        """
        # 标点符号映射，用于统一标点符号
        self.punctuation_map = {
            '，': ',',
            '。': '.',
            '；': ';',
            '：': ':',
            '？': '?',
            '！': '!',
            '"': '"',
            ''': '\'',
            ''': '\'',
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '《': '<',
            '》': '>'
        }
    
    def process(self, feedback: FeedbackModel) -> FeedbackModel:
        """
        处理文本反馈，进行标准化
        
        Args:
            feedback: 原始反馈
            
        Returns:
            FeedbackModel: 处理后的反馈
        """
        # 确保反馈内容是文本类型
        if not isinstance(feedback.content, TextContent):
            return feedback
        
        # 获取原始文本
        text = feedback.content.text
        
        # 标准化处理
        normalized_text = self._normalize_text(text)
        
        # 更新反馈内容
        feedback.content.text = normalized_text
        
        # 添加处理记录到元数据
        if not hasattr(feedback.metadata, 'processing_history'):
            feedback.metadata.processing_history = []
        
        feedback.metadata.processing_history.append({
            'processor': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'operation': 'text_normalization'
        })
        
        return feedback
    
    def _normalize_text(self, text: str) -> str:
        """
        对文本进行标准化处理
        
        Args:
            text: 原始文本
            
        Returns:
            str: 标准化后的文本
        """
        # 统一标点符号
        for cn_punct, en_punct in self.punctuation_map.items():
            text = text.replace(cn_punct, en_punct)
        
        # 去除首尾空格
        text = text.strip()
        
        # 将多个连续空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        return text

class NoiseFilterProcessor(FeedbackProcessor):
    """
    噪声过滤处理器
    
    对反馈内容进行噪声过滤，去除无关信息和干扰内容。
    """
    
    def __init__(self, noise_patterns: List[str] = None, min_content_length: int = 5):
        """
        初始化噪声过滤处理器
        
        Args:
            noise_patterns: 噪声模式列表，用于匹配需要过滤的内容
            min_content_length: 最小内容长度，小于此长度的内容将被视为噪声
        """
        self.noise_patterns = noise_patterns or [
            r'(无意义|没有用|废话)',
            r'(\d{1,2}:\d{2})',  # 时间格式
            r'(请稍等|请等待|loading)',
            r'(测试消息|test message)'
        ]
        self.min_content_length = min_content_length
        self.noise_regex = re.compile('|'.join(self.noise_patterns), re.IGNORECASE)
    
    def process(self, feedback: FeedbackModel) -> FeedbackModel:
        """
        处理反馈，过滤噪声
        
        Args:
            feedback: 原始反馈
            
        Returns:
            FeedbackModel: 处理后的反馈
        """
        # 文本内容噪声过滤
        if isinstance(feedback.content, TextContent):
            # 获取原始文本
            text = feedback.content.text
            
            # 内容长度检查
            if len(text.strip()) < self.min_content_length:
                # 设置噪声标记
                feedback.metadata.is_noise = True
                feedback.metadata.noise_reason = 'content_too_short'
                return feedback
            
            # 噪声模式匹配
            if self.noise_regex.search(text):
                # 设置噪声标记
                feedback.metadata.is_noise = True
                feedback.metadata.noise_reason = 'matched_noise_pattern'
                return feedback
            
            # 过滤噪声内容
            filtered_text = self.noise_regex.sub('', text)
            feedback.content.text = filtered_text.strip()
        
        # 结构化内容噪声过滤
        elif isinstance(feedback.content, StructuredContent):
            # 简单实现：检查是否为空数据
            if not feedback.content.data:
                feedback.metadata.is_noise = True
                feedback.metadata.noise_reason = 'empty_structured_data'
                return feedback
        
        # 添加处理记录到元数据
        if not hasattr(feedback.metadata, 'processing_history'):
            feedback.metadata.processing_history = []
        
        feedback.metadata.processing_history.append({
            'processor': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'operation': 'noise_filtering'
        })
        
        return feedback

class SentimentAnalysisProcessor(FeedbackProcessor):
    """
    情感分析处理器
    
    对反馈内容进行情感分析，识别反馈的情感倾向。
    """
    
    def __init__(self):
        """
        初始化情感分析处理器
        """
        # 积极情感词汇
        self.positive_words = [
            '好', '优秀', '满意', '喜欢', '赞', '棒', '正确', '准确',
            '有用', '有效', '有帮助', '清晰', '易懂', '合理', '恰当'
        ]
        
        # 消极情感词汇
        self.negative_words = [
            '差', '糟糕', '不满', '不喜欢', '批评', '错误', '不准确',
            '无用', '无效', '没帮助', '模糊', '难懂', '不合理', '不恰当'
        ]
    
    def process(self, feedback: FeedbackModel) -> FeedbackModel:
        """
        处理反馈，进行情感分析
        
        Args:
            feedback: 原始反馈
            
        Returns:
            FeedbackModel: 处理后的反馈
        """
        # 确保反馈内容是文本类型
        if not isinstance(feedback.content, TextContent):
            return feedback
        
        # 获取文本内容
        text = feedback.content.text
        
        # 计算情感得分
        sentiment_score = self._calculate_sentiment_score(text)
        
        # 添加情感分析结果到元数据
        feedback.metadata.sentiment_score = sentiment_score
        
        # 根据得分确定情感标签
        if sentiment_score > 0.2:
            feedback.metadata.sentiment = 'positive'
        elif sentiment_score < -0.2:
            feedback.metadata.sentiment = 'negative'
        else:
            feedback.metadata.sentiment = 'neutral'
        
        # 添加处理记录到元数据
        if not hasattr(feedback.metadata, 'processing_history'):
            feedback.metadata.processing_history = []
        
        feedback.metadata.processing_history.append({
            'processor': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'operation': 'sentiment_analysis'
        })
        
        return feedback
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """
        计算文本的情感得分
        
        Args:
            text: 文本内容
            
        Returns:
            float: 情感得分，范围[-1, 1]，正值表示积极，负值表示消极
        """
        # 简单实现：基于词汇匹配的情感分析
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_count