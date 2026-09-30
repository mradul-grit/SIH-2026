import React, {useState} from "react";
import { CheckCircle2, XCircle, Clock3 } from "lucide-react";
import { PageTitle, StatusBadge } from "./PagePrimitives";
import { reviewsSeed } from "../data/demoData";

export default function ReviewQueue({reviews,setReviews,onOpen}){
  const [filter,setFilter]=useState("all");
  const visible=reviews.filter(r=>filter==="all" || r.status.toLowerCase().replace(" ","")==filter);
  const decide=(id,status)=>setReviews(rs=>rs.map(r=>r.id===id?{...r,status,updatedAt:new Date().toLocaleTimeString()}:r));
  return <div className="page"><PageTitle title="Review Queue" subtitle="Analyst confirmation, rejection, and local audit state." actions={<span className="modeBanner">Session audit enabled</span>} />
    <div className="queueFilters"><button className={filter==="all"?"selected":""} onClick={()=>setFilter("all")}>All</button><button className={filter==="pending"?"selected":""} onClick={()=>setFilter("pending")}>Pending</button><button className={filter==="confirmed"?"selected":""} onClick={()=>setFilter("confirmed")}>Confirmed</button><button className={filter==="rejected"?"selected":""} onClick={()=>setFilter("rejected")}>Rejected</button></div>
    <section className="panel tablePanel"><div className="queueTable header"><span>Site</span><span>Type</span><span>Status</span><span>Rationale</span><span>Actions</span></div>{visible.map(r=><div className="queueTable" key={r.id}><button className="linkButton" onClick={()=>onOpen(r.id)}>{r.id}</button><span>{r.type}</span><StatusBadge status={r.status}/><span>{r.rationale}</span><div className="rowActions"><button title="Confirm" onClick={()=>decide(r.id,"Confirmed")}><CheckCircle2 size={14}/></button><button title="Reject" onClick={()=>decide(r.id,"Rejected")}><XCircle size={14}/></button><button title="Needs review" onClick={()=>decide(r.id,"Pending")}><Clock3 size={14}/></button></div></div>)}</section>
  </div>
}

export { reviewsSeed };
