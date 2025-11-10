"""Dataset loader for PyTorch and Hugging Face integration."""

from pathlib import Path
from typing import Union, Optional, Dict, Any

import polars as pl

from datagpu.utils import load_yaml


class CompiledDataset:
    """Wrapper for compiled datasets compatible with PyTorch DataLoader."""
    
    def __init__(self, data: pl.DataFrame, manifest: Dict[str, Any]):
        self.data = data
        self.manifest = manifest
        self._index = 0
    
    def __len__(self) -> int:
        """Return dataset length."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get item by index."""
        if isinstance(idx, int):
            row = self.data[idx]
            return {col: row[col][0] for col in self.data.columns}
        elif isinstance(idx, slice):
            rows = self.data[idx]
            return rows.to_dicts()
        else:
            raise TypeError(f"Invalid index type: {type(idx)}")
    
    def __iter__(self):
        """Iterate over dataset."""
        self._index = 0
        return self
    
    def __next__(self) -> Dict[str, Any]:
        """Get next item."""
        if self._index >= len(self.data):
            raise StopIteration
        item = self[self._index]
        self._index += 1
        return item
    
    def to_pandas(self):
        """Convert to pandas DataFrame."""
        return self.data.to_pandas()
    
    def to_arrow(self):
        """Convert to PyArrow Table."""
        return self.data.to_arrow()
    
    def to_dict(self) -> list:
        """Convert to list of dictionaries."""
        return self.data.to_dicts()


def load(manifest_path: Union[str, Path]) -> CompiledDataset:
    """
    Load a compiled dataset from manifest.
    
    Args:
        manifest_path: Path to manifest.yaml file
    
    Returns:
        CompiledDataset instance compatible with PyTorch DataLoader
    
    Example:
        >>> from datagpu import load
        >>> dataset = load("compiled/manifest.yaml")
        >>> print(len(dataset))
        >>> for item in dataset:
        ...     print(item)
    """
    manifest_path = Path(manifest_path)
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    
    # Load manifest
    manifest = load_yaml(manifest_path)
    
    # Load compiled data
    compiled_path = Path(manifest["compiled_path"])
    if not compiled_path.exists():
        raise FileNotFoundError(f"Compiled dataset not found: {compiled_path}")
    
    data = pl.read_parquet(compiled_path)
    
    return CompiledDataset(data, manifest)


def load_to_hf(manifest_path: Union[str, Path]):
    """
    Load compiled dataset as Hugging Face Dataset.
    
    Requires: pip install datasets
    
    Args:
        manifest_path: Path to manifest.yaml file
    
    Returns:
        Hugging Face Dataset instance
    """
    try:
        from datasets import Dataset
    except ImportError:
        raise ImportError(
            "Hugging Face datasets not installed. "
            "Install with: pip install datasets"
        )
    
    compiled_dataset = load(manifest_path)
    arrow_table = compiled_dataset.to_arrow()
    
    return Dataset(arrow_table)


def load_to_pytorch(manifest_path: Union[str, Path], batch_size: int = 32, shuffle: bool = True):
    """
    Load compiled dataset as PyTorch DataLoader.
    
    Requires: pip install torch
    
    Args:
        manifest_path: Path to manifest.yaml file
        batch_size: Batch size for DataLoader
        shuffle: Whether to shuffle data
    
    Returns:
        PyTorch DataLoader instance
    """
    try:
        from torch.utils.data import DataLoader
    except ImportError:
        raise ImportError(
            "PyTorch not installed. "
            "Install with: pip install torch"
        )
    
    dataset = load(manifest_path)
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle
    )
