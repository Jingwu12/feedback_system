# -*- coding: utf-8 -*-
"""
反馈关系模型

该模块定义了反馈之间的语义关系，构建反馈关系网络。
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum

class RelationType(Enum):
    """
    反馈关系类型枚举
    """
    SUPPORT = "support"           # 支持关系，表示一个反馈支持另一个反馈的观点
    OPPOSE = "oppose"            # 反对关系，表示一个反馈反对另一个反馈的观点
    COMPLEMENT = "complement"    # 补充关系，表示一个反馈补充另一个反馈的信息
    REFINE = "refine"            # 细化关系，表示一个反馈对另一个反馈进行细化
    TEMPORAL = "temporal"        # 时序关系，表示反馈之间的时间先后顺序
    CAUSAL = "causal"            # 因果关系，表示反馈之间的因果联系

class TemporalRelationType(Enum):
    """
    时序关系类型枚举
    """
    BEFORE = "before"            # 先于
    AFTER = "after"              # 后于
    DURING = "during"            # 期间
    OVERLAP = "overlap"          # 重叠

class RelationModel:
    """
    反馈关系模型
    
    定义反馈之间的语义关系，构建反馈关系网络。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 relation_type: RelationType,
                 strength: float = 1.0,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        初始化关系模型
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            relation_type: 关系类型
            strength: 关系强度，范围[0,1]
            metadata: 关系元数据，包含关系的附加信息
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type if isinstance(relation_type, RelationType) else RelationType(relation_type)
        self.strength = max(0.0, min(1.0, strength))  # 确保强度在[0,1]范围内
        self.metadata = metadata if metadata else {}
        self.relation_id = f"{source_id}_{target_id}_{relation_type.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将关系模型转换为字典表示
        
        Returns:
            Dict: 关系的字典表示
        """
        return {
            'relation_id': self.relation_id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type.value,
            'strength': self.strength,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationModel':
        """
        从字典创建关系模型实例
        
        Args:
            data: 关系的字典表示
            
        Returns:
            RelationModel: 关系模型实例
        """
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type'],
            strength=data.get('strength', 1.0),
            metadata=data.get('metadata')
        )

class SupportRelation(RelationModel):
    """
    支持关系模型
    
    表示一个反馈支持另一个反馈的观点或结论。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 strength: float = 1.0,
                 evidence: Optional[List[str]] = None,
                 confidence: float = 1.0):
        """
        初始化支持关系模型
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            strength: 支持强度，范围[0,1]
            evidence: 支持证据，如引用的文献、数据等
            confidence: 支持的置信度，范围[0,1]
        """
        metadata = {
            'evidence': evidence if evidence else [],
            'confidence': confidence
        }
        super().__init__(source_id, target_id, RelationType.SUPPORT, strength, metadata)

class OpposeRelation(RelationModel):
    """
    反对关系模型
    
    表示一个反馈反对另一个反馈的观点或结论。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 strength: float = 1.0,
                 reason: Optional[str] = None,
                 alternative: Optional[str] = None):
        """
        初始化反对关系模型
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            strength: 反对强度，范围[0,1]
            reason: 反对理由
            alternative: 替代方案
        """
        metadata = {
            'reason': reason,
            'alternative': alternative
        }
        super().__init__(source_id, target_id, RelationType.OPPOSE, strength, metadata)

class ComplementRelation(RelationModel):
    """
    补充关系模型
    
    表示一个反馈补充另一个反馈的信息。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 strength: float = 1.0,
                 aspect: Optional[str] = None,
                 information_gain: float = 0.5):
        """
        初始化补充关系模型
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            strength: 补充强度，范围[0,1]
            aspect: 补充的方面
            information_gain: 信息增益，表示补充信息的价值，范围[0,1]
        """
        metadata = {
            'aspect': aspect,
            'information_gain': information_gain
        }
        super().__init__(source_id, target_id, RelationType.COMPLEMENT, strength, metadata)

