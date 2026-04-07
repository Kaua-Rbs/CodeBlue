# Knowledge Schema Design

Status: current
Scope: rationale behind the knowledge schema and why its objects are separated the way they are
Last meaningful change: 2026-04-05

Purpose: preserve the reasoning behind the knowledge-schema design so future changes can extend it without losing the original architectural intent.

This note explains why the knowledge schema was designed the way it was for CodeBlue.

The schema has to solve two hard problems at once:

- represent clinical and outbreak logic in a way the system can execute; and
- keep that logic portable, reviewable, and replaceable across pathogens and hospitals.

Each part of the schema exists to protect one or both of those goals.

## `KnowledgeBundle`

Everything sits inside a top-level `KnowledgeBundle` because the system needs a deployable unit of knowledge.

Why:

- in practice, the system will not load isolated rules one by one;
- it must be possible to know exactly which pathogen pack, policy pack, actions, and tests were active at a given time; and
- the knowledge layer needs a portable, versioned boundary.

The bundle answers:

> What exact logic was the system using in this deployment, on this date?

Without a bundle, the system becomes a loose collection of rules with weak provenance.

## `SourceDocument`

`SourceDocument` exists because CodeBlue cannot treat guidance as anonymous truth.

Why:

- hospital policy, CDC guidance, WHO documents, and papers have different authority levels;
- recommendations change over time;
- some logic comes from prose, some from semi-structured sources, and some from local policy; and
- the system must know where each rule came from.

That is why the schema includes fields such as:

- organization
- publication date
- version
- jurisdiction
- machine readability
- ingestion mode

These make it possible to distinguish:

- authoritative national guidance
- local hospital adaptation
- evidence papers
- manually translated logic

This is essential for auditability and future updating.

## `PathogenPack`

`PathogenPack` is separate because pathogen-specific knowledge should not contaminate the reusable core.

Why:

- influenza, RSV, and other respiratory viruses share infrastructure but differ in timing, prevention, and action logic;
- the architectural promise of CodeBlue is that pathogens are swappable; and
- if pathogen rules are scattered across the system, modularity collapses.

The pack is a container for disease-specific logic, not just metadata.

It lets the system say:

- load influenza
- load RSV
- compare these two versions

That is much cleaner than hard-coding disease assumptions in services.

## `PathogenParameter`

`PathogenParameter` exists because some pathogen facts are best represented as structured parameters rather than full rules.

Examples:

- incubation period
- infectious period
- shedding duration
- hospital-onset threshold
- transmission mode

These are not decisions by themselves. They are inputs to later reasoning.

If represented as parameters:

- they can be reused across many rules;
- they can carry uncertainty; and
- they can be updated without rewriting the full logic tree.

That is better than burying values like `1-4 days` inside rule conditions.

## `CaseDefinitionRule`

`CaseDefinitionRule` is separate because classification is one of the first things the system must do.

Examples:

- hospital-onset influenza
- suspected RSV exposure
- possible cluster-related case

These labels are not merely descriptive. They drive downstream behavior:

- risk scoring
- escalation
- action routing
- audit interpretation

By isolating case-definition rules, the system makes disease classification explicit and inspectable.

## `TransmissionRule`

`TransmissionRule` is separate because transmission logic is one of the core differentiators of CodeBlue.

Why:

- overlap in time and space
- same room
- same unit
- adjacency
- infectious window
- exposed staff or patients

These are mechanisms of hospital spread interpretation, not the same thing as case definition or treatment guidance.

This deserved its own rule family because:

- it is central to the platform;
- it depends heavily on the temporal hospital-state layer; and
- it is likely to grow much richer over time.

Keeping it distinct prevents it from being buried inside generic policy logic.

## `InterventionAssumption`

`InterventionAssumption` is one of the most important objects in the schema.

It exists because intervention knowledge is rarely absolute truth. It is usually:

- evidence-backed
- context-dependent
- policy-limited
- uncertain

Examples:

- isolation reduces spread
- single rooms are preferable in some contexts
- oseltamivir prophylaxis may be beneficial in certain scenarios
- RSV immunization matters only for eligible populations

If modeled as assumptions rather than hard rules:

- uncertainty is preserved;
- provenance is preserved;
- local policy can override or constrain them; and
- the system does not pretend that every intervention is universally valid.

