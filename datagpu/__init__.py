"""
DataGPU - Open-source data compiler for AI training datasets.

Compile datasets like code: clean, rank, and optimize in one command.
"""

__version__ = "0.1.0"

from datagpu.loader import load
from datagpu.compiler import DataCompiler

__all__ = ["load", "DataCompiler", "__version__"]
