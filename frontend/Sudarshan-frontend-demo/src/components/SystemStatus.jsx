import React from "react";
import { CheckCircle2, WifiOff, Database, Cpu, Server } from "lucide-react";
import { PageTitle } from "./PagePrimitives";
import { system } from "../data/demoData";

export default function SystemStatus(){
 const rows=[['Network',system.network,WifiOff],['Archive',`${system.archiveItems} demo items`,Database],['Index',system.index,Server],['Model',system.model,Cpu]];
 return <div className="page"><PageTitle title="System Status" subtitle="Runtime state for the offline frontend demonstration." actions={<span className="modeBanner">No external API dependency</span>} /><section className="panel statusPanel">{rows.map(([label,value,Icon])=><div className="statusRow" key={label}><Icon size={17}/><span>{label}</span><b>{value}</b><CheckCircle2 size={15}/></div>)}</section><section className="panel disclosure"><h2>Integration boundary</h2><p>The frontend is ready to receive local backend services later. Until then, it intentionally stays in fixture mode.</p></section></div>
}