This directly supports the need to carry:

- source
- confidence
- uncertainty
- local approval context
- versioning

## `PolicyPack`

`PolicyPack` is separate from `PathogenPack` because medical truth and local operational permission are not the same thing.

Why:

- a pathogen pack says what is biologically or clinically relevant;
- a policy pack says what the local hospital allows, requires, or forbids.

For example:

- influenza logic may suggest prophylaxis review;
- but hospital policy may require pharmacy approval; or
- it may forbid autonomous medication-related actions entirely.

If policy is not isolated, the system cannot adapt cleanly between hospitals.

## `PolicyConstraintRule`

`PolicyConstraintRule` exists because some policies do not generate actions, they limit the action space.

Examples:

- no autonomous medication ordering
- all medication actions are review-only
- certain alerts must route only to IPC
- some actions are forbidden in pediatrics

These are boundaries, not recommendations.

That is why they should not live in the same object as action-generation logic. Their job is not to say what to do, but what the system is allowed to surface.

This supports the principle:

> AI estimates and prioritizes; policy/governance constrains and routes.

## `EscalationRule`

`EscalationRule` exists because escalation is a distinct operational function.

The system needs to know:

- when to notify IPC
- when to route to pharmacy
- when to alert stewardship
- when to elevate urgency for vulnerable wards

This is not the same as classification, risk scoring, or action definition.

It depends on:

- severity
- vulnerable unit context
- outbreak clustering
- organizational structure

That deserved its own schema component.

## `OverridePolicy`

`OverridePolicy` exists because human override is not an exception to CodeBlue. It is a design requirement.

Why:

- the system must support human rejection, deferral, escalation, and override;
- that behavior must be governed, not improvised; and
- overrides must be accountable.

By formalizing override policy, the system becomes safer and more defensible.

This aligns directly with the need for:

- audit trail
- override
- rejection
- escalation logging

Without a defined override structure, human review becomes informal and hard to audit.

## `ReviewWorkflowPack`

`ReviewWorkflowPack` exists because the system must know not only what action is relevant, but how it moves through human review.

Why:

- a risk output is not yet an operational action;
- even a proposed action is not yet routed; and
- different action families go to different teams.

Examples:

- isolation review -> IPC
- antiviral review -> clinician or pharmacy
- stewardship review -> stewardship team or attending team

This layer converts:

- classifications
- risk outputs
- policy-constrained options

into:

- routed, reviewable work items

This prevents the system from acting like a raw alert generator with no operational pathway.

## `ReviewRule`

`ReviewRule` exists because the system needs explicit logic for:

> Under what conditions should this reviewable action be created?

Why:

- not every risk signal should create work;
- not every classification should route the same way; and
- actions need conditions, urgency, and reviewer roles.

This rule type is the bridge between reasoning and workflow.

## `ActionDefinition`

`ActionDefinition` is a controlled catalog because actions should be standardized objects, not free-form text.

Why:

- free-text recommendations are hard to validate;
- hard to audit;
- hard to compare across sites; and
- hard to route consistently.

A controlled action catalog gives:

- stable identifiers
- categories
- execution mode
- required reviewer role
- logging requirements

That is critical for governance and UI consistency.

It also makes metrics easier:

- how many times was `review_isolation_placement` triggered?
- how often was `review_antibiotic_necessity` rejected?

You cannot do that well with unstructured output.

## `EvidenceStatement`

`EvidenceStatement` exists because evidence should be reusable and referenceable across multiple rules and assumptions.

Why:

- the same paper may support a transmission rule and an intervention assumption;
- multiple rules may depend on the same finding; and
- the system should make it visible which evidence is influencing behavior.

This avoids duplicating evidence logic inside each rule.

It also helps when evidence changes:

- update the evidence layer;
- identify affected rules; and
- review them systematically.

## `TerminologyBinding`

`TerminologyBinding` is essential for real deployment because every hospital names things differently.

Why:

- one hospital may say `DBL`
- another may say `Double`
- another may say `Shared-2`
- but CodeBlue needs one canonical meaning such as `double_room`

The same applies to:

- wards
- lab codes
- room categories
- patient classes
- medication classes

Without terminology bindings, the ingestion layer becomes brittle and non-portable.

This object is the bridge between:

- local hospital vocabulary; and
- the canonical internal schema.

