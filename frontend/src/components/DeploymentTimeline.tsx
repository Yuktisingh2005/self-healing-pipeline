import { getEvents } from "@/lib/api";
import TimelineList from "./TimelineList";

export default async function DeploymentTimeline() {
  const events = await getEvents();

  return (
    <section className="px-6 md:px-16 py-16 max-w-4xl mx-auto">
      <p className="font-mono text-xs text-[var(--text-secondary)] uppercase tracking-widest mb-6">
        Deployment history
      </p>

      {events.length === 0 ? (
        <p className="text-[var(--text-secondary)]">No deployments recorded yet.</p>
      ) : (
        <TimelineList events={events} />
      )}
    </section>
  );
}