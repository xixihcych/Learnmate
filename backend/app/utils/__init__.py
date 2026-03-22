"""
工具函数模块
"""
from .document_parser import (
    parse_document,
    parse_pdf,
    parse_word,
    parse_ppt,
    get_document_info,
    DocumentParser
)

__all__ = [
    'parse_document',
    'parse_pdf',
    'parse_word',
    'parse_ppt',
    'get_document_info',
    'DocumentParser'
]
