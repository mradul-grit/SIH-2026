import React, {useState} from "react";
import { Play, Pause, CalendarDays } from "lucide-react";
import { sites } from "../data/demoData";
import { PageTitle } from "./PagePrimitives";

export default function TemporalViewer({siteId="SITE-A"}){
  const s=sites[siteId]||sites["SITE-A"];
  const [index,setIndex]=useState(0); const [playing,setPlaying]=useState(false);
  React.useEffect(()=>{if(!playing)return; const t=setInterval(()=>setIndex(i=>(i+1)%s.timeline.length),1100);return()=>clearInterval(t)},[playing,s.timeline.length]);
  return <div className="page"><PageTitle title="Temporal Viewer" subtitle="Review the local observation sequence and evidence of persistence." actions={<button className="ghost" onClick={()=>setPlaying(v=>!v)}>{playing?<Pause size={14}/>:<Play size={14}/>} {playing?"Pause":"Play sequence"}</button>} />
    <section className="panel temporalHero"><div className="temporalSelected"><span>Selected site</span><b>{s.id}</b><strong>{s.title}</strong></div><div className="temporalEvidence"><span><CalendarDays size={13}/> {s.observations} observations</span><b>{s.earliest}</b></div></section>
    <section className="panel timelineLarge"><div className="timelineViewport">{s.timeline.map((x,i)=><button key={x[0]} className={i===index?"timeCard active":"timeCard"} onClick={()=>setIndex(i)}><div className="fakeImage"><span>{x[0]}</span></div><b>{x[1]}</b></button>)}</div><div className="timelineControl"><button className="primary" onClick={()=>setPlaying(v=>!v)}>{playing?<Pause size={14}/>:<Play size={14}/>} {playing?"Pause":"Play"}</button><input type="range" min="0" max={s.timeline.length-1} value={index} onChange={e=>setIndex(Number(e.target.value))}/><span>{s.timeline[index][0]}</span></div></section>
  </div>
}
