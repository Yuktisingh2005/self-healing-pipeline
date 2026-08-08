import Hero from "@/components/Hero";
import LiveStatus from "@/components/LiveStatus";
import DeploymentTimeline from "@/components/DeploymentTimeline";
import PipelineBackground from "@/components/PipelineBackground";

export default function Home() {
  return (
    <main className="relative">
      <PipelineBackground />
      <Hero />
      <LiveStatus />
      <DeploymentTimeline />
    </main>
  );
}