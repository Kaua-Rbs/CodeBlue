export type ReviewDecisionType = "approve" | "reject" | "override" | "escalate";
export type ActionStatus =
  | "pending_review"
  | "approved"
  | "rejected"
  | "overridden"
  | "escalated";
export type RiskPriority = "low" | "medium" | "high" | "critical";
export type EntityScope = "patient" | "room" | "ward" | "staff_bridge" | "hospital";
export type TargetScope =
  | "patient"
  | "room"
  | "ward"
  | "staff"
  | "pharmacy"
  | "ipc_team"
  | "hospital"
  | "entry_point";

export interface HealthResponse {
  status: string;
  app: string;
  env: string;
}

export interface RunResponse {
  snapshot_at: string;
  assessment_count: number;
  alert_count: number;
  action_count: number;
  runtime_mode: string;
  knowledge_bundle_id: string | null;
  deployment_profile_id: string | null;
  matched_trigger_count: number;
}

export interface TimeWindow {
  start: string;
  end: string;
}

export interface RiskSignal {
  name: string;
  value: number;
  weight: number;
  evidence_event_ids: string[];
  explanation: string;
}

export interface RiskAssessment {
  assessment_id: string;
  entity_scope: EntityScope;
  target_id: string;
  time_window: TimeWindow;
  score: number;
  priority: RiskPriority;
  contributing_signals: RiskSignal[];
  generated_by: string;
  pathogen_pack_version: string;
  policy_pack_version: string;
  knowledge_bundle_id: string | null;
  triggering_rule_ids: string[];
  context_facts: Record<string, unknown>;
}

export interface PriorityAlert {
  alert_id: string;
  assessment_id: string;
  target_id: string;
  priority: RiskPriority;
  summary: string;
  top_signals: string[];
}

export interface ProposedAction {
  action_id: string;
  risk_assessment_id: string | null;
  action_definition_id: string | null;
  action_type: string;
  category: string | null;
  priority: RiskPriority | null;
  execution_mode: string;
  target_scope: TargetScope;
  target_id: string;
  rationale: string;
  required_reviewer_role: string;
  status: ActionStatus;
  constraints_applied: string[];
  knowledge_bundle_id: string | null;
  triggering_rule_ids: string[];
  audit_ref: string;
  created_at: string;
}

export interface ReviewDecision {
  decision_id: string;
  action_id: string;
  reviewer_role: string;
  decision: ReviewDecisionType;
  rationale: string;
  decided_at: string;
  audit_ref: string;
}

export interface ReviewActionRequest {
  reviewer_role: string;
  decision: ReviewDecisionType;
  rationale: string;
}

export interface PatientState {
  patient_id: string;
  room_id: string;
  ward_id: string;
  start_at: string;
  end_at: string | null;
}

export interface StaffState {
  staff_id: string;
  ward_id: string;
  role: string;
  room_id: string | null;
  start_at: string;
  end_at: string | null;
}

export interface RoomState {
  room_id: string;
  ward_id: string;
  active_patients: string[];
  active_staff: string[];
}

export interface WardState {
  ward_id: string;
  room_ids: string[];
  active_patients: string[];
  active_staff: string[];
}

export interface StateSnapshotRef {
  hospital_id: string;
  at: string;
  time_window: TimeWindow;
  patient_states: PatientState[];
  staff_states: StaffState[];
  room_states: RoomState[];
  ward_states: WardState[];
  source_event_ids: string[];
}

export interface ExplainabilityResponse {
  action_id: string;
  explanation: string;
  assessment_id: string | null;
  trace: Record<string, unknown> | null;
}

export interface EventEnvelope {
  event_id?: string;
  event_type: string;
  occurred_at: string;
  recorded_at: string;
  source_system: string;
  hospital_id: string;
  payload: Record<string, unknown>;
  schema_version?: string;
}

export interface IngestEventsResponse {
  ingested_count: number;
  event_ids: string[];
}
