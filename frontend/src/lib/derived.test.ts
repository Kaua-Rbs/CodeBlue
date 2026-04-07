import { describe, expect, it } from "vitest";
import { buildWardSummaries, deriveActionPriority, enrichActions } from "./derived";
import type { PriorityAlert, ProposedAction, RiskAssessment, StateSnapshotRef } from "../types/api";

describe("derived helpers", () => {
  it("derives action priority from linked assessment", () => {
    const action: ProposedAction = {
      action_id: "action-1",
      risk_assessment_id: "assessment-1",
      action_definition_id: "review_isolation",
      action_type: "review_isolation_placement",
      category: "infection_control",
      priority: null,
      execution_mode: "review_only",
      target_scope: "patient",
      target_id: "patient-1",
      rationale: "Test rationale",
      required_reviewer_role: "ipc_lead",
      status: "pending_review",
      constraints_applied: [],
      knowledge_bundle_id: "kb_demo",
      triggering_rule_ids: ["rule-1"],
      audit_ref: "audit-1",
      created_at: "2026-04-07T10:00:00Z",
    };

    const assessment: RiskAssessment = {
      assessment_id: "assessment-1",
      entity_scope: "ward",
      target_id: "ward-a",
      time_window: {
        start: "2026-04-07T09:00:00Z",
        end: "2026-04-07T10:00:00Z",
      },
      score: 0.92,
      priority: "high",
      contributing_signals: [],
      generated_by: "demo_pack",
      pathogen_pack_version: "1.0.0",
      policy_pack_version: "1.0.0",
      knowledge_bundle_id: "kb_demo",
      triggering_rule_ids: ["rule-1"],
      context_facts: {},
    };

    expect(deriveActionPriority(action, [assessment])).toBe("high");
  });

  it("builds ward summaries from snapshot, assessments, actions, and alerts", () => {
    const snapshot: StateSnapshotRef = {
      hospital_id: "hospital-a",
      at: "2026-04-07T10:00:00Z",
      time_window: {
        start: "2026-04-07T09:00:00Z",
        end: "2026-04-07T10:00:00Z",
      },
      patient_states: [
        {
          patient_id: "patient-1",
          room_id: "room-101",
          ward_id: "ward-a",
          start_at: "2026-04-07T09:00:00Z",
          end_at: null,
        },
      ],
      staff_states: [
        {
          staff_id: "staff-1",
          ward_id: "ward-a",
          room_id: "room-101",
          role: "nurse",
          start_at: "2026-04-07T09:30:00Z",
          end_at: null,
        },
      ],
      room_states: [
        {
          room_id: "room-101",
          ward_id: "ward-a",
          active_patients: ["patient-1"],
          active_staff: ["staff-1"],
        },
      ],
      ward_states: [
        {
          ward_id: "ward-a",
          room_ids: ["room-101"],
          active_patients: ["patient-1"],
          active_staff: ["staff-1"],
        },
      ],
      source_event_ids: ["event-1"],
    };

    const assessments: RiskAssessment[] = [
      {
        assessment_id: "assessment-1",
        entity_scope: "ward",
        target_id: "ward-a",
        time_window: {
          start: "2026-04-07T09:00:00Z",
          end: "2026-04-07T10:00:00Z",
        },
        score: 0.92,
        priority: "high",
        contributing_signals: [],
        generated_by: "demo_pack",
        pathogen_pack_version: "1.0.0",
        policy_pack_version: "1.0.0",
        knowledge_bundle_id: "kb_demo",
        triggering_rule_ids: ["rule-1"],
        context_facts: {},
      },
    ];

    const actions: ProposedAction[] = [
      {
        action_id: "action-1",
        risk_assessment_id: "assessment-1",
        action_definition_id: "review_isolation",
        action_type: "review_isolation_placement",
        category: "infection_control",
        priority: null,
        execution_mode: "review_only",
        target_scope: "patient",
        target_id: "patient-1",
        rationale: "Test rationale",
        required_reviewer_role: "ipc_lead",
        status: "pending_review",
        constraints_applied: [],
        knowledge_bundle_id: "kb_demo",
        triggering_rule_ids: ["rule-1"],
        audit_ref: "audit-1",
        created_at: "2026-04-07T10:00:00Z",
      },
    ];

    const alerts: PriorityAlert[] = [
      {
        alert_id: "alert-1",
        assessment_id: "assessment-1",
        target_id: "ward-a",
        priority: "high",
        summary: "Ward A requires review",
        top_signals: ["hospital_onset_case"],
      },
    ];

    const summaries = buildWardSummaries(snapshot, assessments, enrichActions(actions, assessments), alerts);

    expect(summaries).toHaveLength(1);
    expect(summaries[0].wardId).toBe("ward-a");
    expect(summaries[0].linkedActions).toHaveLength(1);
    expect(summaries[0].alertSummary).toBe("Ward A requires review");
    expect(summaries[0].derivedPriority).toBe("high");
  });

  it("prefers direct action priority when present", () => {
    const action: ProposedAction = {
      action_id: "action-2",
      risk_assessment_id: null,
      action_definition_id: "screening",
      action_type: "Screen and mask symptomatic person",
      category: "screening_and_source_control",
      priority: "critical",
      execution_mode: "review_only",
      target_scope: "patient",
      target_id: "patient-2",
      rationale: "Direct trigger priority",
      required_reviewer_role: "frontline_clinician_or_unit_lead",
      status: "pending_review",
      constraints_applied: [],
      knowledge_bundle_id: "kb_compiled",
      triggering_rule_ids: ["respiratory_symptoms_at_arrival"],
      audit_ref: "audit-2",
      created_at: "2026-04-07T10:00:00Z",
    };

    expect(deriveActionPriority(action, [])).toBe("critical");
  });
});
