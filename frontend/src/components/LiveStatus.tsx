import { getHealth } from "@/lib/api";
import StatusDot from "./StatusDot";

export default async function LiveStatus() {
  const health = await getHealth();
  const isHealthy = health?.status === "healthy";

  return (
    <section className="px-6 md:px-16 py-8">
      <div className="glass-card rounded-2xl px-8 py-6 max-w-2xl mx-auto flex items-center gap-5 flex-wrap">
        <StatusDot healthy={isHealthy} />
        <div>
          <p className="font-mono text-xs text-[var(--text-secondary)] uppercase tracking-widest mb-1">
            Current live version
          </p>
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-2xl">{health?.git_sha ?? "unknown"}</span>
            <span
              className="font-mono text-xs uppercase px-2 py-0.5 rounded-full"
              style={{
                color: isHealthy ? "var(--success)" : "var(--fail)",
                backgroundColor: isHealthy ? "rgba(52,211,153,0.1)" : "rgba(248,113,113,0.1)",
              }}
            >
              {isHealthy ? "healthy" : "unreachable"}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}