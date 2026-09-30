import React from "react";
import { ShieldCheck, Database, Cpu, WifiOff, UserRound, Bell } from "lucide-react";
import { system } from "../data/demoData";

export default function Topbar(){
  return <header className="topbar">
    <div className="topIdentity">
      <div className="brandTitle">Sudarshan</div>
      <div className="brandSub">Semantic Retrieval + Multi-Temporal Change Analysis</div>
    </div>
    <div className="trustBlock"><ShieldCheck size={18}/><span>Ministry of Defence<br/><b>Indian Army (DGIS)</b></span></div>
    <div className="slogan">From Data to Decisions</div>
    <div className="topActions">
      <div className="statusChip"><WifiOff size={15}/><div><b>OFFLINE</b><small>{system.network}</small></div></div>
      <div className="miniChip"><Database size={14}/><div><b>Local archive</b><small>{system.archiveItems} demo items</small></div></div>
      <div className="miniChip"><Cpu size={14}/><div><b>Inference</b><small>Fixture mode</small></div></div>
      <Bell size={16} className="topIcon"/>
      <div className="userChip"><span>MT</span><div><b>Analyst</b><small>Demo session</small></div></div>
    </div>
  </header>
}