class TemporalRelation(RelationModel):
    """
    时序关系模型
    
    表示反馈之间的时间先后顺序。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 temporal_type: TemporalRelationType,
                 time_gap: Optional[float] = None,
                 unit: str = 'seconds'):
        """
        初始化时序关系模型
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            temporal_type: 时序类型
            time_gap: 时间间隔
            unit: 时间单位
        """
        temporal_type = temporal_type if isinstance(temporal_type, TemporalRelationType) else TemporalRelationType(temporal_type)
        metadata = {
            'temporal_type': temporal_type.value,
            'time_gap': time_gap,
            'unit': unit
        }
        super().__init__(source_id, target_id, RelationType.TEMPORAL, 1.0, metadata)

class CausalRelation(RelationModel):
    """
    因果关系模型
    
    表示反馈之间的因果联系。
    """
    
    def __init__(self, 
                 source_id: str, 
                 target_id: str, 
                 strength: float = 1.0,
                 mechanism: Optional[str] = None,
                 confidence: float = 0.8):
        """
        初始化因果关系模型
        
        Args:
            source_id: 源反馈ID（因）
            target_id: 目标反馈ID（果）
            strength: 因果强度，范围[0,1]
            mechanism: 因果机制描述
            confidence: 因果关系的置信度，范围[0,1]
        """
        metadata = {
            'mechanism': mechanism,
            'confidence': confidence
        }
        super().__init__(source_id, target_id, RelationType.CAUSAL, strength, metadata)

class RelationGraph:
    """
    反馈关系图
    
    管理反馈之间的关系，支持关系的添加、查询和分析。
    """
    
    def __init__(self):
        """
        初始化关系图
        """
        self.relations = {}  # 关系字典，键为关系ID，值为关系对象
        self.feedback_relations = {}  # 反馈关系索引，键为反馈ID，值为相关的关系ID列表
    
    def add_relation(self, relation: RelationModel) -> None:
        """
        添加关系
        
        Args:
            relation: 关系模型实例
        """
        self.relations[relation.relation_id] = relation
        
        # 更新索引
        if relation.source_id not in self.feedback_relations:
            self.feedback_relations[relation.source_id] = []
        self.feedback_relations[relation.source_id].append(relation.relation_id)
        
        if relation.target_id not in self.feedback_relations:
            self.feedback_relations[relation.target_id] = []
        self.feedback_relations[relation.target_id].append(relation.relation_id)
    
    def get_relation(self, relation_id: str) -> Optional[RelationModel]:
        """
        获取关系
        
        Args:
            relation_id: 关系ID
            
        Returns:
            Optional[RelationModel]: 关系模型实例，如不存在则返回None
        """
        return self.relations.get(relation_id)
    
    def get_relations_by_feedback(self, feedback_id: str) -> List[RelationModel]:
        """
        获取与指定反馈相关的所有关系
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            List[RelationModel]: 关系模型实例列表
        """
        if feedback_id not in self.feedback_relations:
            return []
        
        return [self.relations[relation_id] for relation_id in self.feedback_relations[feedback_id]]
    
    def get_relations_by_type(self, relation_type: RelationType) -> List[RelationModel]:
        """
        获取指定类型的所有关系
        
        Args:
            relation_type: 关系类型
            
        Returns:
            List[RelationModel]: 关系模型实例列表
        """
        relation_type = relation_type if isinstance(relation_type, RelationType) else RelationType(relation_type)
        return [relation for relation in self.relations.values() if relation.relation_type == relation_type]
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> List[List[RelationModel]]:
        """
        查找两个反馈之间的关系路径
        
        Args:
            source_id: 源反馈ID
            target_id: 目标反馈ID
            max_depth: 最大搜索深度
            
        Returns:
            List[List[RelationModel]]: 关系路径列表，每个路径是一个关系序列
        """
        if source_id == target_id:
            return [[]]
        
        if max_depth <= 0:
            return []
        
        paths = []
        visited = set([source_id])
        
        def dfs(current_id, current_path, depth):
            if depth >= max_depth:
                return
            
            # 获取当前反馈的所有关系
            relations = self.get_relations_by_feedback(current_id)
            
            for relation in relations:
                next_id = relation.target_id if relation.source_id == current_id else relation.source_id
                
                if next_id in visited:
                    continue
                
                visited.add(next_id)
                current_path.append(relation)
                
                if next_id == target_id:
                    # 找到目标，添加路径
                    paths.append(current_path.copy())
                else:
                    # 继续搜索
                    dfs(next_id, current_path, depth + 1)
                
                current_path.pop()
                visited.remove(next_id)
        
        dfs(source_id, [], 0)
        return paths
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将关系图转换为字典表示
        
        Returns:
            Dict: 关系图的字典表示
        """
        return {
            'relations': {relation_id: relation.to_dict() for relation_id, relation in self.relations.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationGraph':
        """
        从字典创建关系图实例
        
        Args:
            data: 关系图的字典表示
            
        Returns:
            RelationGraph: 关系图实例
        """
        graph = cls()
        
        for relation_data in data['relations'].values():
            relation = RelationModel.from_dict(relation_data)
            graph.add_relation(relation)
        
        return graph