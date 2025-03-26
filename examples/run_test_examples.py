# -*- coding: utf-8 -*-
"""
反馈系统测试示例运行脚本

该脚本提供了一个简单的命令行界面，用于运行不同的测试示例，展示反馈系统的各种功能。
"""

import sys
import os
import argparse

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# 导入测试示例
from examples.test_feedback_system import (
    test_generate_random_feedback,
    test_generate_feedback_set,
    test_generate_diverse_feedback_set,
    test_medical_scenarios,
    test_edge_cases,
    test_feedback_collection,
    test_feedback_system_pipeline
)

def main():
    """
    主函数，解析命令行参数并运行相应的测试示例
    """
    parser = argparse.ArgumentParser(description='反馈系统测试示例')
    parser.add_argument('--test', type=str, default='all',
                        choices=['all', 'random', 'set', 'diverse', 'medical', 'edge', 'collection', 'pipeline'],
                        help='要运行的测试示例')
    args = parser.parse_args()
    
    # 根据命令行参数运行相应的测试示例
    if args.test == 'all' or args.test == 'random':
        test_generate_random_feedback()
    
    if args.test == 'all' or args.test == 'set':
        test_generate_feedback_set()
    
    if args.test == 'all' or args.test == 'diverse':
        test_generate_diverse_feedback_set()
    
    if args.test == 'all' or args.test == 'medical':
        test_medical_scenarios()
    
    if args.test == 'all' or args.test == 'edge':
        test_edge_cases()
    
    if args.test == 'all' or args.test == 'collection':
        test_feedback_collection()
    
    if args.test == 'all' or args.test == 'pipeline':
        test_feedback_system_pipeline()

if __name__ == "__main__":
    main()