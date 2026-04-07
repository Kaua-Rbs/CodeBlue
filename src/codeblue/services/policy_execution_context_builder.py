from __future__ import annotations

from codeblue.domain.canonical_events import EventEnvelope
from codeblue.domain.knowledge_runtime_models import CompiledKnowledgePackage, PolicyExecutionContext
from codeblue.domain.state_models import StateSnapshotRef
from codeblue.services.deployment_profile_service import DeploymentProfileService
from codeblue.services.runtime_facts_builder import RuntimeFactsBuilder


class CompiledPolicyExecutionContextBuilder:
    def __init__(self, compiled_package: CompiledKnowledgePackage) -> None:
        self.compiled_package = compiled_package
        self.deployment_profile_service = DeploymentProfileService()
        self.runtime_facts_builder = RuntimeFactsBuilder()

    def build(
        self,
        events: list[EventEnvelope],
        snapshot: StateSnapshotRef,
    ) -> PolicyExecutionContext:
        deployment_profile = self.deployment_profile_service.select_profile(
            self.compiled_package.deployment_profiles,
            snapshot.hospital_id,
        )
        runtime_facts = self.runtime_facts_builder.build(events, snapshot, deployment_profile)
        return PolicyExecutionContext(
            runtime_mode="compiled",
            events=events,
            snapshot=snapshot,
            hospital_id=snapshot.hospital_id,
            compiled_package=self.compiled_package,
            deployment_profile=deployment_profile,
            runtime_facts=runtime_facts,
        )
