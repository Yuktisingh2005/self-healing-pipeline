export interface DeploymentEvent {
  id: number;
  git_sha: string;
  status: "promoted" | "rolled_back";
  reason: string | null;
  timestamp: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8100";

export async function getEvents(): Promise<DeploymentEvent[]> {
  try {
    const res = await fetch(`${API_URL}/api/events/`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function getHealth(): Promise<{ status: string; git_sha: string } | null> {
  try {
    const res = await fetch(`${API_URL}/health/`, { cache: "no-store" });
    const body = await res.json();
    return body;
  } catch {
    return null;
  }
}