import React from "react";
import { UploadCloud, CheckCircle2, Database, RefreshCw, FileText } from "lucide-react";
import MapMock from "./MapMock";
import { system, demoAssets } from "../data/demoData";
import { PageTitle, StatCard } from "./PagePrimitives";

export default function Ingestion() {
  const staged = demoAssets.slice(0,8);
  return <div className="page">
    <PageTitle title="Data Ingestion & AOI" subtitle="Stage only the small archive needed for the controlled demo and preserve geospatial provenance." actions={<span className="modeBanner">32-item target archive</span>} />
    <div className="workflow"><span className="active">1 Ingest</span><i></i><span>2 Define AOI</span><i></i><span>3 Index / Embed</span><i></i><span>4 Cluster / Analyze</span><i></i><span>5 Explore / Review</span></div>
    <div className="metricGrid three"><StatCard label="Target archive" value={system.archiveItems} note="imagery items" icon={Database}/><StatCard label="Sites" value={system.sites} note="demo cases" icon={FileText}/><StatCard label="Index" value="Fixture" note="no full rebuild" icon={RefreshCw}/></div>
    <div className="ingestGrid">
      <section className="panel upload"><h2>Upload satellite data</h2><p>GeoTIFF / COG / approved local assets</p><div className="drop"><UploadCloud size={34}/><b>Drop files here</b><small>Stage only required local imagery</small></div>{staged.map(x=><div className="fileRow" key={x.id}><Database size={14}/><div><b>{x.id} / {x.site}</b><small>{x.sensor} - {x.date}</small></div><span><CheckCircle2 size={14}/> local</span></div>)}</section>
      <section className="panel aoiPanel"><h2>Area of Interest</h2><p>Draw, upload or select the demo AOI.</p><div className="aoiActions"><button className="selected">Draw on Map</button><button>Upload GeoJSON</button><button>Select list</button></div><MapMock/><div className="aoiStats"><span>AOI<strong>Demo region</strong></span><span>Coverage<strong>Small / controlled</strong></span><span>CRS<strong>Preserved</strong></span></div></section>
      <section className="panel indexPanel"><h2>Incremental update</h2><div className="metric"><span>Existing fixture index</span><b>{system.archiveItems} items</b></div><div className="progress"><i style={{width:"78%"}}></i></div><div className="metric"><span>New staged items</span><b>0</b></div><div className="progress"><i style={{width:"0%"}}></i></div><div className="indexNote"><CheckCircle2/> Existing index preserved - no full rebuild.</div><button className="primary"><RefreshCw size={14}/> Simulate incremental update</button></section>
    </div>
  </div>
}
