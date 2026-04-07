import type {
  PriorityAlert,
  ProposedAction,
  RiskAssessment,
  RiskPriority,
  StateSnapshotRef,
  TargetScope,
} from "../types/api";

export interface DerivedAction extends ProposedAction {
  derivedPriority: RiskPriority | "unknown";
}

export interface WardSummary {
  wardId: string;
  derivedPriority: RiskPriority | "unknown";
  score: number | null;
  activePatients: number;
  activeStaff: number;
  roomCount: number;
  linkedActions: DerivedAction[];
  alertSummary: string | null;
}

const priorityOrder: Record<RiskPriority | "unknown", number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
  unknown: 4,
};

export function deriveActionPriority(
  action: ProposedAction,
  assessments: RiskAssessment[],
): RiskPriority | "unknown" {
  if (action.priority) {
    return action.priority;
  }
  if (!action.risk_assessment_id) {
    return "unknown";
  }

  const assessment = assessments.find((item) => item.assessment_id === action.risk_assessment_id);
  return assessment?.priority ?? "unknown";
}

export function enrichActions(
  actions: ProposedAction[],
  assessments: RiskAssessment[],
): DerivedAction[] {
  return actions.map((action) => ({
    ...action,
    derivedPriority: deriveActionPriority(action, assessments),
  }));
}

function mapPatientsToWard(snapshot: StateSnapshotRef): Map<string, string> {
  const mapping = new Map<string, string>();
  snapshot.patient_states.forEach((patient) => mapping.set(patient.patient_id, patient.ward_id));
  return mapping;
}

function mapRoomsToWard(snapshot: StateSnapshotRef): Map<string, string> {
  const mapping = new Map<string, string>();
  snapshot.room_states.forEach((room) => mapping.set(room.room_id, room.ward_id));
  return mapping;
}

function resolveActionWardId(
  action: ProposedAction,
  snapshot: StateSnapshotRef,
): string | null {
  const patientToWard = mapPatientsToWard(snapshot);
  const roomToWard = mapRoomsToWard(snapshot);

  const scope = action.target_scope as TargetScope;
  if (scope === "ward") {
    return action.target_id;
  }
  if (scope === "patient") {
    return patientToWard.get(action.target_id) ?? null;
  }
  if (scope === "room") {
    return roomToWard.get(action.target_id) ?? null;
  }
  return null;
}

export function buildWardSummaries(
  snapshot: StateSnapshotRef | undefined,
  assessments: RiskAssessment[],
  actions: DerivedAction[],
  alerts: PriorityAlert[],
): WardSummary[] {
  if (!snapshot) {
    return [];
  }

  return snapshot.ward_states
    .map((ward) => {
      const wardAssessment = assessments.find(
        (item) => item.entity_scope === "ward" && item.target_id === ward.ward_id,
      );

      const linkedActions = actions.filter(
        (action) => resolveActionWardId(action, snapshot) === ward.ward_id,
      );

      const linkedAlerts = alerts.filter((alert) => alert.target_id === ward.ward_id);

      return {
        wardId: ward.ward_id,
        derivedPriority: wardAssessment?.priority ?? linkedActions[0]?.derivedPriority ?? "unknown",
        score: wardAssessment?.score ?? null,
        activePatients: ward.active_patients.length,
        activeStaff: ward.active_staff.length,
        roomCount: ward.room_ids.length,
        linkedActions,
        alertSummary: linkedAlerts[0]?.summary ?? null,
      };
    })
    .sort((left, right) => priorityOrder[left.derivedPriority] - priorityOrder[right.derivedPriority]);
}

export function formatPriorityLabel(priority: RiskPriority | "unknown"): string {
  if (priority === "unknown") {
    return "Unknown";
  }
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

export function formatScopeLabel(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
