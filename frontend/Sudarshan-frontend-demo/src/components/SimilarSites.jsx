import React from "react";
import { Network, Search, Sparkles } from "lucide-react";
import { sites, clusters } from "../data/demoData";
import { PageTitle, StatusBadge } from "./PagePrimitives";
import MapMock from "./MapMock";

export default function SimilarSites({openSite}){
  const cards=[
    ["SITE-A","Construction-like",96],
    ["SITE-B","Open-ground activity",87],
    ["SITE-C","River-adjacent seasonal",81],
    ["SITE-D","Quality-confounded",74]
  ];
  return <div className="page"><PageTitle title="Similar Sites" subtitle="Discover visually or semantically related locations from the local feature set." actions={<button className="ghost"><Sparkles size={14}/> Find similar to SITE-A</button>} />
    <div className="similarGrid"><section className="panel mapPanel"><div className="panelHead"><div><h2>Similarity map</h2><p>Local candidate distribution</p></div></div><MapMock/></section><section className="panel clusterPanel"><div className="panelHead"><div><h2>Clusters</h2><p>Embedding-style grouping for the demo</p></div></div>{clusters.map(c=><div className="clusterRow" key={c.id}><span>Cluster {c.id}</span><b>{c.name}</b><em>{c.sites} sites</em><small>{c.similarity}</small></div>)}</section></div>
    <div className="similarCards">{cards.map(([id,label,score])=><button className="similarCard" key={id} onClick={()=>openSite(id)}><div className="similarThumb"></div><div><b>{id}</b><strong>{score}% similarity</strong><span>{label}</span><small>{sites[id]?.title||"Local demo site"}</small></div></button>)}</div>
  </div>
}
