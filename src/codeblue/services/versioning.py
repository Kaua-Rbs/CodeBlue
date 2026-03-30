from __future__ import annotations

from codeblue.domain.audit_models import VersionRef
from codeblue.packs.pathogen.base import PathogenPack
from codeblue.packs.policy.base import PolicyPack


def build_version_ref(
    schema_version: str,
    pathogen_pack: PathogenPack,
    policy_pack: PolicyPack,
    scoring_version: str,
) -> VersionRef:
    return VersionRef(
        schema_version=schema_version,
        pathogen_pack_version=pathogen_pack.version,
        policy_pack_version=policy_pack.version,
        scoring_version=scoring_version,
    )
