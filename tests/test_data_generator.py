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
                    "interpretation": "心肌损伤标志物明显升高，符合急性心肌梗死"
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
                text="患者诊断为急性ST段抬高型心肌梗死(STEMI)，右冠状动脉闭塞，建议立即行经皮冠状动脉介入治疗(PCI)，同时给予抗血小板、抗凝、他汀类药物等基础治疗。"
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
                text="对于ST段抬高型心肌梗死(STEMI)患者，推荐在症状发作后90分钟内进行直接经皮冠状动脉介入治疗(PCI)。如无法及时进行PCI，应考虑溶栓治疗。同时给予抗血小板、抗凝、他汀类药物等基础治疗。"
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
                text="我最近出现了多个