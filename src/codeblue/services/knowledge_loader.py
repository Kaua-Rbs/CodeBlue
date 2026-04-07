from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from codeblue.domain.knowledge_models import KnowledgeBundle
from codeblue.persistence.repositories.knowledge_repository import KnowledgeRepository

DEMO_KNOWLEDGE_PATH = (
    Path(__file__).resolve().parents[3] / "seed" / "knowledge" / "demo_bundle.json"
)


def load_knowledge_bundle(path: Path | None = None) -> KnowledgeBundle:
    bundle_path = path or DEMO_KNOWLEDGE_PATH
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    return KnowledgeBundle.model_validate(payload)


def ensure_demo_knowledge_bundle(session: Session) -> KnowledgeBundle:
    repository = KnowledgeRepository(session)
    bundle = repository.get_bundle("kb_codeblue_demo_v1")
    if bundle is not None:
        return bundle

    loaded_bundle = load_knowledge_bundle(DEMO_KNOWLEDGE_PATH)
    repository.replace_bundle(loaded_bundle)
    return loaded_bundle
