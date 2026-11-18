import pytest
from axion.hypothesis_tester.sandbox import (
    ASTSecurityValidator,
    SandboxExecutionWorker,
    SecurityViolationError,
)

def test_ast_validator_blocks_unauthorized_imports():
    worker = SandboxExecutionWorker()

    malicious_scripts = [
        "import os\nos.system('dir')",
        "import subprocess\nsubprocess.run(['ls'])",
        "import socket\ns = socket.socket()",
        "import shutil\nshutil.rmtree('/')",
        "from os import path",
        "import urllib.request",
        "import pickle",
    ]

    for script in malicious_scripts:
        with pytest.raises(SecurityViolationError):
            worker.validate_code_safety(script)

def test_ast_validator_blocks_dangerous_calls_and_dunders():
    worker = SandboxExecutionWorker()

    dangerous_scripts = [
        "eval('1 + 1')",
        "exec('print(1)')",
        "open('secret.txt', 'r')",
        "().__class__.__subclasses__()",
        "def f(): pass\nf.__globals__",
    ]

    for script in dangerous_scripts:
        with pytest.raises(SecurityViolationError):
            worker.validate_code_safety(script)

def test_ast_validator_allows_scientific_imports():
    worker = SandboxExecutionWorker()

    safe_script = """
import math
import numpy as np
import sympy as sp

x = np.linspace(0, 10, 100)
y = np.sin(x)
val = math.sqrt(16.0)
"""
    # Should not raise
    worker.validate_code_safety(safe_script)

def test_sandbox_timeout_guard():
    # Worker with 0.1s timeout
    worker = SandboxExecutionWorker(timeout_seconds=0.1)

    def slow_task():
        import time
        time.sleep(0.3)
        return "done"

    with pytest.raises(TimeoutError):
        worker.execute_safe_computation(slow_task)
