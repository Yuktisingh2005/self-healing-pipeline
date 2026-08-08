"use client";

import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="min-h-[70vh] flex flex-col items-center justify-center text-center px-6">
      <motion.p
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="font-mono text-sm text-[var(--text-secondary)] mb-6 px-3 py-1 rounded-full border border-[var(--border)]"
      >
        ● system online
      </motion.p>

      <motion.h1
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="font-display font-bold text-5xl md:text-7xl leading-[1.05] fade-edges"
      >
        Self-healing
        <br />
        <span className="gradient-text">CI/CD pipeline</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
        className="mt-8 max-w-xl text-[var(--text-secondary)] text-lg"
      >
        Every deploy is shadow-tested against a live health check before it
        ever reaches production. If it fails, it never gets the chance to.
      </motion.p>
    </section>
  );
}