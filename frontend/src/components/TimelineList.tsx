"use client";

import { motion } from "framer-motion";
import type { DeploymentEvent } from "@/lib/api";
import { getSummary } from "@/lib/summary";

export default function TimelineList({ events }: { events: DeploymentEvent[] }) {
  return (
    <div className="flex flex-col gap-3">
      {events.map((event, i) => {
        const promoted = event.status === "promoted";
        return (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45, delay: i * 0.04, ease: [0.16, 1, 0.3, 1] }}
            className="glass-card rounded-xl px-6 py-4 flex flex-col gap-3"
          >
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-4">
                <span
                  className="font-mono text-xs px-2.5 py-1 rounded-full uppercase font-medium"
                  style={{
                    color: promoted ? "var(--success)" : "var(--fail)",
                    backgroundColor: promoted ? "rgba(52,211,153,0.1)" : "rgba(248,113,113,0.1)",
                  }}
                >
                  {promoted ? "promoted" : "rolled back"}
                </span>
                <span className="font-mono text-base">{event.git_sha}</span>
              </div>
              <span className="font-mono text-xs text-[var(--text-secondary)]">
                {new Date(event.timestamp).toLocaleString()}
              </span>
            </div>

            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {getSummary(event)}
            </p>
          </motion.div>
        );
      })}
    </div>
  );
}