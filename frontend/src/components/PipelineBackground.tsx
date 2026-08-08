export default function PipelineBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-[var(--bg)]">
      <div
        className="mesh-blob absolute top-[-10%] left-[10%] h-[500px] w-[500px] rounded-full opacity-30"
        style={{ background: "radial-gradient(circle, #818cf8, transparent 70%)" }}
      />
      <div
        className="mesh-blob absolute bottom-[-15%] right-[5%] h-[600px] w-[600px] rounded-full opacity-25"
        style={{ background: "radial-gradient(circle, #22d3ee, transparent 70%)", animationDelay: "-8s" }}
      />
      <div
        className="mesh-blob absolute top-[30%] right-[25%] h-[350px] w-[350px] rounded-full opacity-20"
        style={{ background: "radial-gradient(circle, #34d399, transparent 70%)", animationDelay: "-15s" }}
      />
    </div>
  );
}