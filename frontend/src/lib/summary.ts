import type { DeploymentEvent } from "./api";

export function getSummary(event: DeploymentEvent): string {
  if (event.status === "promoted") {
    return "Passed health checks (app + DB connectivity) and was promoted to live traffic. No downtime.";
  }

  // Rolled back — build a specific summary from the reason we stored.
  const reason = event.reason || "Health check failed after retries.";

  if (reason.toLowerCase().includes("db")) {
    return `Rolled back — the new version couldn't connect to the database. ${reason}`;
  }

  return `Rolled back — ${reason} Previous version was never taken down, so live traffic was unaffected.`;
}