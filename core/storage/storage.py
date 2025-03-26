# -*- coding: utf-8 -*-
"""
反馈存储层

该模块负责存储和管理反馈信息，为系统提供持久化的反馈记忆。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
import json
import os
import sqlite3
from datetime import datetime
import pickle

from ...models.feedback_model import FeedbackModel, FeedbackCollection
from ...models.metadata_model import MetadataModel
from ...models.content_model import ContentModel
from ...models.relation_model import RelationModel

class FeedbackStorage(ABC):
    """
    反馈存储基类
    
    定义反馈存储的通用接口，所有具体存储实现都应继承此类。
    """
    
    @abstractmethod
    def save(self, feedback: FeedbackModel) -> bool:
        """
        保存反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def save_batch(self, feedbacks: List[FeedbackModel]) -> bool:
        """
        批量保存反馈
        
        Args:
            feedbacks: 反馈模型实例列表
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def get(self, feedback_id: str) -> Optional[FeedbackModel]:
        """
        获取反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[FeedbackModel]: 反馈模型实例，如不存在则返回None
        """
        pass
    
    @abstractmethod
    def get_batch(self, feedback_ids: List[str]) -> List[FeedbackModel]:
        """
        批量获取反馈
        
        Args:
            feedback_ids: 反馈ID列表
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        pass
    
    @abstractmethod
    def delete(self, feedback_id: str) -> bool:
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    @abstractmethod
    def update(self, feedback: FeedbackModel) -> bool:
        """
        更新反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    @abstractmethod
    def query(self, **kwargs) -> List[FeedbackModel]:
        """
        查询反馈
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            List[FeedbackModel]: 符合条件的反馈列表
        """
        pass

class JSONFileStorage(FeedbackStorage):
    """
    JSON文件存储
    
    将反馈以JSON格式存储在文件系统中。
    """
    
    def __init__(self, storage_dir: str):
        """
        初始化JSON文件存储
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # 创建索引目录
        self.index_dir = os.path.join(storage_dir, 'index')
        os.makedirs(self.index_dir, exist_ok=True)
        
        # 加载索引
        self.load_index()
    
    def load_index(self) -> None:
        """
        加载索引
        """
        self.index = {}
        index_file = os.path.join(self.index_dir, 'main_index.json')
        
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
                self.index = {}
    
    def save_index(self) -> None:
        """
        保存索引
        """
        index_file = os.path.join(self.index_dir, 'main_index.json')
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def _get_feedback_path(self, feedback_id: str) -> str:
        """
        获取反馈文件路径
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            str: 文件路径
        """
        return os.path.join(self.storage_dir, f"{feedback_id}.json")
    
    def save(self, feedback: FeedbackModel) -> bool:
        """
        保存反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 将反馈转换为字典
            feedback_dict = feedback.to_dict()
            
            # 保存到文件
            file_path = self._get_feedback_path(feedback.feedback_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(feedback_dict, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            self._update_index(feedback)
            
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def _update_index(self, feedback: FeedbackModel) -> None:
        """
        更新索引
        
        Args:
            feedback: 反馈模型实例
        """
        # 基本信息索引
        self.index[feedback.feedback_id] = {
            'timestamp': feedback.metadata.timestamp.isoformat(),
            'source': feedback.metadata.source.value if hasattr(feedback.metadata.source, 'value') else str(feedback.metadata.source),
            'feedback_type': feedback.metadata.feedback_type.value if hasattr(feedback.metadata.feedback_type, 'value') else str(feedback.metadata.feedback_type),
            'tags': feedback.metadata.tags,
            'reliability': feedback.get_reliability()
        }
        
        # 保存索引
        self.save_index()
    
    def save_batch(self, feedbacks: List[FeedbackModel]) -> bool:
        """
        批量保存反馈
        
        Args:
            feedbacks: 反馈模型实例列表
            
        Returns:
            bool: 保存是否成功
        """
        success = True
        for feedback in feedbacks:
            if not self.save(feedback):
                success = False
        return success
    
    def get(self, feedback_id: str) -> Optional[FeedbackModel]:
        """
        获取反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[FeedbackModel]: 反馈模型实例，如不存在则返回None
        """
        file_path = self._get_feedback_path(feedback_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                feedback_dict = json.load(f)
            
            return FeedbackModel.from_dict(feedback_dict)
        except Exception as e:
            print(f"Error loading feedback: {e}")
            return None
    
    def get_batch(self, feedback_ids: List[str]) -> List[FeedbackModel]:
        """
        批量获取反馈
        
        Args:
            feedback_ids: 反馈ID列表
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        result = []
        for feedback_id in feedback_ids:
            feedback = self.get(feedback_id)
            if feedback:
                result.append(feedback)
        return result
    
    def delete(self, feedback_id: str) -> bool:
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            bool: 删除是否成功
        """
        file_path = self._get_feedback_path(feedback_id)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            # 删除文件
            os.remove(file_path)
            
            # 更新索引
            if feedback_id in self.index:
                del self.index[feedback_id]
                self.save_index()
            
            return True
        except Exception as e:
            print(f"Error deleting feedback: {e}")
            return False
    
    def update(self, feedback: FeedbackModel) -> bool:
        """
        更新反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 检查反馈是否存在
        file_path = self._get_feedback_path(feedback.feedback_id)
        if not os.path.exists(file_path):
            return False
        
        # 保存更新后的反馈
        return self.save(feedback)
    
    def query(self, **kwargs) -> List[FeedbackModel]:
        """
        查询反馈
        
        Args:
            **kwargs: 查询参数，支持以下参数：
                - source: 反馈来源
                - feedback_type: 反馈类型
                - tags: 标签列表
                - start_time: 开始时间
                - end_time: 结束时间
                - min_reliability: 最小可靠性
            
        Returns:
            List[FeedbackModel]: 符合条件的反馈列表
        """
        # 根据索引筛选符合条件的反馈ID
        matched_ids = []
        
        for feedback_id, info in self.index.items():
            match = True
            
            # 按来源筛选
            if 'source' in kwargs and info['source'] != kwargs['source']:
                match = False
            
            # 按类型筛选
            if 'feedback_type' in kwargs and info['feedback_type'] != kwargs['feedback_type']:
                match = False
            
            # 按标签筛选
            if 'tags' in kwargs:
                if not set(kwargs['tags']).issubset(set(info['tags'])):
                    match = False
            
            # 按时间范围筛选
            if 'start_time' in kwargs:
                start_time = kwargs['start_time']
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if datetime.fromisoformat(info['timestamp']) < start_time:
                    match = False
            
            if 'end_time' in kwargs:
                end_time = kwargs['end_time']
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                if datetime.fromisoformat(info['timestamp']) > end_time:
                    match = False
            
            # 按可靠性筛选
            if 'min_reliability' in kwargs and info['reliability'] < kwargs['min_reliability']:
                match = False
            
            if match:
                matched_ids.append(feedback_id)
        
        # 获取符合条件的反馈
        return self.get_batch(matched_ids)

