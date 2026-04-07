import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "../lib/api";
import { demoEvents } from "../lib/demoEvents";
import type { ReviewActionRequest } from "../types/api";

export const queryKeys = {
  health: ["health"] as const,
  events: ["events"] as const,
  state: ["state"] as const,
  actions: ["actions"] as const,
  assessments: ["assessments"] as const,
  alerts: ["alerts"] as const,
  explanation: (actionId: string | null) => ["explanation", actionId] as const,
};

export function useHealthQuery() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.getHealth,
  });
}

export function useEventsQuery() {
  return useQuery({
    queryKey: queryKeys.events,
    queryFn: api.getEvents,
  });
}

export function useActionsQuery() {
  return useQuery({
    queryKey: queryKeys.actions,
    queryFn: api.getActions,
  });
}

export function useAssessmentsQuery() {
  return useQuery({
    queryKey: queryKeys.assessments,
    queryFn: api.getAssessments,
  });
}

export function useAlertsQuery() {
  return useQuery({
    queryKey: queryKeys.alerts,
    queryFn: api.getAlerts,
  });
}

export function useStateQuery() {
  return useQuery({
    queryKey: queryKeys.state,
    queryFn: async () => {
      try {
        return await api.getState();
      } catch (error) {
        if (error instanceof ApiError && error.status === 400) {
          return null;
        }
        throw error;
      }
    },
  });
}

export function useActionExplanationQuery(actionId: string | null) {
  return useQuery({
    queryKey: queryKeys.explanation(actionId),
    queryFn: () => api.explainAction(actionId!),
    enabled: Boolean(actionId),
  });
}

export function useLoadDemoEventsMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.ingestEvents(demoEvents),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.events }),
        queryClient.invalidateQueries({ queryKey: queryKeys.state }),
        queryClient.invalidateQueries({ queryKey: queryKeys.actions }),
        queryClient.invalidateQueries({ queryKey: queryKeys.assessments }),
        queryClient.invalidateQueries({ queryKey: queryKeys.alerts }),
      ]);
    },
  });
}

export function useRunAssessmentMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.triggerRun,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.actions }),
        queryClient.invalidateQueries({ queryKey: queryKeys.assessments }),
        queryClient.invalidateQueries({ queryKey: queryKeys.alerts }),
        queryClient.invalidateQueries({ queryKey: queryKeys.state }),
      ]);
    },
  });
}

export function useReviewActionMutation(actionId: string | null) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ReviewActionRequest) => api.reviewAction(actionId!, payload),
    onSuccess: async (_, __) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.actions }),
        queryClient.invalidateQueries({ queryKey: queryKeys.explanation(actionId) }),
      ]);
    },
  });
}
