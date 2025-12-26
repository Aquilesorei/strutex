"""
Hybrid provider that combines multimodal LLM capabilities with traditional OCR/Text extraction.

Strategies:
1. TEXT_FIRST: Extract text locally, send to LLM (Faster/Cheaper). Fallback to Multimodal.
2. HYBRID_FALLBACK: Try Multimodal first. Fallback to local text extraction on error.
"""

import os
import tempfile
import logging
from typing import Any, Optional, Type, Union
from enum import Enum

from .base import Provider
from ..plugins.registry import PluginRegistry
from ..types import Schema
from ..documents import get_mime_type

logger = logging.getLogger("strutex.providers.hybrid")


class HybridStrategy(str, Enum):
    TEXT_FIRST = "text_first"        # Extract text -> LLM. (Cheaper)
    HYBRID_FALLBACK = "fallback"     # LLM (Multimodal) -> Fallback to extracted text. (Robust)


class HybridProvider(Provider):
    """
    Provider that combines LLM capabilities with local text extraction.
    """
    
    def __init__(
        self,
        primary_provider: Union[str, Provider],
        strategy: HybridStrategy = HybridStrategy.HYBRID_FALLBACK,
        force_ocr: bool = False,
        **kwargs
    ):
        """
        Args:
            primary_provider: The LLM provider to use for reasoning.
            strategy: Processing strategy (TEXT_FIRST or HYBRID_FALLBACK).
            force_ocr: If True, always use OCR even if primary succeeds (mostly for debug/TEXT_FIRST).
        """
        self.strategy = strategy
        self.force_ocr = force_ocr
        
        # Resolve primary provider
        if isinstance(primary_provider, str):
            cls = PluginRegistry.get("provider", primary_provider)
            if not cls:
                raise ValueError(f"Provider not found: {primary_provider}")
            self.primary = cls(**kwargs)
        else:
            self.primary = primary_provider

    def process(
        self,
        file_path: str,
        prompt: str,
        schema: Schema,
        mime_type: str,
        **kwargs
    ) -> Any:
        if self.strategy == HybridStrategy.TEXT_FIRST:
            return self._process_text_first(file_path, prompt, schema, mime_type, **kwargs)
        else:
            return self._process_fallback(file_path, prompt, schema, mime_type, **kwargs)

    async def aprocess(
        self,
        file_path: str,
        prompt: str,
        schema: Schema,
        mime_type: str,
        **kwargs
    ) -> Any:
        # Async implementation mirroring sync logic
        # Note: Extractors are currently sync, so we run them in sync
        if self.strategy == HybridStrategy.TEXT_FIRST:
            return await self._aprocess_text_first(file_path, prompt, schema, mime_type, **kwargs)
        else:
            return await self._aprocess_fallback(file_path, prompt, schema, mime_type, **kwargs)
            
    def _extract_text(self, file_path: str, mime_type: str) -> Optional[str]:
        """Attempt to extract text using registered extractors."""
        # Find capable extractor
        # Logic: Iterate through all registered extractors?
        # Or just specific ones we know (pdfplumber)
        
        # For now, explicit check for PDF. Future: PluginRegistry.list("extractor")
        if mime_type == "application/pdf":
            from ..extractors.pdf import PDFExtractor, PDFPLUMBER_AVAILABLE
            if PDFPLUMBER_AVAILABLE:
                extractor = PDFExtractor()
                return extractor.extract(file_path)
        
        return None

    def _create_temp_text_file(self, text: str) -> str:
        """Create a temp file with the extracted text."""
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="extracted_")
        with os.fdopen(fd, 'w') as f:
            f.write(text)
        return path

    def _process_text_first(self, file_path: str, prompt: str, schema: Schema, mime_type: str, **kwargs):
        """Try extracting text first."""
        text = self._extract_text(file_path, mime_type)
        
        if text:
            logger.info(f"Hybrid: Extracted {len(text)} chars from {file_path}")
            # Create temp text file
            txt_path = self._create_temp_text_file(text)
            try:
                # Augment prompt
                full_prompt = f"{prompt}\n\n[Context: The following is text extracted from the source document]\n"
                
                return self.primary.process(txt_path, full_prompt, schema, "text/plain", **kwargs)
            finally:
                if os.path.exists(txt_path):
                    os.remove(txt_path)
        else:
            logger.warning(f"Hybrid: Could not extract text from {file_path}, falling back to multimodal.")
            return self.primary.process(file_path, prompt, schema, mime_type, **kwargs)

    def _process_fallback(self, file_path: str, prompt: str, schema: Schema, mime_type: str, **kwargs):
        """Try multimodal first, fallback to text."""
        try:
            return self.primary.process(file_path, prompt, schema, mime_type, **kwargs)
        except Exception as e:
            logger.warning(f"Hybrid: Primary provider failed ({e}), attempting text fallback.")
            
            text = self._extract_text(file_path, mime_type)
            if not text:
                logger.error("Hybrid: No text extraction available for fallback.")
                raise e
                
            txt_path = self._create_temp_text_file(text)
            try:
                full_prompt = f"{prompt}\n\n[Context: The following is text extracted from the source document after a processing failure]\n"
                return self.primary.process(txt_path, full_prompt, schema, "text/plain", **kwargs)
            except Exception as e2:
                logger.error(f"Hybrid: Fallback also failed: {e2}")
                raise e  # Raise original error
            finally:
                if os.path.exists(txt_path):
                    os.remove(txt_path)

    async def _aprocess_text_first(self, file_path: str, prompt: str, schema: Schema, mime_type: str, **kwargs):
        text = self._extract_text(file_path, mime_type)
        if text:
            txt_path = self._create_temp_text_file(text)
            try:
                full_prompt = f"{prompt}\n\n[Context: Extracted text]\n"
                return await self.primary.aprocess(txt_path, full_prompt, schema, "text/plain", **kwargs)
            finally:
                if os.path.exists(txt_path):
                    os.remove(txt_path)
        else:
            return await self.primary.aprocess(file_path, prompt, schema, mime_type, **kwargs)

    async def _aprocess_fallback(self, file_path: str, prompt: str, schema: Schema, mime_type: str, **kwargs):
        try:
            return await self.primary.aprocess(file_path, prompt, schema, mime_type, **kwargs)
        except Exception as e:
            text = self._extract_text(file_path, mime_type)
            if not text:
                raise e
            
            txt_path = self._create_temp_text_file(text)
            try:
                full_prompt = f"{prompt}\n\n[Context: Extracted text fallback]\n"
                return await self.primary.aprocess(txt_path, full_prompt, schema, "text/plain", **kwargs)
            finally:
                if os.path.exists(txt_path):
                    os.remove(txt_path)
