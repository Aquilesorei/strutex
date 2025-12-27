"""
Unstructured.io fallback integration for Strutex.

Provides a hybrid processor that falls back to traditional OCR/partitioning
when LLM-based extraction fails.

Note: This integration is marked as EXPERIMENTAL. The Unstructured library
evolves rapidly and API compatibility is not guaranteed.
"""
import logging
from typing import Any, Dict, Optional, Union

try:
    from unstructured.partition.auto import partition  # type: ignore
except ImportError:
    partition = None

from strutex.processor import DocumentProcessor
from strutex.plugins.base import Provider
from strutex.types import Schema

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when extraction fails and fallback is not used."""
    pass


class UnstructuredFallbackProcessor:
    """
    A wrapper around DocumentProcessor that falls back to Unstructured.io
    if the primary AI extraction fails.

    **EXPERIMENTAL**: This integration is experimental and may change.
    
    Behavior options:
    - `on_fallback="raise"` (default): Raise ExtractionError on failure
    - `on_fallback="empty"`: Return empty dict matching schema structure
    - `on_fallback="partial"`: Return partial data with _fallback fields
    
    Example:
        processor = UnstructuredFallbackProcessor(
            schema=InvoiceSchema,
            on_fallback="raise"  # Fail loudly, don't return inconsistent data
        )
        
        try:
            result = processor.process("doc.pdf")
        except ExtractionError as e:
            # Handle failure explicitly
            pass
    """

    def __init__(
            self,
            schema: Optional[Schema] = None,
            provider: Union[str, Provider] = "gemini",
            api_key: Optional[str] = None,
            config: Optional[Dict[str, Any]] = None,
            on_fallback: str = "raise"  # "raise", "empty", or "partial"
    ):
        """
        Initialize the fallback processor.
        
        Args:
            schema: Target extraction schema
            provider: LLM provider name or instance
            api_key: API key for provider
            config: Additional processor config
            on_fallback: Behavior when extraction fails:
                - "raise": Raise ExtractionError (recommended, consistent)
                - "empty": Return empty dict with schema structure
                - "partial": Return partial data with fallback metadata
        """
        if on_fallback not in ("raise", "empty", "partial"):
            raise ValueError(f"on_fallback must be 'raise', 'empty', or 'partial', got '{on_fallback}'")
        
        self.processor = DocumentProcessor(
            provider=provider,
            api_key=api_key,
            **(config or {})
        )
        self.schema = schema
        self.on_fallback = on_fallback

        if partition is None:
            logger.warning(
                "Unstructured is not installed. Fallback will not work. "
                "Install with: pip install unstructured"
            )

    def process(
        self, 
        file_path: str, 
        schema: Optional[Schema] = None, 
        prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Attempt extraction with Strutex. If it fails, behavior depends on on_fallback.

        Args:
            file_path: Path to document
            schema: Override schema for this request
            prompt: Extraction prompt
            
        Returns:
            Extracted data as dict (consistent shape based on schema)
            
        Raises:
            ExtractionError: If on_fallback="raise" and extraction fails
        """
        target_schema = schema or self.schema

        try:
            # 1. Try Strutex (Primary)
            result = self.processor.process(
                file_path=file_path,
                schema=target_schema,
                prompt=prompt
            )
            # Ensure consistent dict return
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            return result

        except Exception as e:
            logger.error(f"Strutex extraction failed: {e}")
            
            if self.on_fallback == "raise":
                raise ExtractionError(
                    f"Extraction failed for {file_path}: {e}"
                ) from e
            
            elif self.on_fallback == "empty":
                # Return empty dict matching schema structure
                return self._get_empty_schema(target_schema)
            
            elif self.on_fallback == "partial":
                # Try to get raw text, return with fallback metadata
                raw_text = self._extract_raw_text(file_path)
                empty = self._get_empty_schema(target_schema)
                empty["_fallback"] = True
                empty["_error"] = str(e)
                empty["_raw_text"] = raw_text
                return empty
            
            # Should never reach here
            raise ExtractionError(f"Extraction failed: {e}") from e

    def _get_empty_schema(self, schema: Optional[Schema]) -> Dict[str, Any]:
        """Generate empty dict matching schema structure."""
        if schema is None:
            return {}
        
        # Pydantic model
        if hasattr(schema, 'model_fields'):
            return {field: None for field in schema.model_fields.keys()}
        
        # Strutex schema with to_dict
        if hasattr(schema, 'to_dict'):
            schema_dict = schema.to_dict()
            if 'properties' in schema_dict:
                return {prop: None for prop in schema_dict['properties'].keys()}
        
        return {}

    def _extract_raw_text(self, file_path: str) -> str:
        """Extract raw text using Unstructured if available."""
        if partition is None:
            return ""
        
        try:
            elements = partition(filename=file_path)
            return "\n\n".join([str(el) for el in elements])
        except Exception as e:
            logger.warning(f"Unstructured fallback also failed: {e}")
            return ""