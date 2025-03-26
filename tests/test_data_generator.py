# -*- coding: utf-8 -*-
"""
测试数据生成器

该模块用于生成测试数据，支持生成各种类型的反馈数据，用于测试反馈系统的各个组件。
"""

import random
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.feedback_model import FeedbackModel
from models.metadata_model import MetadataModel, SourceType, FeedbackType
from models.content_model import TextContent, StructuredContent
from models.relation_model import RelationModel, RelationType

class TestDataGenerator:
    """
    测试数据生成器
    """
    
    def __init__(self):
        """
        初始化测试数据生成器
        """
        # 医疗症状列表
        self.symptoms = [
            "头痛", "胸痛", "腹痛", "发热", "咳嗽", "呕吐", "腹泻", "乏力", "头晕", "呼吸困难",
            "心悸", "关节痛", "肌肉酸痛", "皮疹", "视力模糊", "听力下降", "食欲不振", "体重减轻",
            "尿频", "尿急", "尿痛", "便秘", "黄疸", "水肿", "出血", "麻木", "瘙痒", "失眠"
        ]
        
        # 医疗诊断列表
        self.diagnoses = [
            "高血压", "糖尿病", "冠心病", "心肌梗死", "脑卒中", "肺炎", "肺癌", "胃炎", "胃溃疡",
            "胃癌", "肝炎", "肝硬化", "肝癌", "肾炎", "肾衰竭", "尿路感染", "前列腺炎", "前列腺增生",
            "前列腺癌", "乳腺炎", "乳腺癌", "甲状腺功能亢进", "甲状腺功能减退", "甲状腺炎", "甲状腺癌",
            "类风湿关节炎", "骨质疏松", "骨折", "椎间盘突出", "颈椎病", "腰椎间盘突出", "腰椎管狭窄",
            "偏头痛", "抑郁症", "焦虑症", "精神分裂症", "双相情感障碍", "痴呆", "帕金森病", "癫痫"
        ]
        
        # 医疗治疗列表
        self.treatments = [
            "药物治疗", "手术治疗", "物理治疗", "心理治疗", "放射治疗", "化疗", "免疫治疗", "靶向治疗",
            "基因治疗", "干细胞治疗", "康复治疗", "中医治疗", "针灸治疗", "推拿治疗", "饮食治疗", "运动治疗"
        ]
        
        # 医疗检查列表
        self.examinations = [
            "血常规", "尿常规", "便常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "超声心动图",
            "胸部X线", "腹部B超", "CT", "MRI", "PET-CT", "内镜", "病理活检", "基因检测", "免疫组化"
        ]
    
    def generate_random_feedback(self, source_type=None, feedback_type=None, timestamp=None):
        """
        生成随机反馈
        
        Args:
            source_type: 反馈来源类型，如果为None则随机选择
            feedback_type: 反馈类型，如果为None则随机选择
            timestamp: 反馈时间戳，如果为None则随机生成
            
        Returns:
            FeedbackModel: 随机生成的反馈
        """
        # 随机选择来源类型
        if source_type is None:
            source_type = random.choice(list(SourceType))
        
        # 随机选择反馈类型
        if feedback_type is None:
            feedback_type = random.choice(list(FeedbackType))
        
        # 随机生成时间戳
        if timestamp is None:
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        # 随机生成标签
        tags = []
        tag_count = random.randint(0, 3)
        if tag_count > 0:
            if 'doctor' in str(source_type):
                tags = random.sample(["urgent", "follow_up", "consultation", "referral"], tag_count)
            elif 'patient' in str(source_type):
                tags = random.sample(["symptom", "medication", "side_effect", "improvement"], tag_count)
            elif 'system' in str(source_type):
                tags = random.sample(["test_result", "monitoring", "alert", "reminder"], tag_count)
            elif 'knowledge' in str(source_type):
                tags = random.sample(["guideline", "research", "evidence", "recommendation"], tag_count)
        
        # 创建元数据
        metadata = MetadataModel(
            source=source_type,
            feedback_type=feedback_type,
            timestamp=timestamp,
            tags=tags
        )
        
        # 根据反馈类型创建内容
        if feedback_type == FeedbackType.TEXTUAL or feedback_type == FeedbackType.DIAGNOSTIC or feedback_type == FeedbackType.THERAPEUTIC:
            content = self._generate_text_content(source_type, feedback_type)
        else:
            content = self._generate_structured_content(source_type, feedback_type)
        
        # 创建反馈
        feedback = FeedbackModel(metadata, content)
        
        return feedback
    
    def _generate_text_content(self, source_type, feedback_type):
        """
        生成文本内容
        
        Args:
            source_type: 反馈来源类型
            feedback_type: 反馈类型
            
        Returns:
            TextContent: 生成的文本内容
        """
        text = ""
        
        # 根据来源类型和反馈类型生成不同的文本内容
        if 'doctor' in str(source_type):
            if feedback_type == FeedbackType.DIAGNOSTIC:
                symptom = random.choice(self.symptoms)
                diagnosis = random.choice(self.diagnoses)
                examination = random.choice(self.examinations)
                text = f"患者主诉{symptom}，经过检查考虑为{diagnosis}，建议进行{examination}以确诊。"
            elif feedback_type == FeedbackType.THERAPEUTIC:
                diagnosis = random.choice(self.diagnoses)
                treatment = random.choice(self.treatments)
                text = f"针对患者的{diagnosis}，建议采用{treatment}，同时注意定期复查。"
            else:
                text = f"患者情况稳定，继续按照现有方案治疗，一周后复诊。"
        
        elif 'patient' in str(source_type):
            symptom1 = random.choice(self.symptoms)
            symptom2 = random.choice(self.symptoms)
            text = f"我最近感到{symptom1}，同时还有{symptom2}，吃了药后有所缓解，但还是不太舒服。"
        
        elif 'system' in str(source_type):
            examination = random.choice(self.examinations)
            if random.random() < 0.7:  # 70%概率正常
                text = f"{examination}检查结果正常，未见明显异常。"
            else:  # 30%概率异常
                diagnosis = random.choice(self.diagnoses)
                text = f"{examination}检查发现异常，提示可能存在{diagnosis}，建议进一步检查。"
        
        elif 'knowledge' in str(source_type):
            diagnosis = random.choice(self.diagnoses)
            treatment1 = random.choice(self.treatments)
            treatment2 = random.choice(self.treatments)
            text = f"根据最新临床指南，对于{diagnosis}患者，推荐采用{treatment1}和{treatment2}联合治疗，可显著提高治疗效果。"
        
        else:
            text = "反馈内容"
        
        return TextContent(text=text)
    
    def _generate_structured_content(self, source_type, feedback_type):
        """
        生成结构化内容
        
        Args:
            source_type: 反馈来源类型
            feedback_type: 反馈类型
            
        Returns:
            StructuredContent: 生成的结构化内容
        """
        data = {}
        
        # 根据来源类型和反馈类型生成不同的结构化内容
        if 'system' in str(source_type):
            if 'imaging' in str(source_type):
                examination = random.choice(["X线", "CT", "MRI", "超声", "内镜"])
                region = random.choice(["头部", "胸部", "腹部", "四肢", "脊柱"])
                if random.random() < 0.7:  # 70%概率正常
                    findings = "未见明显异常"
                    conclusion = f"正常{region}{examination}表现"
                else:  # 30%概率异常
                    diagnosis = random.choice(self.diagnoses)
                    findings = f"发现{diagnosis}相关改变"
                    conclusion = f"考虑{diagnosis}可能，建议结合临床"
                
                data = {
                    "examination_type": examination,
                    "region": region,
                    "findings": findings,
                    "conclusion": conclusion
                }
            
            elif 'lab' in str(source_type):
                test_type = random.choice(["血常规", "生化", "免疫", "微生物", "病理"])
                test_items = {}
                for i in range(random.randint(3, 6)):
                    item_name = f"检测项目{i+1}"
                    if random.random() < 0.7:  # 70%概率正常
                        item_value = f"正常值 (参考范围内)"
                    else:  # 30%概率异常
                        direction = random.choice(["升高", "降低"])
                        item_value = f"{direction} (超出参考范围)"
                    test_items[item_name] = item_value
                
                data = {
                    "test_type": test_type,
                    "test_items": test_items,
                    "summary": "请结合临床综合判断"
                }
            
            elif 'ehr' in str(source_type):
                vital_signs = {
                    "体温": f"{36 + random.random():.1f}°C",
                    "脉搏": f"{60 + random.randint(0, 40)}次/分",
                    "呼吸": f"{16 + random.randint(0, 8)}次/分",
                    "血压": f"{110 + random.randint(0, 40)}/{70 + random.randint(0, 20)}mmHg",
                    "血氧饱和度": f"{95 + random.randint(0, 5)}%"
                }
                
                data = {
                    "record_type": "生命体征",
                    "vital_signs": vital_signs,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        else:
            # 默认结构化数据
            data = {
                "item1": "value1",
                "item2": "value2",
                "item3": "value3"
            }
        
        return StructuredContent(data=data)
    
    def generate_feedback_by_type(self, feedback_type, count=5, with_relations=True):
        """
        生成特定类型的反馈数据集
        
        Args:
            feedback_type: 反馈类型
            count: 反馈数量
            with_relations: 是否生成反馈之间的关系
            
        Returns:
            List[FeedbackModel]: 反馈列表
        """
        feedbacks = []
        
        # 生成不同来源但相同类型的反馈
        source_types = list(SourceType)
        for i in range(count):
            source_type = source_types[i % len(source_types)]
            feedback = self.generate_random_feedback(source_type=source_type, feedback_type=feedback_type)
            feedbacks.append(feedback)
        
        # 生成反馈之间的关系
        if with_relations and len(feedbacks) >= 2:
            relation_count = min(count - 1, count // 2)
            for i in range(relation_count):
                source_idx = i
                target_idx = (i + 1) % count  # 形成一个环形关系链
                
                relation_type = random.choice(list(RelationType))
                strength = random.random() * 0.5 + 0.5  # 0.5-1.0之间的随机值
                
                relation = RelationModel(
                    source_id=feedbacks[source_idx].feedback_id,
                    target_id=feedbacks[target_idx].feedback_id,
                    relation_type=relation_type,
                    strength=strength
                )
                
                feedbacks[source_idx].add_relation(relation)
        
        return feedbacks
    
    def generate_feedback_set(self, count=10, with_relations=True):
        """
        生成反馈集合
        
        Args:
            count: 反馈数量
            with_relations: 是否生成反馈之间的关系
            
        Returns:
            List[FeedbackModel]: 反馈列表
        """
        feedbacks = []
        
        # 生成不同来源的反馈
        source_types = list(SourceType)
        for i in range(count):
            source_type = source_types[i % len(source_types)]
            feedback = self.generate_random_feedback(source_type=source_type)
            feedbacks.append(feedback)
        
        # 生成反馈之间的关系
        if with_relations and len(feedbacks) >= 2:
            relation_count = random.randint(count // 3, count // 2)
            for _ in range(relation_count):
                source_idx = random.randint(0, len(feedbacks) - 1)
                target_idx = random.randint(0, len(feedbacks) - 1)
                while source_idx == target_idx:
                    target_idx = random.randint(0, len(feedbacks) - 1)
                
                relation_type = random.choice(list(RelationType))
                strength = random.random() * 0.5 + 0.5  # 0.5-1.0之间的随机值
                
                relation = RelationModel(
                    source_id=feedbacks[source_idx].feedback_id,
                    target_id=feedbacks[target_idx].feedback_id,
                    relation_type=relation_type,
                    strength=strength
                )
                
                feedbacks[source_idx].add_relation(relation)
        
        return feedbacks
    
    def generate_diverse_feedback_set(self, count=10, time_span_days=30):
        """
        生成具有多样性的反馈数据集，包含不同来源、不同类型和不同时间的反馈
        
        Args:
            count: 反馈数量
            time_span_days: 时间跨度（天）
            
        Returns:
            List[FeedbackModel]: 反馈列表
        """
        feedbacks = []
        
        # 确保包含所有来源类型
        source_types = list(SourceType)
        # 确保包含所有反馈类型
        feedback_types = list(FeedbackType)
        
        # 生成不同来源、不同类型、不同时间的反馈
        for i in range(count):
            # 循环使用不同的来源类型
            source_type = source_types[i % len(source_types)]
            # 循环使用不同的反馈类型
            feedback_type = feedback_types[i % len(feedback_types)]
            # 生成不同的时间戳，均匀分布在指定的时间跨度内
            days_ago = (i * time_span_days) // count
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # 生成反馈
            feedback = self.generate_random_feedback(
                source_type=source_type,
                feedback_type=feedback_type,
                timestamp=timestamp
            )
            feedbacks.append(feedback)
        
        # 生成反馈之间的关系网络
        if count >= 3:
            # 创建一个小型关系网络，每个反馈至少与一个其他反馈有关系
            for i in range(count):
                # 随机选择1-3个目标反馈建立关系
                relation_count = random.randint(1, min(3, count-1))
                targets = random.sample([j for j in range(count) if j != i], relation_count)
                
                for target in targets:
                    relation_type = random.choice(list(RelationType))
                    strength = random.random() * 0.5 + 0.5  # 0.5-1.0之间的随机值
                    
                    relation = RelationModel(
                        source_id=feedbacks[i].feedback_id,
                        target_id=feedbacks[target].feedback_id,
                        relation_type=relation_type,
                        strength=strength
                    )
                    
                    feedbacks[i].add_relation(relation)
        
        return feedbacks
    
    def generate_medical_scenario(self, scenario_type="common"):
        """
        生成医疗场景数据
        
        Args:
            scenario_type: 场景类型，可选值："common"(常见病例), "emergency"(急诊), "chronic"(慢性病), "complex"(复杂病例)
            
        Returns:
            List[FeedbackModel]: 反馈列表
        """
        feedbacks = []
        
        if scenario_type == "emergency":
            # 急诊场景：心肌梗死
            # 患者反馈
            patient_metadata = MetadataModel(
                source=SourceType.HUMAN_PATIENT,
                feedback_type=FeedbackType.TEXTUAL,
                timestamp=datetime.now() - timedelta(hours=2),
                tags=["emergency", "chest_pain"]
            )
            patient_content = TextContent(
                text="我突然感到胸口剧烈疼痛，像是被重物压住一样，伴有出汗和呼吸困难，疼痛持续了约30分钟。"
            )
            patient_feedback = FeedbackModel(patient_metadata, patient_content)
            feedbacks.append(patient_feedback)
            
            # 急诊医生反馈
            doctor_metadata = MetadataModel(
                source="human.doctor.emergency",
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(hours=1, minutes=30),
                tags=["urgent", "cardiac"]
            )
            doctor_content = TextContent(
                text="患者表现为典型的心前区疼痛，伴有冷汗和呼吸困难，考虑急性冠脉综合征可能，建议立即心电图检查和心肌酶谱检测。"
            )
            doctor_feedback = FeedbackModel(doctor_metadata, doctor_content)
            feedbacks.append(doctor_feedback)
            
            # 心电图检查
            ecg_metadata = MetadataModel(
                source=SourceType.SYSTEM_EHR,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(hours=1),
                tags=["ecg", "test_result"]
            )
            ecg_content = StructuredContent(
                data={
                    "examination_type": "ECG",
                    "findings": "II、III、aVF导联ST段抬高>2mm",
                    "interpretation": "符合急性下壁心肌梗死表现",
                    "recommendation": "建议紧急冠脉介入治疗"
                }
            )
            ecg_feedback = FeedbackModel(ecg_metadata, ecg_content)
            feedbacks.append(ecg_feedback)
            
            # 心肌酶检查
            enzyme_metadata = MetadataModel(
                source=SourceType.SYSTEM_LAB,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(minutes=45),
                tags=["cardiac_enzymes", "test_result"]
            )
            enzyme_content = StructuredContent(
                data={
                    "test_type": "心肌酶谱",
                    "test_items": {
                        "肌钙蛋白I": "2.8 ng/mL (参考值: <0.04)",
                        "肌酸激酶同工酶": "42 U/L (参考值: <25)",
                        "肌红蛋白": "180 ng/mL (参考值: <90)"
                    },
                    "interpretation": "肌肉损伤标志物明显升高，符合急性心肌梗死"
                }
            )
            enzyme_feedback = FeedbackModel(enzyme_metadata, enzyme_content)
            feedbacks.append(enzyme_feedback)
            
            # 心内科医生反馈
            cardiologist_metadata = MetadataModel(
                source="human.doctor.cardiologist",
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(minutes=30),
                tags=["treatment", "intervention"]
            )
            cardiologist_content = TextContent(
                text="患者诊断为急性ST段抬高型心肌梗死(STEMI)，右冠状动脉闭塞，建议立即行经皮 coronary arteri介入治疗(PCI)，同时给予抗血小板、抗凝、他汀类药物等基础治疗。"
            )
            cardiologist_feedback = FeedbackModel(cardiologist_metadata, cardiologist_content)
            feedbacks.append(cardiologist_feedback)
            
            # 指南反馈
            guideline_metadata = MetadataModel(
                source=SourceType.KNOWLEDGE_LITERATURE,
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(days=180),  # 半年前的指南
                tags=["guideline", "STEMI"]
            )
            guideline_content = TextContent(
                text="对于ST段抬高型心肌梗死(STEMI)患者，推荐在症状发作后90分钟内进行直接经皮 coronary arteri介入治疗(PCI)。如无法及时进行PCI，应考虑溶栓治疗。同时给予抗血小板、抗凝、他汀类药物等基础治疗。"
            )
            guideline_feedback = FeedbackModel(guideline_metadata, guideline_content)
            feedbacks.append(guideline_feedback)
            
        elif scenario_type == "chronic":
            # 慢性病场景：2型糖尿病
            # 患者反馈
            patient_metadata = MetadataModel(
                source=SourceType.HUMAN_PATIENT,
                feedback_type=FeedbackType.TEXTUAL,
                timestamp=datetime.now() - timedelta(days=7),
                tags=["follow_up", "diabetes"]
            )
            patient_content = TextContent(
                text="最近一个月我一直按时服药，但血糖还是不太稳定，尤其是早上空腹血糖偏高，大约在8-10mmol/L之间，而且经常感到口渴和乏力。"
            )
            patient_feedback = FeedbackModel(patient_metadata, patient_content)
            feedbacks.append(patient_feedback)
            
            # 血糖监测数据
            glucose_metadata = MetadataModel(
                source=SourceType.SYSTEM_EHR,
                feedback_type=FeedbackType.NUMERIC,
                timestamp=datetime.now() - timedelta(days=3),
                tags=["glucose_monitoring", "diabetes"]
            )
            glucose_content = StructuredContent(
                data={
                    "record_type": "血糖监测",
                    "measurements": {
                        "空腹血糖": "9.2 mmol/L (参考值: 3.9-6.1)",
                        "餐后2小时血糖": "12.5 mmol/L (参考值: <7.8)",
                        "糖化血红蛋白": "8.1% (参考值: <6.5%)"
                    },
                    "trend": "血糖控制不佳，较前次检查有所上升"
                }
            )
            glucose_feedback = FeedbackModel(glucose_metadata, glucose_content)
            feedbacks.append(glucose_feedback)
            
            # 内分泌科医生反馈
            doctor_metadata = MetadataModel(
                source="human.doctor.endocrinologist",
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(days=1),
                tags=["treatment_adjustment", "diabetes"]
            )
            doctor_content = TextContent(
                text="患者2型糖尿病血糖控制不佳，建议调整用药方案：1. 二甲双胍剂量增加至每日2000mg；2. 加用SGLT-2抑制剂恩格列净10mg每日一次；3. 严格控制饮食，减少碳水化合物摄入；4. 增加有氧运动，每周至少150分钟；5. 一周后复查空腹及餐后血糖。"
            )
            doctor_feedback = FeedbackModel(doctor_metadata, doctor_content)
            feedbacks.append(doctor_feedback)
            
            # 营养师反馈
            nutritionist_metadata = MetadataModel(
                source="human.nutritionist",
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(hours=12),
                tags=["diet", "diabetes"]
            )
            nutritionist_content = TextContent(
                text="建议患者采用低碳水、高纤维饮食模式，每日碳水化合物摄入控制在150g以内，增加蔬菜和优质蛋白质摄入，避免精制碳水化合物和添加糖，分餐进食，保持规律三餐，避免夜间进食。"
            )
            nutritionist_feedback = FeedbackModel(nutritionist_metadata, nutritionist_content)
            feedbacks.append(nutritionist_feedback)
            
            # 指南反馈
            guideline_metadata = MetadataModel(
                source=SourceType.KNOWLEDGE_LITERATURE,
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(days=365),  # 一年前的指南
                tags=["guideline", "diabetes"]
            )
            guideline_content = TextContent(
                text="对于2型糖尿病患者，建议个体化血糖控制目标，一般糖化血红蛋白控制在7%以下。二甲双胍是首选口服降糖药物，如单药治疗效果不佳，可联合SGLT-2抑制剂、GLP-1受体激动剂、DPP-4抑制剂等。生活方式干预是基础治疗，包括饮食控制、规律运动、戒烟限酒等。"
            )
            guideline_feedback = FeedbackModel(guideline_metadata, guideline_content)
            feedbacks.append(guideline_feedback)
            
        elif scenario_type == "complex":
            # 复杂病例场景：多系统疾病（系统性红斑狼疮）
            # 患者反馈
            patient_metadata = MetadataModel(
                source=SourceType.HUMAN_PATIENT,
                feedback_type=FeedbackType.TEXTUAL,
                timestamp=datetime.now() - timedelta(days=14),
                tags=["complex", "autoimmune"]
            )
            patient_content = TextContent(
                text="我最近出现了多个关节疼痛，尤其是手指和膝盖，同时脸上出现了红斑，容易疲劳，有时还会发热。这些症状断断续续持续了两个多月了。"
            )
            patient_feedback = FeedbackModel(patient_metadata, patient_content)
            feedbacks.append(patient_feedback)
            
            # 风湿免疫科医生反馈
            doctor_metadata = MetadataModel(
                source="human.doctor.rheumatologist",
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(days=10),
                tags=["autoimmune", "consultation"]
            )
            doctor_content = TextContent(
                text="患者表现为多关节炎、面部蝶形红斑、乏力、低热症状，考虑系统性红斑狼疮可能，建议完善自身抗体检测、血常规、肾功能等检查。"
            )
            doctor_feedback = FeedbackModel(doctor_metadata, doctor_content)
            feedbacks.append(doctor_feedback)
            
            # 实验室检查结果
            lab_metadata = MetadataModel(
                source=SourceType.SYSTEM_LAB,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(days=7),
                tags=["lab_result", "autoimmune"]
            )
            lab_content = StructuredContent(
                data={
                    "test_type": "自身抗体检测",
                    "test_items": {
                        "抗核抗体(ANA)": "1:320 阳性 (参考值: <1:80)",
                        "抗dsDNA抗体": "阳性",
                        "抗Sm抗体": "阳性",
                        "补体C3": "0.5 g/L (参考值: 0.9-1.8)",
                        "补体C4": "0.08 g/L (参考值: 0.1-0.4)"
                    },
                    "blood_routine": {
                        "白细胞": "3.2×10^9/L (参考值: 4.0-10.0)",
                        "血红蛋白": "105 g/L (参考值: 120-160)",
                        "血小板": "90×10^9/L (参考值: 100-300)"
                    },
                    "kidney_function": {
                        "肌酐": "90 μmol/L (参考值: 44-106)",
                        "尿蛋白": "2+ (参考值: 阴性)"
                    },
                    "interpretation": "自身抗体高滴度阳性，符合系统性红斑狼疮血清学特征，伴有轻度血细胞减少和蛋白尿"
                }
            )
            lab_feedback = FeedbackModel(lab_metadata, lab_content)
            feedbacks.append(lab_feedback)
            
            # 肾脏科医生会诊
            nephrologist_metadata = MetadataModel(
                source="human.doctor.nephrologist",
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(days=5),
                tags=["consultation", "nephritis"]
            )
            nephrologist_content = TextContent(
                text="患者出现蛋白尿，考虑狼疮性肾炎可能，建议行肾穿刺活检明确诊断和分型，以指导后续治疗。"
            )
            nephrologist_feedback = FeedbackModel(nephrologist_metadata, nephrologist_content)
            feedbacks.append(nephrologist_feedback)
            
            # 病理检查结果
            pathology_metadata = MetadataModel(
                source=SourceType.SYSTEM_LAB,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(days=2),
                tags=["pathology", "biopsy"]
            )
            pathology_content = StructuredContent(
                data={
                    "specimen": "肾穿刺活检组织",
                    "light_microscopy": "系膜细胞增生，部分毛细血管壁增厚，见免疫复合物沉积",
                    "immunofluorescence": "IgG、IgA、IgM、C3、C1q沉积",
                    "electron_microscopy": "系膜区及部分上皮下见电子致密物沉积",
                    "diagnosis": "狼疮性肾炎III型(局灶增生性狼疮性肾炎)",
                    "recommendation": "建议激素联合免疫抑制剂治疗"
                }
            )
            pathology_feedback = FeedbackModel(pathology_metadata, pathology_content)
            feedbacks.append(pathology_feedback)
            
            # 风湿免疫科治疗方案
            treatment_metadata = MetadataModel(
                source="human.doctor.rheumatologist",
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(days=1),
                tags=["treatment", "SLE"]
            )
            treatment_content = TextContent(
                text="患者确诊为系统性红斑狼疮伴III型狼疮性肾炎，建议以下治疗方案：1. 泼尼松40mg/日，逐渐减量；2. 羟氯喹200mg每日两次；3. 环磷酰胺静脉冲击治疗，首次0.75g/m²，后续每月一次；4. 定期监测血常规、肾功能、尿常规等指标；5. 避免暴晒，注意休息。"
            )
            treatment_feedback = FeedbackModel(treatment_metadata, treatment_content)
            feedbacks.append(treatment_feedback)
            
            # 指南反馈
            guideline_metadata = MetadataModel(
                source=SourceType.KNOWLEDGE_LITERATURE,
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(days=365),  # 一年前的指南
                tags=["guideline", "SLE"]
            )
            guideline_content = TextContent(
                text="对于III型狼疮性肾炎，推荐使用糖皮质激素联合免疫抑制剂治疗。诱导期可选择环磷酰胺或霉酚酸酯，维持期可选择霉酚酸酯或硫唑嘌呤。羟氯喹应作为基础治疗用药。对于难治性病例，可考虑利妥昔单抗等生物制剂。"
            )
            guideline_feedback = FeedbackModel(guideline_metadata, guideline_content)
            feedbacks.append(guideline_feedback)
            
        else:  # 默认为常见病例
            # 患者反馈
            patient_metadata = MetadataModel(
                source=SourceType.HUMAN_PATIENT,
                feedback_type=FeedbackType.TEXTUAL,
                timestamp=datetime.now() - timedelta(hours=12),
                tags=["symptom"]
            )
            patient_content = TextContent(
                text=f"我最近感到{random.choice(self.symptoms)}，同时还有{random.choice(self.symptoms)}，这种情况持续了几天了。"
            )
            patient_feedback = FeedbackModel(patient_metadata, patient_content)
            feedbacks.append(patient_feedback)
            
            # 医生反馈
            doctor_metadata = MetadataModel(
                source=SourceType.HUMAN_DOCTOR,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(hours=6),
                tags=["consultation"]
            )
            diagnosis = random.choice(self.diagnoses)
            examination = random.choice(self.examinations)
            doctor_content = TextContent(
                text=f"患者可能患有{diagnosis}，建议进行{examination}检查以确诊。"
            )
            doctor_feedback = FeedbackModel(doctor_metadata, doctor_content)
            feedbacks.append(doctor_feedback)
            
            # 检查结果
            test_metadata = MetadataModel(
                source=SourceType.SYSTEM_LAB,
                feedback_type=FeedbackType.DIAGNOSTIC,
                timestamp=datetime.now() - timedelta(hours=3),
                tags=["test_result"]
            )
            if random.random() < 0.7:  # 70%概率确诊
                result = f"检查结果支持{diagnosis}诊断"
            else:  # 30%概率需要进一步检查
                result = f"检查结果不典型，建议进一步检查"
            
            test_content = StructuredContent(
                data={
                    "examination": examination,
                    "result": result,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            test_feedback = FeedbackModel(test_metadata, test_content)
            feedbacks.append(test_feedback)
            
            # 治疗建议
            treatment_metadata = MetadataModel(
                source=SourceType.HUMAN_DOCTOR,
                feedback_type=FeedbackType.THERAPEUTIC,
                timestamp=datetime.now() - timedelta(hours=2),
                tags=["treatment"]
            )
            treatment = random.choice(self.treatments)
            treatment_content = TextContent(
                text=f"针对患者的{diagnosis}，建议采用{treatment}，同时注意休息，多饮水。"
            )
            treatment_feedback = FeedbackModel(treatment_metadata, treatment_content)
            feedbacks.append(treatment_feedback)
        
        # 生成反馈之间的关系
        if len(feedbacks) >= 2:
            for i in range(1, len(feedbacks)):
                # 每个反馈与前一个反馈建立关系
                relation_type = random.choice(list(RelationType))
                strength = random.random() * 0.5 + 0.5  # 0.5-1.0之间的随机值
                
                relation = RelationModel(
                    source_id=feedbacks[i].feedback_id,
                    target_id=feedbacks[i-1].feedback_id,
                    relation_type=relation_type,
                    strength=strength
                )
                
                feedbacks[i].add_relation(relation)
        
        return feedbacks

    def generate_edge_case_feedback(self, case_type="empty"):
        """
        生成边界情况的反馈数据，用于测试系统的健壮性
        
        Args:
            case_type: 边界情况类型，可选值：
                - "empty": 空内容
                - "long": 极长内容
                - "special_chars": 特殊字符
                - "future": 未来时间戳
                - "old": 非常旧的时间戳
            
        Returns:
            FeedbackModel: 边界情况的反馈
        """
        # 随机选择来源类型和反馈类型
        source_type = random.choice(list(SourceType))
        feedback_type = random.choice(list(FeedbackType))
        
        # 根据边界情况类型生成不同的内容和元数据
        if case_type == "empty":
            # 空内容反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now(),
                tags=[]
            )
            content = TextContent(text="")
            
        elif case_type == "long":
            # 极长内容反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now(),
                tags=["long_content"]
            )
            # 生成一个长度约为1000字符的文本
            long_text = ""
            for _ in range(50):
                long_text += f"这是一段非常长的文本内容，用于测试系统处理极长反馈的能力。包含了{random.choice(self.symptoms)}和{random.choice(self.diagnoses)}等医疗信息。"
            content = TextContent(text=long_text)
            
        elif case_type == "special_chars":
            # 特殊字符内容反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now(),
                tags=["special_chars"]
            )
            special_text = "特殊字符测试：!@#$%^&*()_+{}[]|\\:;\"'<>,.?/\n\t\r中英文混合 English mixed 123456 \u4e2d\u6587Unicode"
            content = TextContent(text=special_text)
            
        elif case_type == "future":
            # 未来时间戳反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now() + timedelta(days=365),  # 一年后
                tags=["future"]
            )
            content = TextContent(text="这是一条来自未来的反馈")
            
        elif case_type == "old":
            # 非常旧的时间戳反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now() - timedelta(days=3650),  # 十年前
                tags=["old"]
            )
            content = TextContent(text="这是一条非常旧的历史反馈")
            
        else:
            # 默认情况，创建一个普通反馈
            metadata = MetadataModel(
                source=source_type,
                feedback_type=feedback_type,
                timestamp=datetime.now(),
                tags=["default"]
            )
            content = TextContent(text="默认边界情况反馈")
        
        # 创建反馈
        feedback = FeedbackModel(metadata, content)
        
        return feedback