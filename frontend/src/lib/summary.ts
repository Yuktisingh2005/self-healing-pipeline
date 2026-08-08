import type { DeploymentEvent } from "./api";

export function getSummary(event: DeploymentEvent): string {
  if (event.status === "promoted") {
    return "Passed health checks (app + DB connectivity) and was promoted to live traffic. No downtime.";
  }

  const reason = event.reason || "Health check failed after retries.";
  return `Rolled back — ${reason} Previous version was never taken down, so live traffic was unaffected.`;
}