# -*- coding: utf-8 -*-
"""
lib-common VM模块: 虚拟机和解释器

包含：
- 简单虚拟机
- 字节码解释器
- 基础编译器框架

示例:
    from lib_common.vm import SimpleVM, Interpreter
    
    vm = SimpleVM()
    vm.load([("LOAD", 0), ("ADD", 1), ("PRINT", None)])
    vm.run()
"""

from typing import List, Dict, Any, Callable, Optional


class Instruction:
    """指令"""
    def __init__(self, op: str, arg: Any = None):
        self.op = op
        self.arg = arg
    
    def __repr__(self):
        if self.arg is not None:
            return f"{self.op} {self.arg}"
        return self.op


class SimpleVM:
    """简单虚拟机"""
    
    def __init__(self):
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.labels: Dict[str, int] = {}
        self.instructions: List[Instruction] = []
        self.ip: int = 0  # 指令指针
    
    def load(self, bytecode: List[tuple]):
        """
        加载字节码
        
        Args:
            bytecode: [(操作码, 参数), ...]
        """
        self.instructions = [Instruction(op, arg) for op, arg in bytecode]
        self._build_labels()
    
    def _build_labels(self):
        """构建标签表"""
        self.labels = {}
        for i, instr in enumerate(self.instructions):
            if instr.op.endswith(':'):
                self.labels[instr.op[:-1]] = i
    
    def run(self):
        """运行虚拟机"""
        self.ip = 0
        while self.ip < len(self.instructions):
            self._execute(self.instructions[self.ip])
            self.ip += 1
    
    def _execute(self, instr: Instruction):
        """执行指令"""
        op = instr.op.upper()
        
        if op == "PUSH":
            self.stack.append(instr.arg)
        
        elif op == "POP":
            self.stack.pop()
        
        elif op == "LOAD":
            self.stack.append(self.variables.get(instr.arg))
        
        elif op == "STORE":
            self.variables[instr.arg] = self.stack.pop()
        
        elif op == "ADD":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        
        elif op == "SUB":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        
        elif op == "MUL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        
        elif op == "DIV":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a / b)
        
        elif op == "PRINT":
            print(self.stack[-1] if self.stack else "")
        
        elif op == "JUMP":
            self.ip = self.labels[instr.arg] - 1  # -1因为循环会自动+1
        
        elif op == "JUMPIF":
            if self.stack.pop():
                self.ip = self.labels[instr.arg] - 1
        
        elif op == "HALT":
            self.ip = len(self.instructions)


class Lexer:
    """词法分析器"""
    
    TOKENS = [
        ("NUMBER", r"\d+"),
        ("STRING", r'"[^"]*"'),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("STAR", r"\*"),
        ("SLASH", r"/"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("EQ", r"="),
        ("SKIP", r"[ \t\n]+"),
    ]
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.tokens = []
    
    def tokenize(self) -> List[tuple]:
        """分词"""
        while self.pos < len(self.source):
            matched = False
            
            for token_type, pattern in self.TOKENS:
                import re
                match = re.match(pattern, self.source[self.pos:])
                if match:
                    if token_type != "SKIP":
                        self.tokens.append((token_type, match.group()))
                    self.pos += match.end()
                    matched = True
                    break
            
            if not matched:
                raise SyntaxError(f"无法识别的字符: {self.source[self.pos]}")
        
        return self.tokens


class Interpreter:
    """简单表达式解释器"""
    
    def __init__(self):
        self.variables: Dict[str, float] = {}
    
    def eval_expr(self, tokens: List[tuple]) -> float:
        """求值表达式"""
        import re
        
        # 简单实现：只处理加减乘除和数字
        expr = " ".join(t[1] for t in tokens if t[0] not in ("SKIP",))
        
        # 安全求值
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expr):
            return eval(expr)
        
        raise ValueError("表达式包含不允许的字符")


def run_bytecode(bytecode: List[tuple]):
    """快速运行字节码"""
    vm = SimpleVM()
    vm.load(bytecode)
    vm.run()
