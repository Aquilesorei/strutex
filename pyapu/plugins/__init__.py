"""
Plugin system for pyapu extensibility.

Provides the PluginRegistry for registering and discovering plugins,
the @register decorator for easy plugin registration, and base classes
for all plugin types.
"""

from .registry import PluginRegistry, register
from .base import (
    Provider,
    Extractor,
    Validator,
    ValidationResult,
    Postprocessor,
    SecurityPlugin,
    SecurityResult
)

__all__ = [
    "PluginRegistry",
    "register",
    "Provider",
    "Extractor",
    "Validator",
    "ValidationResult",
    "Postprocessor",
    "SecurityPlugin",
    "SecurityResult"
]
