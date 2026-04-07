from __future__ import annotations

from pathlib import Path

from codeblue.domain.knowledge_runtime_models import CompiledKnowledgePackage
from codeblue.services.knowledge_source_compiler import compile_workbook_source_package

WORKBOOK_DIRECTORY = Path(__file__).resolve().parents[3] / "workbook"

_CACHED_SIGNATURE: tuple[tuple[str, int, int], ...] | None = None
_CACHED_PACKAGE: CompiledKnowledgePackage | None = None


def _directory_signature(path: Path) -> tuple[tuple[str, int, int], ...]:
    files = [item for item in path.iterdir() if item.is_file()]
    return tuple(
        sorted(
            (
                file_path.name,
                file_path.stat().st_mtime_ns,
                file_path.stat().st_size,
            )
            for file_path in files
        )
    )


def load_compiled_runtime_package_cached(
    path: Path | None = None,
) -> CompiledKnowledgePackage:
    global _CACHED_PACKAGE, _CACHED_SIGNATURE

    source_path = path or WORKBOOK_DIRECTORY
    signature = _directory_signature(source_path)
    if _CACHED_PACKAGE is None or _CACHED_SIGNATURE != signature:
        _CACHED_PACKAGE = compile_workbook_source_package(source_path)
        _CACHED_SIGNATURE = signature
    return _CACHED_PACKAGE
