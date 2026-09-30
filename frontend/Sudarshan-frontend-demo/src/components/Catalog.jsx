import React from "react";
import { Search } from "lucide-react";
import { demoAssets } from "../data/demoData";
import { PageTitle } from "./PagePrimitives";

export default function Catalog(){
  return <div className="page"><PageTitle title="Data Catalog" subtitle="Compact local catalogue for the demo imagery pack." actions={<div className="searchMini"><Search size={13}/><input placeholder="Filter assets"/></div>} /><section className="panel tablePanel"><div className="catalogTable header"><span>Asset</span><span>Site</span><span>Observation</span><span>Sensor</span><span>Quality</span><span>Role</span></div>{demoAssets.map(a=><div className="catalogTable" key={a.id}><b>{a.id}</b><span>{a.site}</span><span>{a.date}</span><span>{a.sensor}</span><span>{a.quality}</span><span>{a.role}</span></div>)}</section></div>
}
