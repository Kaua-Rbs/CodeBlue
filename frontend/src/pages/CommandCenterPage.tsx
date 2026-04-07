import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  useActionsQuery,
  useAlertsQuery,
  useAssessmentsQuery,
  useEventsQuery,
  useLoadDemoEventsMutation,
  useRunAssessmentMutation,
  useStateQuery,
} from "../features/useCodeBlueData";
import {
  buildWardSummaries,
  enrichActions,
  formatPriorityLabel,
  formatScopeLabel,
  formatTimestamp,
} from "../lib/derived";
import { useUiStore } from "../store/uiStore";
import styles from "./CommandCenterPage.module.css";

function priorityClass(priority: string): string {
  if (priority === "critical" || priority === "high") {
    return styles.high;
  }
  if (priority === "medium") {
    return styles.medium;
  }
  return styles.low;
}

export function CommandCenterPage() {
  const navigate = useNavigate();
  const [lastRunSummary, setLastRunSummary] = useState<string>("No run executed in this session.");
  const setSelectedActionId = useUiStore((state) => state.setSelectedActionId);
  const setSelectedWardId = useUiStore((state) => state.setSelectedWardId);
  const openTrace = useUiStore((state) => state.openTrace);

  const eventsQuery = useEventsQuery();
  const actionsQuery = useActionsQuery();
  const assessmentsQuery = useAssessmentsQuery();
  const alertsQuery = useAlertsQuery();
  const stateQuery = useStateQuery();

  const loadDemoEventsMutation = useLoadDemoEventsMutation();
  const runMutation = useRunAssessmentMutation();

  const actions = actionsQuery.data ?? [];
  const assessments = assessmentsQuery.data ?? [];
  const alerts = alertsQuery.data ?? [];

  const enrichedActions = useMemo(
    () => enrichActions(actions, assessments),
    [actions, assessments],
  );

  const wardSummaries = useMemo(
    () => buildWardSummaries(stateQuery.data ?? undefined, assessments, enrichedActions, alerts),
    [stateQuery.data, assessments, enrichedActions, alerts],
  );

  const pendingActions = enrichedActions.filter((action) => action.status === "pending_review");
  const highPriorityPending = pendingActions.filter((action) =>
    ["critical", "high"].includes(action.derivedPriority),
  );

  const topActions = [...pendingActions].sort((left, right) => {
    const order = { critical: 0, high: 1, medium: 2, low: 3, unknown: 4 };
    return order[left.derivedPriority] - order[right.derivedPriority];
  });

  const uniqueBundles = Array.from(
    new Set(
      [...enrichedActions, ...assessments]
        .map((item) => item.knowledge_bundle_id)
        .filter((item): item is string => Boolean(item)),
    ),
  );

  const hasEvents = (eventsQuery.data?.length ?? 0) > 0;

  return (
    <section className={styles.page}>
      <div className={styles.toolbar}>
        <div>
          <h2 className={styles.toolbarTitle}>Command Center</h2>
          <p className={styles.toolbarText}>
            This screen shows the current review queue, the highest-risk wards the backend
            can currently derive, and the overall system posture based on the current API
            surface.
          </p>
        </div>

        <div className={styles.toolbarActions}>
          <button
            type="button"
            className={styles.secondaryButton}
            disabled={loadDemoEventsMutation.isPending || hasEvents}
            onClick={() => {
              loadDemoEventsMutation.mutate(undefined, {
                onSuccess: () => {
                  setLastRunSummary("Demo events loaded. Run an assessment to generate actions.");
                },
              });
            }}
          >
            {hasEvents ? "Demo events already loaded" : "Load Demo Events"}
          </button>
          <button
            type="button"
            className={styles.primaryButton}
            disabled={runMutation.isPending || !hasEvents}
            onClick={() => {
              runMutation.mutate(undefined, {
                onSuccess: (result) => {
                  setLastRunSummary(
                    `Run completed at ${formatTimestamp(result.snapshot_at)} · ${result.action_count} actions generated via ${result.runtime_mode} runtime with ${result.matched_trigger_count} matched triggers.`,
                  );
                },
                onError: (error) => {
                  setLastRunSummary(
                    error instanceof Error ? error.message : "Run failed. Check backend state.",
                  );
                },
              });
            }}
          >
            Run Assessment
          </button>
        </div>
      </div>

      <div className={styles.notice}>
        <strong>Current session status</strong>
        <div>{lastRunSummary}</div>
      </div>

      <div className={styles.summaryBand}>
        <article className={`${styles.metricCard} ${styles.critical}`}>
          <div className={styles.metricLabel}>High-priority pending</div>
          <div className={styles.metricValue}>{highPriorityPending.length}</div>
          <div className={styles.metricNote}>Pending actions linked to high or critical assessments.</div>
        </article>
        <article className={`${styles.metricCard} ${styles.watch}`}>
          <div className={styles.metricLabel}>Open review queue</div>
          <div className={styles.metricValue}>{pendingActions.length}</div>
          <div className={styles.metricNote}>Current actions still waiting for manual disposition.</div>
        </article>
        <article className={`${styles.metricCard} ${styles.watch}`}>
          <div className={styles.metricLabel}>High-risk wards</div>
          <div className={styles.metricValue}>
            {wardSummaries.filter((ward) => ["high", "critical"].includes(ward.derivedPriority)).length}
          </div>
          <div className={styles.metricNote}>Derived from current ward-level assessments.</div>
        </article>
        <article className={`${styles.metricCard} ${styles.stable}`}>
          <div className={styles.metricLabel}>Active alerts</div>
          <div className={styles.metricValue}>{alerts.length}</div>
          <div className={styles.metricNote}>Priority alert records currently available from the backend.</div>
        </article>
        <article className={`${styles.metricCard} ${styles.stable}`}>
          <div className={styles.metricLabel}>Loaded events</div>
          <div className={styles.metricValue}>{eventsQuery.data?.length ?? 0}</div>
          <div className={styles.metricNote}>Required before state, risk, and action generation.</div>
        </article>
      </div>

      {!hasEvents ? (
        <div className={styles.notice}>
          <strong>No events are loaded yet.</strong>
          <div>
            Use <em>Load Demo Events</em> to seed the backend, then run an assessment to
            populate the dashboard with state, risks, and actions.
          </div>
        </div>
      ) : null}

      <div className={styles.grid}>
        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <h3>Prioritized Action Queue</h3>
              <p>Best currently available view of what should be reviewed first.</p>
            </div>
            <button className={styles.panelLink} onClick={() => navigate("/actions")} type="button">
              Open actions
            </button>
          </div>
          <div className={styles.list}>
            {topActions.length > 0 ? (
              topActions.slice(0, 5).map((action) => (
                <article key={action.action_id} className={styles.itemCard}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedActionId(action.action_id);
                      navigate("/actions");
                    }}
                  >
                    <div className={styles.itemTop}>
                      <div>
                        <h4>{action.action_type}</h4>
                        <p className={styles.itemMeta}>
                          {formatScopeLabel(action.target_scope)} · {action.target_id}
                        </p>
                      </div>
                      <span className={`${styles.badge} ${priorityClass(action.derivedPriority)}`}>
                        {formatPriorityLabel(action.derivedPriority)}
                      </span>
                    </div>
                    <p className={styles.itemMeta}>{action.rationale}</p>
                    <div className={styles.chipRow}>
                      <span className={styles.chip}>{action.required_reviewer_role}</span>
                      <span className={styles.chip}>{action.status}</span>
                    </div>
                  </button>
                </article>
              ))
            ) : (
              <article className={styles.itemCard}>
                <strong>No actions yet.</strong>
                <p className={styles.itemMeta}>Run an assessment after events are available.</p>
              </article>
            )}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <h3>Ward Risk Board</h3>
              <p>Composed from the current state snapshot, assessments, and linked actions.</p>
            </div>
            <button className={styles.panelLink} onClick={() => navigate("/wards")} type="button">
              Open wards
            </button>
          </div>
          <div className={styles.list}>
            {wardSummaries.length > 0 ? (
              wardSummaries.map((ward) => (
                <article key={ward.wardId} className={styles.itemCard}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedWardId(ward.wardId);
                      navigate("/wards");
                    }}
                  >
                    <div className={styles.itemTop}>
                      <div>
                        <h4>{ward.wardId}</h4>
                        <p className={styles.itemMeta}>
                          {ward.activePatients} patients · {ward.activeStaff} staff · {ward.roomCount} rooms
                        </p>
                      </div>
                      <span className={`${styles.badge} ${priorityClass(ward.derivedPriority)}`}>
                        {formatPriorityLabel(ward.derivedPriority)}
                      </span>
                    </div>
                    <p className={styles.itemMeta}>{ward.alertSummary ?? "No alert summary available."}</p>
                    <div className={styles.chipRow}>
                      <span className={styles.chip}>{ward.linkedActions.length} linked actions</span>
                      <span className={styles.chip}>
                        {ward.score !== null ? `Score ${ward.score.toFixed(2)}` : "No score"}
                      </span>
                    </div>
                  </button>
                </article>
              ))
            ) : (
              <article className={styles.itemCard}>
                <strong>No ward data yet.</strong>
                <p className={styles.itemMeta}>
                  The backend needs a state snapshot and assessments before wards can be shown.
                </p>
              </article>
            )}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <h3>System and Trigger Context</h3>
              <p>Current backend-level indicators that support operator trust.</p>
            </div>
          </div>
          <div className={styles.list}>
            <article className={styles.itemCard}>
              <div className={styles.itemTop}>
                <div>
                  <h4>Knowledge bundles in use</h4>
                  <p className={styles.itemMeta}>Derived from actions and assessments currently in memory.</p>
                </div>
              </div>
              <div className={styles.chipRow}>
                {uniqueBundles.length > 0 ? (
                  uniqueBundles.map((bundleId) => <span key={bundleId} className={styles.chip}>{bundleId}</span>)
                ) : (
                  <span className={styles.chip}>No bundles surfaced yet</span>
                )}
              </div>
            </article>

            <article className={styles.itemCard}>
              <div className={styles.itemTop}>
                <div>
                  <h4>Current state snapshot</h4>
                  <p className={styles.itemMeta}>
                    {stateQuery.data ? `Snapshot at ${formatTimestamp(stateQuery.data.at)}` : "No snapshot currently available"}
                  </p>
                </div>
              </div>
              <div className={styles.chipRow}>
                <span className={styles.chip}>
                  {stateQuery.data ? `${stateQuery.data.source_event_ids.length} source events` : "No source events"}
                </span>
                <span className={styles.chip}>
                  {stateQuery.data ? `${stateQuery.data.ward_states.length} wards` : "0 wards"}
                </span>
              </div>
            </article>

            <article className={styles.itemCard}>
              <div className={styles.itemTop}>
                <div>
                  <h4>Trace entry point</h4>
                  <p className={styles.itemMeta}>
                    Open the reasoning chain for the highest-priority pending action.
                  </p>
                </div>
              </div>
              <button
                type="button"
                className={styles.panelLink}
                onClick={() => openTrace(topActions[0]?.action_id ?? null)}
              >
                Open trace
              </button>
            </article>
          </div>
        </section>
      </div>
    </section>
  );
}
