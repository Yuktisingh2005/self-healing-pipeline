"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { DeploymentEvent } from "@/lib/api";
import { getSummary } from "@/lib/summary";

function TimelineCard({ event, index }: { event: DeploymentEvent; index: number }) {
  const [open, setOpen] = useState(false);
  const promoted = event.status === "promoted";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.45, delay: index * 0.04, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card rounded-xl px-6 py-4"
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
          <span className="font-mono text-xs text-[var(--text-secondary)] hidden sm:inline">
            {new Date(event.timestamp).toLocaleString()}
          </span>
        </div>

        <button
          onClick={() => setOpen((v) => !v)}
          className="font-mono text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors flex items-center gap-1"
        >
          {open ? "Hide details" : "View details"}
          <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
            ▾
          </motion.span>
        </button>
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed pt-3 mt-3 border-t border-[var(--border)]">
              {getSummary(event)}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function TimelineList({ events }: { events: DeploymentEvent[] }) {
  return (
    <div className="flex flex-col gap-3">
      {events.map((event, i) => (
        <TimelineCard key={event.id} event={event} index={i} />
      ))}
    </div>
  );
}