## Rule Condition DSL

A small structured condition language is preferable to free text because the rules must be:

- machine-evaluable
- testable
- inspectable
- portable

Why:

- prose is too ambiguous;
- arbitrary Python code is too opaque and hard to govern; and
- a constrained DSL is easier to validate while still being expressive enough for useful logic.

That is why the condition language uses:

- `all`
- `any`
- typed `fact`
- typed `op`
- typed `value`

This keeps the rule engine understandable by humans and forces the system to refer back to canonical facts produced by the event/state layer.

## `RuleAuditRecord`

`RuleAuditRecord` exists because the translation from source guidance into executable rules is itself a governed act.

Why:

- someone had to interpret the guideline;
- that interpretation may be imperfect; and
- clinical and legal defensibility requires knowing who translated and who approved it.

This object answers:

- who created the rule?
- from which source?
- when?
- who approved it?

That becomes especially important when the source was prose and had to be manually structured.

## `DecisionAuditRecord`

`DecisionAuditRecord` exists because the system must audit not only rules, but runtime outputs.

Why:

- what action was proposed?
- which rules triggered it?
- which bundle versions were active?
- what was the review status?

This is fundamental if CodeBlue is ever going to be trusted in operational settings.

It supports:

- post hoc analysis
- debugging
- governance
- quality improvement
- regulatory defensibility

## `KnowledgeTestCase`

`KnowledgeTestCase` exists because structured knowledge without tests becomes unsafe very quickly.

Why:

- changing one rule can silently break others;
- policy logic can produce unexpected actions; and
- synthetic scenarios with expected outputs are necessary.

This follows the logic of structured clinical decision support systems where executable logic is accompanied by test cases.

For CodeBlue, this is especially important because:

- the system encodes real operational consequences;
- regression testing is needed across pack versions; and
- local hospital adaptations should be testable before deployment.

## Why The Schema Is Split Into Packs, Rules, Actions, Evidence, And Audit

This separation was deliberate.

If everything is collapsed together, the distinction is lost between:

- what is biologically true,
- what is supported by evidence,
- what is permitted locally,
- what should be reviewed operationally, and
- what actually happened at runtime.

CodeBlue needs all five.

That is why the schema preserves these major architectural boundaries:

- `PathogenPack` -> disease-specific knowledge
- `PolicyPack` -> local constraints
- `ReviewWorkflowPack` -> routing and review process
- `ActionDefinition` catalog -> standardized surfaced actions
- evidence layer -> provenance and confidence
- audit layer -> traceability and accountability

That separation is what makes the system both modular and governable.

## Why Rules Should Be Stored As Data And Validated In Python

Rules should be stored as data rather than only code because:

- policies change;
- pathogen knowledge changes;
- different hospitals need different packs; and
- non-core contributors may need to edit logic later.

If rules exist only in Python code:

- updates become developer-dependent;
- review is harder;
- portability is worse; and
- version comparison is harder.

If rules are stored as structured data:

- Pydantic can validate them;
- PostgreSQL can store them;
- the rule engine can execute them;
- future tooling can edit them; and
- separation between engine and knowledge content is preserved.

That is a major architectural advantage.

## Overall Schema Principle

The schema is built around one central principle:

**CodeBlue should not ingest guidance as documents and then improvise. It should ingest guidance into typed, versioned, testable knowledge objects that can interact safely with the canonical hospital event/state model.**

A shorter summary is:

- `KnowledgeBundle` -> deployment unit
- `SourceDocument` -> provenance
- `PathogenPack` -> disease modularity
- `PathogenParameter` -> reusable temporal and biological facts
- `CaseDefinitionRule` -> classification logic
- `TransmissionRule` -> spread logic
- `InterventionAssumption` -> evidence-backed but uncertain action knowledge
- `PolicyPack` -> hospital-specific constraints
- `PolicyConstraintRule` -> action boundaries
- `EscalationRule` -> notification and routing
- `OverridePolicy` -> human authority
- `ReviewWorkflowPack` and `ReviewRule` -> review pipeline
- `ActionDefinition` -> controlled operational outputs
- `EvidenceStatement` -> reusable evidence backbone
- `TerminologyBinding` -> local-to-canonical mapping
- condition DSL -> safe computable logic
- audit records -> accountability
- test cases -> validation