class SQLiteStorage(FeedbackStorage):
    """
    SQLite数据库存储
    
    将反馈存储在SQLite数据库中。
    """
    
    def __init__(self, db_path: str):
        """
        初始化SQLite数据库存储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """
        初始化数据库
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建反馈表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            feedback_id TEXT PRIMARY KEY,
            source TEXT,
            feedback_type TEXT,
            timestamp TEXT,
            reliability REAL,
            content BLOB,
            metadata BLOB,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # 创建标签表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_id TEXT,
            tag TEXT,
            FOREIGN KEY (feedback_id) REFERENCES feedbacks (feedback_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建关系表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relations (
            relation_id TEXT PRIMARY KEY,
            source_id TEXT,
            target_id TEXT,
            relation_type TEXT,
            strength REAL,
            metadata BLOB,
            FOREIGN KEY (source_id) REFERENCES feedbacks (feedback_id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES feedbacks (feedback_id) ON DELETE CASCADE
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedbacks_source ON feedbacks (source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedbacks_type ON feedbacks (feedback_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedbacks_timestamp ON feedbacks (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_feedback_id ON tags (feedback_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags (tag)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_source_id ON relations (source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_target_id ON relations (target_id)')
        
        conn.commit()
        conn.close()
    
    def save(self, feedback: FeedbackModel) -> bool:
        """
        保存反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 序列化内容和元数据
            content_blob = pickle.dumps(feedback.content)
            metadata_blob = pickle.dumps(feedback.metadata)
            
            # 获取源和类型的字符串表示
            source = feedback.metadata.source.value if hasattr(feedback.metadata.source, 'value') else str(feedback.metadata.source)
            feedback_type = feedback.metadata.feedback_type.value if hasattr(feedback.metadata.feedback_type, 'value') else str(feedback.metadata.feedback_type)
            
            now = datetime.now().isoformat()
            
            # 插入反馈
            cursor.execute('''
            INSERT OR REPLACE INTO feedbacks 
            (feedback_id, source, feedback_type, timestamp, reliability, content, metadata, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                source,
                feedback_type,
                feedback.metadata.timestamp.isoformat(),
                feedback.get_reliability(),
                content_blob,
                metadata_blob,
                now,
                now
            ))
            
            # 删除旧标签
            cursor.execute('DELETE FROM tags WHERE feedback_id = ?', (feedback.feedback_id,))
            
            # 插入标签
            for tag in feedback.metadata.tags:
                cursor.execute('INSERT INTO tags (feedback_id, tag) VALUES (?, ?)', (feedback.feedback_id, tag))
            
            # 保存关系
            for relation in feedback.relations:
                relation_metadata_blob = pickle.dumps(relation.metadata)
                
                cursor.execute('''
                INSERT OR REPLACE INTO relations 
                (relation_id, source_id, target_id, relation_type, strength, metadata) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    relation.relation_id,
                    relation.source_id,
                    relation.target_id,
                    relation.relation_type.value,
                    relation.strength,
                    relation_metadata_blob
                ))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error saving feedback to SQLite: {e}")
            return False
    
    def save_batch(self, feedbacks: List[FeedbackModel]) -> bool:
        """
        批量保存反馈
        
        Args:
            feedbacks: 反馈模型实例列表
            
        Returns:
            bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.isolation_level = None  # 开启事务模式
            cursor = conn.cursor()
            
            try:
                cursor.execute('BEGIN TRANSACTION')
                
                for feedback in feedbacks:
                    # 序列化内容和元数据
                    content_blob = pickle.dumps(feedback.content)
                    metadata_blob = pickle.dumps(feedback.metadata)
                    
                    # 获取源和类型的字符串表示
                    source = feedback.metadata.source.value if hasattr(feedback.metadata.source, 'value') else str(feedback.metadata.source)
                    feedback_type = feedback.metadata.feedback_type.value if hasattr(feedback.metadata.feedback_type, 'value') else str(feedback.metadata.feedback_type)
                    
                    now = datetime.now().isoformat()
                    
                    # 插入反馈
                    cursor.execute('''
                    INSERT OR REPLACE INTO feedbacks 
                    (feedback_id, source, feedback_type, timestamp, reliability, content, metadata, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        feedback.feedback_id,
                        source,
                        feedback_type,
                        feedback.metadata.timestamp.isoformat(),
                        feedback.get_reliability(),
                        content_blob,
                        metadata_blob,
                        now,
                        now
                    ))
                    
                    # 删除旧标签
                    cursor.execute('DELETE FROM tags WHERE feedback_id = ?', (feedback.feedback_id,))
                    
                    # 插入标签
                    for tag in feedback.metadata.tags:
                        cursor.execute('INSERT INTO tags (feedback_id, tag) VALUES (?, ?)', (feedback.feedback_id, tag))
                    
                    # 保存关系
                    for relation in feedback.relations:
                        relation_metadata_blob = pickle.dumps(relation.metadata)
                        
                        cursor.execute('''
                        INSERT OR REPLACE INTO relations 
                        (relation_id, source_id, target_id, relation_type, strength, metadata) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            relation.relation_id,
                            relation.source_id,
                            relation.target_id,
                            relation.relation_type.value,
                            relation.strength,
                            relation_metadata_blob
                        ))
                
                cursor.execute('COMMIT')
                return True
            except Exception as e:
                cursor.execute('ROLLBACK')
                raise e
        except Exception as e:
            print(f"Error batch saving feedbacks to SQLite: {e}")
            return False
        finally:
            conn.close()
    
    def get(self, feedback_id: str) -> Optional[FeedbackModel]:
        """
        获取反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[FeedbackModel]: 反馈模型实例，如不存在则返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询反馈
            cursor.execute('SELECT content, metadata FROM feedbacks WHERE feedback_id = ?', (feedback_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            content_blob, metadata_blob = row
            
            # 反序列化内容和元数据
            content = pickle.loads(content_blob)
            metadata = pickle.loads(metadata_blob)
            
            # 查询关系
            cursor.execute('SELECT relation_id, source_id, target_id, relation_type, strength, metadata FROM relations WHERE source_id = ? OR target_id = ?', (feedback_id, feedback_id))
            relations = []
            
            for relation_row in cursor.fetchall():
                relation_id, source_id, target_id, relation_type, strength, relation_metadata_blob = relation_row
                relation_metadata = pickle.loads(relation_metadata_blob)
                
                from ...models.relation_model import RelationType
                relation = RelationModel(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=RelationType(relation_type),
                    strength=strength,
                    metadata=relation_metadata
                )
                relations.append(relation)
            
            conn.close()
            
            # 创建反馈模型
            feedback = FeedbackModel(metadata, content, relations)
            return feedback
        except Exception as e:
            print(f"Error getting feedback from SQLite: {e}")
            return None
    
    def get_batch(self, feedback_ids: List[str]) -> List[FeedbackModel]:
        """
        批量获取反馈
        
        Args:
            feedback_ids: 反馈ID列表
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        result = []
        for feedback_id in feedback_ids:
            feedback = self.get(feedback_id)
            if feedback:
                result.append(feedback)
        return result
    
    def delete(self, feedback_id: str) -> bool:
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除反馈（关联的标签和关系会通过外键约束自动删除）
            cursor.execute('DELETE FROM feedbacks WHERE feedback_id = ?', (feedback_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error deleting feedback from SQLite: {e}")
            return False
    
    def update(self, feedback: FeedbackModel) -> bool:
        """
        更新反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 检查反馈是否存在
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM feedbacks WHERE feedback_id = ?', (feedback.feedback_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        conn.close()
        
        # 保存更新后的反馈
        return self.save(feedback)
    
    def query(self, **kwargs) -> List[FeedbackModel]:
        """
        查询反馈
        
        Args:
            **kwargs: 查询参数，支持以下参数：
                - source: 反馈来源
                - feedback_type: 反馈类型
                - tags: 标签列表
                - start_time: 开始时间
                - end_time: 结束时间
                - min_reliability: 最小可靠性
                - limit: 返回结果数量限制
                - offset: 返回结果偏移量
            
        Returns:
            List[FeedbackModel]: 符合条件的反馈列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建查询
            query = 'SELECT DISTINCT f.feedback_id FROM feedbacks f'
            params = []
            conditions = []
            
            # 标签条件需要连接标签表
            if 'tags' in kwargs and kwargs['tags']:
                query += ' LEFT JOIN tags t ON f.feedback_id = t.feedback_id'
            
            # 按来源筛选
            if 'source' in kwargs:
                conditions.append('f.source = ?')
                params.append(kwargs['source'])
            
            # 按类型筛选
            if 'feedback_type' in kwargs:
                conditions.append('f.feedback_type = ?')
                params.append(kwargs['feedback_type'])
            
            # 按标签筛选
            if 'tags' in kwargs and kwargs['tags']:
                tag_conditions = []
                for tag in kwargs['tags']:
                    tag_conditions.append('t.tag = ?')
                    params.append(tag)
                
                # 要求匹配所有标签
                tag_query = ' OR '.join(tag_conditions)
                conditions.append(f'({tag_query})')
            
            # 按时间范围筛选
            if 'start_time' in kwargs:
                start_time = kwargs['start_time']
                if isinstance(start_time, datetime):
                    start_time = start_time.isoformat()
                conditions.append('f.timestamp >= ?')
                params.append(start_time)
            
            if 'end_time' in kwargs:
                end_time = kwargs['end_time']
                if isinstance(end_time, datetime):
                    end_time = end_time.isoformat()
                conditions.append('f.timestamp <= ?')
                params.append(end_time)
            
            # 按可靠性筛选
            if 'min_reliability' in kwargs:
                conditions.append('f.reliability >= ?')
                params.append(kwargs['min_reliability'])
            
            # 添加条件到查询
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            # 添加排序
            query += ' ORDER BY f.timestamp DESC'
            
            # 添加分页
            if 'limit' in kwargs:
                query += ' LIMIT ?'
                params.append(int(kwargs['limit']))
                
                if 'offset' in kwargs:
                    query += ' OFFSET ?'
                    params.append(int(kwargs['offset']))
            
            # 执行查询
            cursor.execute(query, params)
            feedback_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # 获取反馈
            return self.get_batch(feedback_ids)
        except Exception as e:
            print(f"Error querying feedbacks from SQLite: {e}")
            return []

class VersionControlStorage(FeedbackStorage):
    """
    版本控制存储
    
    支持反馈的版本控制和历史追踪，适用于需要长期积累和分析反馈演变的场景。
    """
    
    def __init__(self, base_storage: FeedbackStorage):
        """
        初始化版本控制存储
        
        Args:
            base_storage: 基础存储实现，用于实际存储反馈数据
        """
        self.base_storage = base_storage
        self.version_history = {}
    
    def save(self, feedback: FeedbackModel) -> bool:
        """
        保存反馈，并记录版本信息
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 保存是否成功
        """
        # 检查是否存在历史版本
        if feedback.feedback_id in self.version_history:
            # 获取当前版本号
            current_version = self.version_history[feedback.feedback_id]['current_version']
            new_version = current_version + 1
            
            # 创建版本记录
            version_record = {
                'version': new_version,
                'timestamp': datetime.now().isoformat(),
                'changes': self._detect_changes(feedback)
            }
            
            # 更新版本历史
            self.version_history[feedback.feedback_id]['versions'].append(version_record)
            self.version_history[feedback.feedback_id]['current_version'] = new_version
        else:
            # 创建新的版本历史记录
            self.version_history[feedback.feedback_id] = {
                'current_version': 1,
                'versions': [{
                    'version': 1,
                    'timestamp': datetime.now().isoformat(),
                    'changes': {'type': 'create', 'details': 'Initial version'}
                }]
            }
        
        # 保存到基础存储
        return self.base_storage.save(feedback)
    
    def _detect_changes(self, new_feedback: FeedbackModel) -> Dict[str, Any]:
        """
        检测反馈的变化
        
        Args:
            new_feedback: 新的反馈模型实例
            
        Returns:
            Dict[str, Any]: 变化记录
        """
        # 获取旧版本反馈
        old_feedback = self.base_storage.get(new_feedback.feedback_id)
        if not old_feedback:
            return {'type': 'create', 'details': 'Initial version'}
        
        changes = {'type': 'update', 'details': {}}
        
        # 检测元数据变化
        if old_feedback.metadata.to_dict() != new_feedback.metadata.to_dict():
            changes['details']['metadata'] = {
                'old': old_feedback.metadata.to_dict(),
                'new': new_feedback.metadata.to_dict()
            }
        
        # 检测内容变化
        if old_feedback.content.to_dict() != new_feedback.content.to_dict():
            changes['details']['content'] = {
                'old': old_feedback.content.to_dict(),
                'new': new_feedback.content.to_dict()
            }
        
        # 检测关系变化
        old_relations = {r.relation_id: r.to_dict() for r in old_feedback.relations}
        new_relations = {r.relation_id: r.to_dict() for r in new_feedback.relations}
        
        if old_relations != new_relations:
            changes['details']['relations'] = {
                'added': [r for r_id, r in new_relations.items() if r_id not in old_relations],
                'removed': [r for r_id, r in old_relations.items() if r_id not in new_relations],
                'modified': [new_relations[r_id] for r_id in set(old_relations).intersection(set(new_relations))
                             if old_relations[r_id] != new_relations[r_id]]
            }
        
        return changes
    
    def save_batch(self, feedbacks: List[FeedbackModel]) -> bool:
        """
        批量保存反馈
        
        Args:
            feedbacks: 反馈模型实例列表
            
        Returns:
            bool: 保存是否成功
        """
        success = True
        for feedback in feedbacks:
            if not self.save(feedback):
                success = False
        return success
    
    def get(self, feedback_id: str, version: int = None) -> Optional[FeedbackModel]:
        """
        获取反馈，支持获取特定版本
        
        Args:
            feedback_id: 反馈ID
            version: 版本号，如不指定则获取最新版本
            
        Returns:
            Optional[FeedbackModel]: 反馈模型实例，如不存在则返回None
        """
        # 如果不需要特定版本，直接返回最新版本
        if version is None or feedback_id not in self.version_history:
            return self.base_storage.get(feedback_id)
        
        # 获取版本历史
        history = self.version_history[feedback_id]
        current_version = history['current_version']
        
        # 检查版本号是否有效
        if version < 1 or version > current_version:
            return None
        
        # 如果请求的是当前版本，直接返回
        if version == current_version:
            return self.base_storage.get(feedback_id)
        
        # 获取历史版本（简化实现，实际应用中可能需要更复杂的版本恢复逻辑）
        # 这里假设我们存储了完整的历史版本
        # 实际应用中可能需要基于差异记录重建历史版本
        return None  # 暂不支持获取历史版本
    
    def get_batch(self, feedback_ids: List[str]) -> List[FeedbackModel]:
        """
        批量获取反馈
        
        Args:
            feedback_ids: 反馈ID列表
            
        Returns:
            List[FeedbackModel]: 反馈模型实例列表
        """
        return self.base_storage.get_batch(feedback_ids)
    
    def delete(self, feedback_id: str) -> bool:
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            bool: 删除是否成功
        """
        # 删除版本历史
        if feedback_id in self.version_history:
            del self.version_history[feedback_id]
        
        # 从基础存储中删除
        return self.base_storage.delete(feedback_id)
    
    def update(self, feedback: FeedbackModel) -> bool:
        """
        更新反馈
        
        Args:
            feedback: 反馈模型实例
            
        Returns:
            bool: 更新是否成功
        """
        # 保存会自动处理版本控制
        return self.save(feedback)
    
    def query(self, **kwargs) -> List[FeedbackModel]:
        """
        查询反馈
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            List[FeedbackModel]: 符合条件的反馈列表
        """
        return self.base_storage.query(**kwargs)
    
    def get_version_history(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        获取反馈的版本历史
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[Dict[str, Any]]: 版本历史记录，如不存在则返回None
        """
        return self.version_history.get(feedback_id)