"""
知识库向量搜索系统测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.knowledge_base import KnowledgeBase, knowledge_base
from app.utils.vector_store import VectorStore


def test_add_document():
    """测试添加文档到知识库"""
    print("=" * 50)
    print("测试添加文档到知识库")
    print("=" * 50)
    
    # 测试文本
    test_text = """
    人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
    它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    
    机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。
    深度学习是机器学习的一个子集，它使用神经网络来模拟人脑的工作方式。
    
    自然语言处理（NLP）是人工智能的一个重要分支，它使计算机能够理解、解释和生成人类语言。
    """
    
    try:
        # 添加文档
        chunk_count = knowledge_base.add_document(
            document_id=1,
            text=test_text,
            filename="test_ai_doc.txt",
            metadata={'category': 'AI', 'author': 'Test'}
        )
        
        print(f"✓ 文档添加成功")
        print(f"  生成的文本块数量: {chunk_count}")
        
        # 获取统计信息
        stats = knowledge_base.get_stats()
        print(f"\n知识库统计:")
        print(f"  总文本块数: {stats.get('total_chunks', 0)}")
        print(f"  总文档数: {stats.get('total_documents', 0)}")
        print(f"  索引维度: {stats.get('index_dimension', 'N/A')}")
        
    except Exception as e:
        print(f"✗ 添加文档失败: {e}")


def test_search():
    """测试知识库搜索"""
    print("\n" + "=" * 50)
    print("测试知识库搜索")
    print("=" * 50)
    
    queries = [
        "什么是人工智能",
        "机器学习",
        "自然语言处理"
    ]
    
    for query in queries:
        try:
            results = knowledge_base.search(query=query, top_k=3)
            
            print(f"\n查询: {query}")
            print(f"找到 {len(results)} 个结果:")
            
            for i, result in enumerate(results, 1):
                print(f"\n  结果 {i}:")
                print(f"    文档ID: {result['document_id']}")
                print(f"    文件名: {result['filename']}")
                print(f"    相似度: {result['similarity']:.2%}")
                print(f"    距离分数: {result['score']:.4f}")
                print(f"    文本预览: {result['chunk_text'][:100]}...")
        
        except Exception as e:
            print(f"✗ 搜索失败: {e}")


def test_document_stats():
    """测试文档统计信息"""
    print("\n" + "=" * 50)
    print("测试文档统计信息")
    print("=" * 50)
    
    document_id = 1
    
    try:
        stats = knowledge_base.get_document_stats(document_id)
        print(f"文档 {document_id} 统计信息:")
        print(f"  文本块数量: {stats.get('chunk_count', 0)}")
        print(f"  平均块大小: {stats.get('avg_chunk_size', 0):.0f} 字符")
    except Exception as e:
        print(f"✗ 获取统计信息失败: {e}")


def test_text_splitting():
    """测试文本切分"""
    print("\n" + "=" * 50)
    print("测试文本切分")
    print("=" * 50)
    
    from app.utils.text_splitter import split_text, split_text_by_paragraph, smart_split_text
    
    long_text = """
    第一章：人工智能概述
    
    人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
    这些任务包括学习、推理、问题解决、感知和语言理解。
    
    第二章：机器学习基础
    
    机器学习是AI的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。
    机器学习算法通过分析数据来识别模式，然后使用这些模式对新数据进行预测。
    
    第三章：深度学习
    
    深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的工作方式。
    深度学习在图像识别、自然语言处理和语音识别等领域取得了显著的成功。
    """
    
    print("\n1. 固定大小切分（chunk_size=100）:")
    chunks1 = split_text(long_text, chunk_size=100, chunk_overlap=20)
    print(f"   生成 {len(chunks1)} 个文本块")
    for i, chunk in enumerate(chunks1[:3], 1):
        print(f"   块{i}: {chunk[:50]}...")
    
    print("\n2. 按段落切分:")
    chunks2 = split_text_by_paragraph(long_text, max_chunk_size=200)
    print(f"   生成 {len(chunks2)} 个文本块")
    for i, chunk in enumerate(chunks2[:3], 1):
        print(f"   块{i}: {chunk[:50]}...")
    
    print("\n3. 智能切分:")
    chunks3 = smart_split_text(long_text, chunk_size=150, chunk_overlap=30)
    print(f"   生成 {len(chunks3)} 个文本块")
    for i, chunk in enumerate(chunks3[:3], 1):
        print(f"   块{i}: {chunk[:50]}...")


def test_full_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 50)
    print("测试完整工作流程")
    print("=" * 50)
    
    print("\n流程：")
    print("1. 文本切分")
    print("2. 生成embedding")
    print("3. 存入FAISS")
    print("4. 用户搜索返回最相似文本")
    
    # 准备测试文档
    documents = [
        {
            'id': 10,
            'text': 'Python是一种高级编程语言，广泛用于数据科学、机器学习和Web开发。',
            'filename': 'python_intro.txt'
        },
        {
            'id': 11,
            'text': 'FastAPI是一个现代、快速的Web框架，用于构建API。它基于Python类型提示。',
            'filename': 'fastapi_intro.txt'
        },
        {
            'id': 12,
            'text': 'FAISS是Facebook开发的向量相似性搜索库，用于高效的大规模向量搜索。',
            'filename': 'faiss_intro.txt'
        }
    ]
    
    try:
        # 1-3. 添加文档（包含切分、生成embedding、存入FAISS）
        print("\n步骤1-3: 添加文档到知识库")
        for doc in documents:
            chunk_count = knowledge_base.add_document(
                document_id=doc['id'],
                text=doc['text'],
                filename=doc['filename']
            )
            print(f"  ✓ {doc['filename']}: {chunk_count} 个文本块")
        
        # 4. 搜索
        print("\n步骤4: 搜索知识库")
        search_queries = [
            "Python编程语言",
            "Web框架",
            "向量搜索"
        ]
        
        for query in search_queries:
            results = knowledge_base.search(query=query, top_k=2)
            print(f"\n  查询: {query}")
            print(f"  找到 {len(results)} 个结果:")
            for result in results:
                print(f"    - {result['filename']} (相似度: {result['similarity']:.2%})")
                print(f"      {result['chunk_text'][:60]}...")
    
    except Exception as e:
        print(f"✗ 工作流程测试失败: {e}")


if __name__ == "__main__":
    print("\n知识库向量搜索系统测试\n")
    
    # 运行测试
    test_text_splitting()
    test_add_document()
    test_search()
    test_document_stats()
    test_full_workflow()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)






