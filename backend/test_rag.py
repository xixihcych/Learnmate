"""
RAG问答系统测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.knowledge_base import knowledge_base
from app.services.gemini_service import GeminiService, get_gemini_service


def test_rag_workflow():
    """测试完整的RAG工作流程"""
    print("=" * 50)
    print("RAG问答系统完整流程测试")
    print("=" * 50)
    
    # 步骤1: 用户输入问题
    query = "什么是人工智能？"
    print(f"\n步骤1: 用户输入问题")
    print(f"  问题: {query}")
    
    # 步骤2: 在FAISS中检索相关文本
    print(f"\n步骤2: 在FAISS中检索相关文本")
    try:
        search_results = knowledge_base.search(
            query=query,
            top_k=5
        )
        
        if not search_results:
            print("  ⚠️  知识库中没有找到相关文档")
            print("  请先添加文档到知识库")
            return
        
        print(f"  ✓ 找到 {len(search_results)} 个相关文本块")
        for i, result in enumerate(search_results[:3], 1):
            print(f"    结果{i}: {result['filename']} (相似度: {result['similarity']:.2%})")
            print(f"            {result['chunk_text'][:100]}...")
    
    except Exception as e:
        print(f"  ✗ 检索失败: {e}")
        return
    
    # 步骤3: 将文本作为上下文
    print(f"\n步骤3: 构建上下文")
    context_texts = [result['chunk_text'] for result in search_results[:5]]
    print(f"  ✓ 构建了 {len(context_texts)} 个上下文文本块")
    print(f"  总上下文长度: {sum(len(ctx) for ctx in context_texts)} 字符")
    
    # 步骤4: 调用Gemini API生成回答
    print(f"\n步骤4: 调用Gemini API生成回答")
    try:
        gemini_service = get_gemini_service()
        
        print("  正在生成回答...")
        response = gemini_service.generate_response(
            query=query,
            context=context_texts,
            temperature=0.7
        )
        
        print(f"\n  ✓ Gemini回答生成成功")
        print(f"\n  回答内容:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    
    except ValueError as e:
        if "API密钥" in str(e) or "api_key" in str(e).lower():
            print(f"  ⚠️  Gemini API密钥未配置")
            print(f"  请设置环境变量 GEMINI_API_KEY")
            print(f"  或创建 .env 文件并添加: GEMINI_API_KEY=your_key")
        else:
            print(f"  ✗ 配置错误: {e}")
    except Exception as e:
        print(f"  ✗ Gemini API调用失败: {e}")
        print(f"  错误详情: {str(e)}")


def test_gemini_service():
    """测试Gemini服务"""
    print("\n" + "=" * 50)
    print("测试Gemini服务")
    print("=" * 50)
    
    try:
        gemini_service = get_gemini_service()
        print("✓ Gemini服务初始化成功")
        print(f"  模型: {gemini_service.model_name}")
        
        # 测试简单问答
        print("\n测试简单问答:")
        response = gemini_service.generate_response(
            query="用一句话解释什么是机器学习",
            context=["机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。"],
            temperature=0.7
        )
        print(f"  回答: {response}")
    
    except ValueError as e:
        if "API密钥" in str(e):
            print("⚠️  Gemini API密钥未配置")
            print("请设置环境变量 GEMINI_API_KEY")
        else:
            print(f"✗ 配置错误: {e}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")


def test_context_building():
    """测试上下文构建"""
    print("\n" + "=" * 50)
    print("测试上下文构建")
    print("=" * 50)
    
    # 模拟检索结果
    mock_results = [
        {
            'chunk_text': '人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。',
            'filename': 'ai_intro.pdf',
            'similarity': 0.95
        },
        {
            'chunk_text': '机器学习是AI的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。',
            'filename': 'ml_basics.pdf',
            'similarity': 0.88
        },
        {
            'chunk_text': '深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的工作方式。',
            'filename': 'dl_intro.pdf',
            'similarity': 0.82
        }
    ]
    
    query = "什么是人工智能？"
    
    # 构建上下文
    context_texts = [result['chunk_text'] for result in mock_results]
    
    print(f"问题: {query}")
    print(f"\n上下文文本 ({len(context_texts)} 个):")
    for i, ctx in enumerate(context_texts, 1):
        print(f"\n  [{i}] {ctx}")
    
    # 显示提示词构建
    print("\n构建的提示词预览:")
    print("-" * 50)
    prompt_preview = f"""你是一个智能助手，基于提供的上下文信息回答用户的问题。

上下文信息：
[来源1]
{context_texts[0]}

[来源2]
{context_texts[1]}

[来源3]
{context_texts[2]}

用户问题：{query}

请基于上述上下文信息回答用户的问题："""
    print(prompt_preview[:300] + "...")
    print("-" * 50)


if __name__ == "__main__":
    print("\nRAG问答系统测试\n")
    
    # 检查环境变量
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  警告: GEMINI_API_KEY 环境变量未设置")
        print("   请设置环境变量或创建 .env 文件")
        print("   获取API密钥: https://makersuite.google.com/app/apikey\n")
    
    # 运行测试
    test_context_building()
    test_gemini_service()
    test_rag_workflow()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)






