import { useMemo } from "react";
import { useActionExplanationQuery, useActionsQuery, useAssessmentsQuery } from "../../features/useCodeBlueData";
import { deriveActionPriority, formatPriorityLabel } from "../../lib/derived";
import { useUiStore } from "../../store/uiStore";
import styles from "./TraceDrawer.module.css";

export function TraceDrawer() {
  const traceOpen = useUiStore((state) => state.traceOpen);
  const traceActionId = useUiStore((state) => state.traceActionId);
  const closeTrace = useUiStore((state) => state.closeTrace);

  const actionsQuery = useActionsQuery();
  const assessmentsQuery = useAssessmentsQuery();
  const explanationQuery = useActionExplanationQuery(traceActionId);

  const currentAction = useMemo(
    () => actionsQuery.data?.find((item) => item.action_id === traceActionId) ?? null,
    [actionsQuery.data, traceActionId],
  );

  const derivedPriority =
    currentAction && assessmentsQuery.data
      ? deriveActionPriority(currentAction, assessmentsQuery.data)
      : "unknown";

  return (
    <aside className={`${styles.drawer} ${traceOpen ? styles.drawerOpen : ""}`} aria-hidden={!traceOpen}>
      <div className={styles.topbar}>
        <div>
          <h3>Trace</h3>
          <p>Why the action exists and what context produced it.</p>
        </div>
        <button className={styles.closeButton} onClick={closeTrace} type="button">
          X
        </button>
      </div>

      {currentAction ? (
        <div className={styles.stack}>
          <section className={styles.card}>
            <p className={styles.label}>Decision summary</p>
            <strong>{currentAction.action_type}</strong>
            <p>{currentAction.rationale}</p>
          </section>

          <section className={styles.card}>
            <p className={styles.label}>Current action context</p>
            <div className={styles.list}>
              <div className={styles.fact}>Target: {currentAction.target_scope} · {currentAction.target_id}</div>
              <div className={styles.fact}>Status: {currentAction.status}</div>
              <div className={styles.fact}>Derived priority: {formatPriorityLabel(derivedPriority)}</div>
              <div className={styles.fact}>Bundle: {currentAction.knowledge_bundle_id ?? "Not available"}</div>
            </div>
          </section>

          <section className={styles.card}>
            <p className={styles.label}>Trigger and rule chain</p>
            <div className={styles.chips}>
              {currentAction.triggering_rule_ids.length > 0 ? (
                currentAction.triggering_rule_ids.map((ruleId) => (
                  <span key={ruleId} className={styles.chip}>
                    {ruleId}
                  </span>
                ))
              ) : (
                <span className={styles.chip}>No triggering rules surfaced</span>
              )}
            </div>
          </section>

          <section className={styles.card}>
            <p className={styles.label}>Constraints and execution mode</p>
            <div className={styles.chips}>
              <span className={styles.chip}>{currentAction.execution_mode}</span>
              {currentAction.constraints_applied.map((constraint) => (
                <span key={constraint} className={styles.chip}>
                  {constraint}
                </span>
              ))}
            </div>
          </section>

          <section className={styles.card}>
            <p className={styles.label}>Narrative explanation</p>
            <p>{explanationQuery.data?.explanation ?? "Loading explanation..."}</p>
          </section>

          {explanationQuery.data?.trace ? (
            <section className={styles.card}>
              <p className={styles.label}>Compiled runtime trace</p>
              <div className={styles.list}>
                <div className={styles.fact}>
                  Runtime: {String(explanationQuery.data.trace.runtime_mode ?? "unknown")}
                </div>
                <div className={styles.fact}>
                  Deployment profile: {String(explanationQuery.data.trace.deployment_profile_id ?? "n/a")}
                </div>
                <div className={styles.fact}>
                  Matched triggers: {Array.isArray(explanationQuery.data.trace.matched_trigger_ids)
                    ? explanationQuery.data.trace.matched_trigger_ids.join(", ")
                    : "n/a"}
                </div>
                <div className={styles.fact}>
                  Matched mappings: {Array.isArray(explanationQuery.data.trace.matched_mapping_ids)
                    ? explanationQuery.data.trace.matched_mapping_ids.join(", ")
                    : "n/a"}
                </div>
              </div>
            </section>
          ) : null}
        </div>
      ) : (
        <div className={styles.card}>
          <p className={styles.label}>No action selected</p>
          <p>Select an action and open trace to inspect the current reasoning chain.</p>
        </div>
      )}
    </aside>
  );
}
