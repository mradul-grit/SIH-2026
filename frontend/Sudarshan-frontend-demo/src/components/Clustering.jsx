import React from "react";
import { Layers3, SlidersHorizontal } from "lucide-react";
import { clusters } from "../data/demoData";
import { PageTitle } from "./PagePrimitives";
import MapMock from "./MapMock";

export default function Clustering(){
  return <div className="page"><PageTitle title="Clustering" subtitle="Group similar locations without constructing a separate query for every site." actions={<button className="ghost"><SlidersHorizontal size={14}/> Cluster settings</button>} /><div className="twoCol"><section className="panel"><div className="panelHead"><div><h2>Cluster overview</h2><p>Local demo embedding groups</p></div></div><MapMock/></section><section className="panel"><div className="panelHead"><div><h2>Cluster summary</h2></div><Layers3 size={16}/></div>{clusters.map(c=><div className="clusterCard" key={c.id}><div><b>Cluster {c.id}</b><span>{c.name}</span></div><strong>{c.sites}</strong><small>{c.similarity}</small></div>)}</section></div></div>
}
