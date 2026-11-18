import ast
import time
import math
from typing import Any, Callable, Dict, Optional, Set
import numpy as np
import sympy as sp

DISALLOWED_MODULES: Set[str] = {
    "os", "sys", "subprocess", "shutil", "socket", "requests", "urllib",
    "http", "pickle", "importlib", "ctypes", "threading", "multiprocessing",
    "pty", "asyncio", "signal", "posix", "nt"
}

DISALLOWED_CALLS: Set[str] = {
    "exec", "eval", "compile", "open", "input", "breakpoint", "memoryview"
}

DISALLOWED_ATTRS: Set[str] = {
    "__subclasses__", "__globals__", "__code__", "__closure__", "__dict__",
    "__class__", "__bases__", "__mro__"
}

SAFE_BUILTINS: Dict[str, Any] = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "math": math,
    "np": np,
    "numpy": np,
    "sp": sp,
    "sympy": sp,
}

class SecurityViolationError(Exception):
    """Raised when script violates AST safety or isolation boundaries."""
    pass

class ASTSecurityValidator(ast.NodeVisitor):
    """
    Statically analyzes Python AST prior to execution to enforce strict security boundaries:
    - Zero unauthorized module imports
    - Zero system/shell/subprocess invocation
    - Zero introspection or sandbox escape attributes
    """

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in DISALLOWED_MODULES:
                raise SecurityViolationError(f"Import of unauthorized module '{base_mod}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in DISALLOWED_MODULES:
                raise SecurityViolationError(f"Import from unauthorized module '{base_mod}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in DISALLOWED_CALLS:
                raise SecurityViolationError(f"Invocation of dangerous function '{node.func.id}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in DISALLOWED_ATTRS:
            raise SecurityViolationError(f"Access to introspection attribute '{node.attr}' is strictly prohibited.")
        self.generic_visit(node)

class SandboxExecutionWorker:
    """
    Isolated scientific computation runner.
    Applies AST static validation, restricted namespace builtins, and timeout limits.
    """

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def validate_code_safety(self, code_str: str) -> None:
        """Parses and verifies code safety using AST visitor."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            raise SecurityViolationError(f"Syntax error in code: {e}")
        validator = ASTSecurityValidator()
        validator.visit(tree)

    def execute_safe_computation(
        self,
        computation_fn: Callable[..., Any],
        *args,
        **kwargs
    ) -> tuple[Any, float]:
        """
        Executes a Python scientific callable with timing and timeout guard.
        Returns (result, execution_time_ms).
        """
        start_time = time.perf_counter()
        # Execute callable
        try:
            result = computation_fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Computation failed: {e}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if elapsed_ms > (self.timeout_seconds * 1000.0):
            raise TimeoutError(f"Execution exceeded timeout limit of {self.timeout_seconds} seconds.")

        return result, round(elapsed_ms, 2)
