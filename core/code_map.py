"""
# --- DNK-MRH-HEADER ---
# mrh_id: "core/code_map.py"
# purpose: "Native Python AST Symbol Indexer for zero-waste token-efficient file inspection."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-25"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
"""

import ast
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class SymbolInfo:
    name: str
    kind: str  # "class", "function", "async_function", "method"
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    parent_class: Optional[str] = None


@dataclass
class CodeMapResult:
    file_path: str
    total_lines: int
    symbols: List[SymbolInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def get_symbol_by_name(self, name: str) -> Optional[SymbolInfo]:
        for sym in self.symbols:
            if sym.name == name:
                return sym
        return None

    def to_compact_summary(self) -> str:
        """Generates a token-efficient compact map of the file structure."""
        if self.error:
            return f"Error in {self.file_path}: {self.error}"

        lines = [f"# CodeMap: {self.file_path} ({self.total_lines} lines)"]
        if self.imports:
            lines.append(f"Imports: {len(self.imports)} statement(s)")

        for sym in self.symbols:
            indent = "  " if sym.parent_class else ""
            params_str = ", ".join(sym.parameters)
            dec_str = f" [@{', @'.join(sym.decorators)}]" if sym.decorators else ""
            lines.append(
                f"{indent}- [{sym.kind}] {sym.name}({params_str}) -> L{sym.start_line}-L{sym.end_line}{dec_str}"
            )

        return "\n".join(lines)


def _get_decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_get_decorator_name(node.value)}.{node.attr}"
    elif isinstance(node, ast.Call):
        return _get_decorator_name(node.func)
    return "decorator"


def _extract_parameters(args_node: ast.arguments) -> List[str]:
    params = []
    for arg in args_node.args:
        ann = ""
        if arg.annotation:
            ann = f": {ast.unparse(arg.annotation)}"
        params.append(f"{arg.arg}{ann}")
    return params


class ASTSymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.symbols: List[SymbolInfo] = []
        self.imports: List[str] = []
        self.current_class: Optional[str] = None

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        doc = ast.get_docstring(node)
        decorators = [_get_decorator_name(d) for d in node.decorator_list]
        self.symbols.append(
            SymbolInfo(
                name=node.name,
                kind="class",
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=doc.split("\n")[0] if doc else None,
                decorators=decorators,
                parent_class=None,
            )
        )
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._record_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._record_function(node, is_async=True)

    def _record_function(self, node: Any, is_async: bool):
        doc = ast.get_docstring(node)
        decorators = [_get_decorator_name(d) for d in node.decorator_list]
        params = _extract_parameters(node.args)

        if self.current_class:
            kind = "async_method" if is_async else "method"
        else:
            kind = "async_function" if is_async else "function"

        self.symbols.append(
            SymbolInfo(
                name=node.name,
                kind=kind,
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=doc.split("\n")[0] if doc else None,
                parameters=params,
                decorators=decorators,
                parent_class=self.current_class,
            )
        )
        # Avoid traversing nested functions for top-level code maps
        # unless necessary, but generic_visit is fine:
        self.generic_visit(node)


def generate_code_map(source_code: str, file_path: str = "in_memory.py") -> CodeMapResult:
    """
    Parses Python source code into an AST and extracts top-level symbols,
    classes, functions, methods, and line ranges.
    """
    total_lines = len(source_code.splitlines())
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        return CodeMapResult(
            file_path=file_path,
            total_lines=total_lines,
            error=f"SyntaxError: {e.msg} at line {e.lineno}",
        )

    visitor = ASTSymbolVisitor(file_path=file_path)
    visitor.visit(tree)

    return CodeMapResult(
        file_path=file_path,
        total_lines=total_lines,
        symbols=visitor.symbols,
        imports=visitor.imports,
    )


def generate_code_map_from_file(file_path: str) -> CodeMapResult:
    """Reads a Python file from disk and parses its AST symbol map."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return generate_code_map(content, file_path=file_path)
    except Exception as e:
        return CodeMapResult(file_path=file_path, total_lines=0, error=str(e))
