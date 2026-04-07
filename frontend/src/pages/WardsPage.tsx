import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useActionsQuery, useAlertsQuery, useAssessmentsQuery, useStateQuery } from "../features/useCodeBlueData";
import { buildWardSummaries, enrichActions, formatPriorityLabel, formatTimestamp } from "../lib/derived";
import { useUiStore } from "../store/uiStore";
import styles from "./WardsPage.module.css";

function priorityClass(priority: string): string {
  if (priority === "critical" || priority === "high") {
    return styles.high;
  }
  if (priority === "medium") {
    return styles.medium;
  }
  return styles.low;
}

export function WardsPage() {
  const navigate = useNavigate();
  const selectedWardId = useUiStore((state) => state.selectedWardId);
  const setSelectedWardId = useUiStore((state) => state.setSelectedWardId);
  const setSelectedActionId = useUiStore((state) => state.setSelectedActionId);
  const openTrace = useUiStore((state) => state.openTrace);

  const actionsQuery = useActionsQuery();
  const assessmentsQuery = useAssessmentsQuery();
  const alertsQuery = useAlertsQuery();
  const stateQuery = useStateQuery();

  const enrichedActions = useMemo(
    () => enrichActions(actionsQuery.data ?? [], assessmentsQuery.data ?? []),
    [actionsQuery.data, assessmentsQuery.data],
  );

  const wardSummaries = useMemo(
    () => buildWardSummaries(stateQuery.data ?? undefined, assessmentsQuery.data ?? [], enrichedActions, alertsQuery.data ?? []),
    [stateQuery.data, assessmentsQuery.data, enrichedActions, alertsQuery.data],
  );

  useEffect(() => {
    if (!selectedWardId && wardSummaries.length > 0) {
      setSelectedWardId(wardSummaries[0].wardId);
    }
  }, [selectedWardId, setSelectedWardId, wardSummaries]);

  const selectedWard = wardSummaries.find((ward) => ward.wardId === selectedWardId) ?? wardSummaries[0];

  return (
    <section className={styles.page}>
      <div className={styles.layout}>
        <section className={styles.panel}>
          <div className={styles.header}>
            <h2>Ward view</h2>
            <p>Derived from the current snapshot, ward-level assessments, and linked actions.</p>
          </div>
          <div className={styles.list}>
            {wardSummaries.length > 0 ? (
              wardSummaries.map((ward) => (
                <article
                  key={ward.wardId}
                  className={`${styles.wardCard} ${ward.wardId === selectedWard?.wardId ? styles.wardCardSelected : ""}`}
                  onClick={() => setSelectedWardId(ward.wardId)}
                >
                  <div className={styles.row}>
                    <div>
                      <h3>{ward.wardId}</h3>
                      <p className={styles.meta}>{ward.alertSummary ?? "No alert summary available."}</p>
                    </div>
                    <span className={`${styles.badge} ${priorityClass(ward.derivedPriority)}`}>
                      {formatPriorityLabel(ward.derivedPriority)}
                    </span>
                  </div>
                  <div className={styles.chips}>
                    <span className={styles.chip}>{ward.activePatients} active patients</span>
                    <span className={styles.chip}>{ward.linkedActions.length} linked actions</span>
                  </div>
                </article>
              ))
            ) : (
              <article className={styles.wardCard}>
                <h3>No ward data available</h3>
                <p className={styles.meta}>Ward detail becomes available once state and assessments exist.</p>
              </article>
            )}
          </div>
        </section>

        <section className={styles.panel}>
          {selectedWard ? (
            <>
              <div className={styles.header}>
                <h2>{selectedWard.wardId}</h2>
                <p>
                  This view is assembled from current backend responses. It will become richer
                  once a dedicated ward summary endpoint exists.
                </p>
              </div>

              <div className={styles.detailSection}>
                <p className={styles.label}>Current profile</p>
                <div className={styles.grid}>
                  <div className={styles.detailCard}>
                    <strong>Priority</strong>
                    <span>{formatPriorityLabel(selectedWard.derivedPriority)}</span>
                  </div>
                  <div className={styles.detailCard}>
                    <strong>Score</strong>
                    <span>{selectedWard.score !== null ? selectedWard.score.toFixed(2) : "Not available"}</span>
                  </div>
                  <div className={styles.detailCard}>
                    <strong>Active patients</strong>
                    <span>{selectedWard.activePatients}</span>
                  </div>
                  <div className={styles.detailCard}>
                    <strong>Active staff</strong>
                    <span>{selectedWard.activeStaff}</span>
                  </div>
                </div>
              </div>

              <div className={styles.detailSection}>
                <p className={styles.label}>Snapshot context</p>
                <div className={styles.detailCard}>
                  <strong>Current snapshot time</strong>
                  <span>{formatTimestamp(stateQuery.data?.at)}</span>
                </div>
              </div>

              <div className={styles.detailSection}>
                <p className={styles.label}>Actions affecting this ward</p>
                <div className={styles.list}>
                  {selectedWard.linkedActions.length > 0 ? (
                    selectedWard.linkedActions.map((action) => (
                      <article key={action.action_id} className={styles.actionCard}>
                        <button
                          type="button"
                          className={styles.actionButton}
                          onClick={() => {
                            setSelectedActionId(action.action_id);
                            navigate("/actions");
                          }}
                        >
                          <div className={styles.row}>
                            <div>
                              <h3>{action.action_type}</h3>
                              <p className={styles.meta}>{action.rationale}</p>
                            </div>
                            <span className={`${styles.badge} ${priorityClass(action.derivedPriority)}`}>
                              {formatPriorityLabel(action.derivedPriority)}
                            </span>
                          </div>
                        </button>
                      </article>
                    ))
                  ) : (
                    <article className={styles.actionCard}>
                      <h3>No linked actions</h3>
                      <p className={styles.meta}>This ward has no directly linked actions in the current API state.</p>
                    </article>
                  )}
                </div>
              </div>

              <div className={styles.detailSection}>
                <p className={styles.label}>Trace entry point</p>
                <div className={styles.actionCard}>
                  <button
                    type="button"
                    className={styles.actionButton}
                    onClick={() => openTrace(selectedWard.linkedActions[0]?.action_id ?? null)}
                  >
                    <strong>Open trace for top linked action</strong>
                    <p className={styles.meta}>
                      Use the trace drawer to inspect the reasoning chain for the selected ward’s
                      most important linked action.
                    </p>
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className={styles.header}>
              <h2>No ward selected</h2>
              <p>Ward detail will appear once the backend has enough state and assessment data.</p>
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
