"use client";

import { motion } from "framer-motion";

export default function StatusDot({ healthy }: { healthy: boolean }) {
  const color = healthy ? "var(--success)" : "var(--fail)";
  return (
    <span className="relative flex h-3 w-3">
      <motion.span
        animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        className="absolute inline-flex h-full w-full rounded-full"
        style={{ backgroundColor: color }}
      />
      <span className="relative inline-flex rounded-full h-3 w-3" style={{ backgroundColor: color }} />
    </span>
  );
}