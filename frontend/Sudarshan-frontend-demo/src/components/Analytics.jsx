import React from "react";
import { Activity, Clock3, HardDrive, Cpu, SearchCheck, ShieldCheck } from "lucide-react";
import { system } from "../data/demoData";
import { PageTitle, StatCard } from "./PagePrimitives";

export default function Analytics() {
  return <div className="page">
    <PageTitle title="Analytics" subtitle="Separate real measurements from fixture-mode UI demonstrations." actions={<span className="modeBanner">Fixture-aware</span>} />
    <div className="metricGrid three">
      <StatCard label="Archive items" value={system.archiveItems} note="planned demo pack" icon={HardDrive}/>
      <StatCard label="Indexed sites" value={system.sites} note="controlled cases" icon={SearchCheck}/>
      <StatCard label="Offline state" value="ON" note="no network required" icon={ShieldCheck}/>
      <StatCard label="Query latency" value="Not measured" note="fixture-only mode" icon={Clock3}/>
      <StatCard label="Index build time" value="Not measured" note="fixture-only mode" icon={Cpu}/>
      <StatCard label="Inference throughput" value="Not measured" note="real model not connected" icon={Activity}/>
    </div>
    <section className="panel disclosure"><h2>Metrics integrity</h2><p>Only measured values should replace the fixture placeholders once the local retrieval/change pipeline is connected. This keeps the frontend from presenting invented production metrics.</p></section>
  </div>
}
