"""
文本分块工具
将长文本分割成适合向量化的块

支持多种分割策略：
1. 按固定大小分割（带重叠）
2. 按段落分割
3. 智能分割（在句子边界分割）
"""
from typing import List
import re


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    将文本分割成固定大小的块
    
    Args:
        text: 原始文本
        chunk_size: 每个块的大小（字符数）
        chunk_overlap: 块之间的重叠大小
    
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句号、换行符等位置分割
        if end < len(text):
            # 向后查找句号或换行符
            for i in range(end, max(start, end - 100), -1):
                if text[i] in ['。', '\n', '.', '!', '?']:
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - chunk_overlap
    
    return chunks


def split_text_by_paragraph(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    按段落分割文本，如果段落太长则进一步分割
    
    Args:
        text: 原始文本
        max_chunk_size: 最大块大小
    
    Returns:
        文本块列表
    """
    # 先按双换行符分割段落
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 移除多余的空白字符
        para = re.sub(r'\s+', ' ', para)
        
        if len(para) <= max_chunk_size:
            chunks.append(para)
        else:
            # 段落太长，进一步分割
            sub_chunks = split_text(para, chunk_size=max_chunk_size)
            chunks.extend(sub_chunks)
    
    return chunks


def split_text_by_sentences(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    按句子分割文本
    
    Args:
        text: 原始文本
        chunk_size: 每个块的大小（字符数）
        chunk_overlap: 块之间的重叠大小
    
    Returns:
        文本块列表
    """
    # 中英文句子分隔符
    sentence_endings = r'[。！？.!?\n]'
    sentences = re.split(sentence_endings, text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_size = len(sentence)
        
        # 如果当前块加上新句子超过大小，保存当前块
        if current_size + sentence_size > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            
            # 处理重叠：保留最后几个句子
            overlap_sentences = []
            overlap_size = 0
            for s in reversed(current_chunk):
                if overlap_size + len(s) <= chunk_overlap:
                    overlap_sentences.insert(0, s)
                    overlap_size += len(s)
                else:
                    break
            
            current_chunk = overlap_sentences
            current_size = overlap_size
        
        current_chunk.append(sentence)
        current_size += sentence_size
    
    # 添加最后一个块
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append(chunk_text)
    
    return chunks


def smart_split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    智能分割文本，优先在段落边界，其次在句子边界
    
    Args:
        text: 原始文本
        chunk_size: 每个块的大小（字符数）
        chunk_overlap: 块之间的重叠大小
    
    Returns:
        文本块列表
    """
    # 先按段落分割
    paragraphs = split_text_by_paragraph(text, max_chunk_size=chunk_size * 2)
    
    chunks = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            # 段落太长，按句子分割
            para_chunks = split_text_by_sentences(para, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks.extend(para_chunks)
    
    return chunks

