import type {
  EventEnvelope,
  ExplainabilityResponse,
  HealthResponse,
  IngestEventsResponse,
  PriorityAlert,
  ProposedAction,
  ReviewActionRequest,
  ReviewDecision,
  RiskAssessment,
  RunResponse,
  StateSnapshotRef,
} from "../types/api";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? (body as { detail: unknown }).detail
        : body;
    throw new ApiError(`Request failed for ${path}`, response.status, detail);
  }

  return body as T;
}

export const api = {
  getHealth: () => request<HealthResponse>("/health"),
  getEvents: () => request<EventEnvelope[]>("/api/v1/events"),
  ingestEvents: (events: EventEnvelope[]) =>
    request<IngestEventsResponse>("/api/v1/events", {
      method: "POST",
      body: JSON.stringify({ events }),
    }),
  triggerRun: () =>
    request<RunResponse>("/api/v1/runs", {
      method: "POST",
    }),
  getState: () => request<StateSnapshotRef>("/api/v1/state"),
  getActions: () => request<ProposedAction[]>("/api/v1/actions"),
  reviewAction: (actionId: string, payload: ReviewActionRequest) =>
    request<ReviewDecision>(`/api/v1/actions/${actionId}/review`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getAssessments: () => request<RiskAssessment[]>("/api/v1/risk/assessments"),
  getAlerts: () => request<PriorityAlert[]>("/api/v1/risk/alerts"),
  explainAction: (actionId: string) =>
    request<ExplainabilityResponse>(`/api/v1/explainability/actions/${actionId}`),
};
