"""
知识图谱模块测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.knowledge_graph import KnowledgeGraph, get_knowledge_graph


def test_extract_entities():
    """测试实体和关系抽取"""
    print("=" * 50)
    print("测试实体和关系抽取")
    print("=" * 50)
    
    test_text = """
    人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
    机器学习是AI的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。
    深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的工作方式。
    自然语言处理（NLP）是AI的一个重要分支，它使计算机能够理解、解释和生成人类语言。
    Python是一种广泛用于AI开发的编程语言。
    """
    
    try:
        kg = get_knowledge_graph()
        print(f"\n输入文本:\n{test_text[:200]}...")
        
        print("\n正在抽取实体和关系...")
        result = kg.process_text(test_text)
        
        print(f"\n✓ 抽取成功")
        print(f"  三元组数量: {result['triples_count']}")
        print(f"  实体数量: {result['entities_count']}")
        print(f"  关系数量: {result['relations_count']}")
        
        # 显示部分三元组
        print(f"\n部分三元组:")
        for i, triple in enumerate(kg.triples[:5], 1):
            print(f"  {i}. ({triple[0]}, {triple[1]}, {triple[2]})")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_visualization():
    """测试知识图谱可视化"""
    print("\n" + "=" * 50)
    print("测试知识图谱可视化")
    print("=" * 50)
    
    try:
        kg = get_knowledge_graph()
        
        # 检查是否有数据
        stats = kg.get_statistics()
        if stats["nodes_count"] == 0:
            print("⚠️  知识图谱为空，先添加一些数据...")
            # 添加测试数据
            test_text = """
            人工智能是计算机科学的分支。
            机器学习是AI的子领域。
            深度学习是机器学习的子集。
            """
            kg.process_text(test_text)
        
        print("\n正在生成可视化...")
        output_path = kg.visualize("test_kg.html")
        
        print(f"✓ 可视化生成成功")
        print(f"  文件路径: {output_path}")
        print(f"  节点数: {stats['nodes_count']}")
        print(f"  边数: {stats['edges_count']}")
        print(f"\n可以在浏览器中打开 {output_path} 查看知识图谱")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_entity_info():
    """测试获取实体信息"""
    print("\n" + "=" * 50)
    print("测试获取实体信息")
    print("=" * 50)
    
    try:
        kg = get_knowledge_graph()
        
        # 获取第一个实体
        if kg.graph.number_of_nodes() > 0:
            entity = list(kg.graph.nodes())[0]
            print(f"\n查询实体: {entity}")
            
            info = kg.get_entity_info(entity)
            
            print(f"\n✓ 实体信息:")
            print(f"  实体: {info['entity']}")
            print(f"  度: {info['degree']}")
            print(f"  入边关系数: {len(info['incoming_relations'])}")
            print(f"  出边关系数: {len(info['outgoing_relations'])}")
            print(f"  相关笔记数: {len(info['notes'])}")
            
            if info['outgoing_relations']:
                print(f"\n  出边关系:")
                for rel in info['outgoing_relations'][:3]:
                    print(f"    {entity} --{rel['relation']}--> {rel['to']}")
        else:
            print("⚠️  知识图谱为空")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_statistics():
    """测试统计信息"""
    print("\n" + "=" * 50)
    print("测试统计信息")
    print("=" * 50)
    
    try:
        kg = get_knowledge_graph()
        stats = kg.get_statistics()
        
        print("\n知识图谱统计:")
        print(f"  节点数: {stats['nodes_count']}")
        print(f"  边数: {stats['edges_count']}")
        print(f"  三元组数: {stats['triples_count']}")
        print(f"  实体数: {stats['entities_count']}")
        print(f"  关系类型数: {stats['relations_count']}")
        print(f"  笔记数: {stats['notes_count']}")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_full_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 50)
    print("测试完整工作流程")
    print("=" * 50)
    
    print("\n流程:")
    print("1. 文本输入")
    print("2. 使用 Gemini API 抽取实体关系")
    print("3. 生成三元组")
    print("4. 构建 networkx 图结构")
    print("5. 使用 pyvis 生成可视化网页")
    
    test_texts = [
        """
        人工智能（AI）是计算机科学的一个分支。
        机器学习是AI的子领域，使用算法从数据中学习。
        深度学习是机器学习的子集，使用神经网络。
        """,
        """
        Python是一种编程语言，广泛用于AI开发。
        TensorFlow是Google开发的深度学习框架。
        PyTorch是Facebook开发的深度学习框架。
        """
    ]
    
    try:
        kg = get_knowledge_graph()
        
        # 步骤1-3: 处理文本
        print("\n步骤1-3: 处理文本并抽取实体关系")
        for i, text in enumerate(test_texts, 1):
            result = kg.process_text(text, source_id=i)
            print(f"  文本{i}: {result['triples_count']} 个三元组")
        
        # 步骤4: 构建图结构（已完成）
        print("\n步骤4: 构建networkx图结构")
        stats = kg.get_statistics()
        print(f"  ✓ 图结构已构建")
        print(f"    节点数: {stats['nodes_count']}")
        print(f"    边数: {stats['edges_count']}")
        
        # 步骤5: 生成可视化
        print("\n步骤5: 生成pyvis可视化网页")
        output_path = kg.visualize("full_workflow_kg.html")
        print(f"  ✓ 可视化已生成: {output_path}")
        
        print("\n✓ 完整流程测试成功！")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


if __name__ == "__main__":
    print("\n知识图谱模块测试\n")
    
    # 检查Gemini API配置
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  警告: GEMINI_API_KEY 环境变量未设置")
        print("   请设置环境变量或创建 .env 文件")
        print("   获取API密钥: https://makersuite.google.com/app/apikey\n")
    
    # 运行测试
    test_extract_entities()
    test_statistics()
    test_entity_info()
    test_visualization()
    test_full_workflow()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)






