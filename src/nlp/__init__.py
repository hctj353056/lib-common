# -*- coding: utf-8 -*-
"""
lib-common.nlp: NLP处理模块

包含：
- 分词
- 词性标注
- 形式化语言解析

(待完善)
"""

from typing import List, Dict


class SimpleTokenizer:
    """简单分词器"""
    
    def __init__(self):
        self.vocab: Dict[str, int] = {}
    
    def tokenize(self, text: str) -> List[str]:
        """中英文分词"""
        import re
        
        # 简单按空格和标点分词
        tokens = re.findall(r'[\w]+|[^\s\w]', text)
        return [t for t in tokens if t.strip()]
    
    def build_vocab(self, texts: List[str]):
        """构建词表"""
        for text in texts:
            for token in self.tokenize(text):
                if token not in self.vocab:
                    self.vocab[token] = len(self.vocab)


class RegexParser:
    """正则表达式解析器"""
    
    def __init__(self, pattern: str):
        import re
        self.pattern = re.compile(pattern)
    
    def findall(self, text: str) -> List[str]:
        """查找所有匹配"""
        return self.pattern.findall(text)
    
    def match(self, text: str) -> bool:
        """从头匹配"""
        return bool(self.pattern.match(text))
