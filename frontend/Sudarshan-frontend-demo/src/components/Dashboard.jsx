import React from "react";
import { Search, GitCompare, Database, ShieldCheck, Activity, ArrowRight, CheckCircle2 } from "lucide-react";
import { PageTitle, StatCard } from "./PagePrimitives";
import { system, demoQueries, reviewsSeed } from "../data/demoData";
import MapMock from "./MapMock";

export default function Dashboard({setPage,openSite}){
  return <div className="page">
    <PageTitle title="Analyst Dashboard" subtitle="Local, offline workspace for semantic imagery retrieval and temporal change review." actions={<span className="modeBanner">{system.mode}</span>} />
    <div className="metricGrid four">
      <StatCard label="Demo imagery items" value={system.archiveItems} note="small local archive" icon={Database}/>
      <StatCard label="Investigation queries" value={system.queries} note="primary + secondary" icon={Search}/>
      <StatCard label="Review queue" value={reviewsSeed.length} note="local demo cases" icon={ShieldCheck}/>
      <StatCard label="Network" value="OFFLINE" note="no runtime API calls" icon={Activity}/>
    </div>
    <div className="dashboardGrid">
      <section className="panel focusPanel">
        <div className="panelHead"><div><h2>Primary investigation</h2><p>Recommended demo path</p></div><button className="primary" onClick={()=>setPage("search")}><Search size={14}/> Start search</button></div>
        <div className="queryHero"><span>Natural-language query</span><b>"{demoQueries[0].query}"</b><small>Search -> rank -> inspect -> verify -> review -> export</small></div>
        <div className="processRow"><span>1 Search</span><i></i><span>2 Select</span><i></i><span>3 Compare</span><i></i><span>4 Verify</span><i></i><span>5 Export</span></div>
      </section>
      <section className="panel mapPanel"><div className="panelHead"><div><h2>Demo AOI</h2><p>Candidate distribution within the local reference region</p></div></div><MapMock compact/></section>
      <section className="panel recentPanel"><div className="panelHead"><h2>Recent analyst cases</h2></div>{reviewsSeed.map(r=><button className="caseRow" key={r.id} onClick={()=>r.id!=="SITE-C" && openSite(r.id)}><div><b>{r.id}</b><span>{r.type}</span></div><span className="rowMeta">{r.status}</span><ArrowRight size={14}/></button>)}</section>
      <section className="panel integrityPanel"><div className="panelHead"><h2>Demo integrity</h2><ShieldCheck size={17}/></div><div className="integrityList"><div><CheckCircle2/> No external runtime APIs</div><div><CheckCircle2/> No large archive dependency</div><div><CheckCircle2/> Fixture values are explicitly labelled</div><div><CheckCircle2/> Provenance UI present</div></div></section>
    </div>
  </div>
}
