from __future__ import annotations
import gc
import os
import time
from pathlib import Path
from typing import Any
from research_agent.utils.config import settings

MARKER_CONFIG = {
    "output_format": "markdown",
    "use_llm": True,
    "llm_service": "marker.services.openai.OpenAIService",
    "openai_base_url": settings.OPENAI_BASE_URL,
    "openai_model": settings.OPENAI_MODEL_NAME,
    "openai_api_key": settings.OPENAI_API_KEY,
    "disable_ocr": True,
    "disable_image_extraction": True,
}

# Lazy imports — heavy, only load when PDF is parsed
_PdfConverter = None
_ConfigParser = None
_create_model_dict = None
_text_from_rendered = None


def _lazy_imports():
    global _PdfConverter, _ConfigParser, _create_model_dict, _text_from_rendered
    if _PdfConverter is None:
        from marker.converters.pdf import PdfConverter
        from marker.config.parser import ConfigParser
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        _PdfConverter = PdfConverter
        _ConfigParser = ConfigParser
        _create_model_dict = create_model_dict
        _text_from_rendered = text_from_rendered
        # logger.info("marker-pdf 2.0.0 loaded")


_CACHED_CONVERTER: Any = None


def _get_converter() -> Any:
    """Build (and cache) the PdfConverter with LLM service config."""
    global _CACHED_CONVERTER
    if _CACHED_CONVERTER is None:
        _lazy_imports()
        config_parser = _ConfigParser(MARKER_CONFIG)
        model_dict = _create_model_dict()
        llm_service = config_parser.get_llm_service()

        _probe = _PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=model_dict,
            llm_service=llm_service,
        )
        all_processors = _probe.processor_list

        filtered_processor_strings = [
            f"{p.__class__.__module__}.{p.__class__.__name__}"
            for p in all_processors
            if "llm" not in p.__class__.__module__.lower()
            or "table" in p.__class__.__name__.lower()
        ]

        _CACHED_CONVERTER = _PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=model_dict,
            processor_list=filtered_processor_strings,
            renderer=config_parser.get_renderer(),
            llm_service=llm_service,
        )
        # logger.info(f"[marker-pdf] Converter initialized with LLM service: {settings.OPENAI_BASE_URL}/{settings.LLM_MODEL}")
    return _CACHED_CONVERTER


def parse_pdf_to_markdown(file_bytes: bytes) -> str:
    """Parse a PDF via marker-pdf 2.0.0 → markdown text."""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        converter = _get_converter()
        t0 = time.time()
        rendered = converter(str(tmp_path))
        text, _, _ = _text_from_rendered(rendered)
        elapsed = time.time() - t0
        # logger.info(
        #     f"marker-pdf parsed {len(file_bytes)} bytes in {elapsed:.2f}s "
        #     f"→ {len(text)} chars"
        # )
        return str(text)
    finally:
        gc.collect()
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
