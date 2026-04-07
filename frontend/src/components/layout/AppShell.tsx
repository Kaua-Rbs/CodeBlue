import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useEventsQuery, useHealthQuery } from "../../features/useCodeBlueData";
import { TraceDrawer } from "../trace/TraceDrawer";
import styles from "./AppShell.module.css";

function buildNavLinkClass(isActive: boolean): string {
  return isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink;
}

export function AppShell() {
  const location = useLocation();
  const healthQuery = useHealthQuery();
  const eventsQuery = useEventsQuery();

  const hospitalLabel =
    eventsQuery.data && eventsQuery.data.length > 0
      ? eventsQuery.data[0].hospital_id
      : "No site loaded";

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.brandMark}>CB</div>
          <div>
            <h1 className={styles.brandTitle}>CodeBlue</h1>
            <p className={styles.brandSubtitle}>Operator client · influenza-first demo</p>
          </div>
        </div>

        <section className={styles.navGroup}>
          <p className={styles.navLabel}>Primary surfaces</p>
          <div className={styles.navLinks}>
            <NavLink to="/" end className={({ isActive }) => buildNavLinkClass(isActive)}>
              <span className={styles.navLinkTitle}>Command Center</span>
              <span className={styles.navLinkText}>Overview, priorities, and operational posture.</span>
            </NavLink>
            <NavLink to="/actions" className={({ isActive }) => buildNavLinkClass(isActive)}>
              <span className={styles.navLinkTitle}>Actions</span>
              <span className={styles.navLinkText}>Review queue, rationale, and decisions.</span>
            </NavLink>
            <NavLink to="/wards" className={({ isActive }) => buildNavLinkClass(isActive)}>
              <span className={styles.navLinkTitle}>Wards</span>
              <span className={styles.navLinkText}>Current concentration of risk and ward context.</span>
            </NavLink>
          </div>
        </section>

        <section className={styles.sidebarCard}>
          <h2>Current runtime context</h2>
          <p>
            This frontend is wired to the current CodeBlue API surface and reflects the
            current backend truth, not only the static prototype.
          </p>
          <div className={styles.sidebarPills}>
            <div className={styles.sidebarPill}>
              <span>Route</span>
              <strong>{location.pathname}</strong>
            </div>
            <div className={styles.sidebarPill}>
              <span>Site</span>
              <strong>{hospitalLabel}</strong>
            </div>
            <div className={styles.sidebarPill}>
              <span>API</span>
              <strong>{healthQuery.data?.status ?? "loading"}</strong>
            </div>
          </div>
        </section>
      </aside>

      <div className={styles.content}>
        <div className={styles.contentInner}>
          <header className={styles.header}>
            <div>
              <h2 className={styles.headerTitle}>Hospital outbreak operations</h2>
              <p className={styles.headerText}>
                Reviewable operational recommendations built from canonical state,
                risk outputs, and governed action logic.
              </p>
            </div>
            <div className={styles.headerPills}>
              <div className={`${styles.headerPill} ${styles.accentPill}`}>
                <strong>Health</strong>
                {healthQuery.data?.status ?? "Loading"}
              </div>
              <div className={styles.headerPill}>
                <strong>App</strong>
                {healthQuery.data?.app ?? "CodeBlue"}
              </div>
              <div className={styles.headerPill}>
                <strong>Env</strong>
                {healthQuery.data?.env ?? "development"}
              </div>
            </div>
          </header>

          <Outlet />
        </div>
      </div>

      <TraceDrawer />
    </div>
  );
}
