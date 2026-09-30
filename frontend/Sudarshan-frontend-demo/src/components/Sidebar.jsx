import React from "react";
import {
  LayoutDashboard, Search, GitCompare, Network, ClipboardCheck, Database,
  BarChart3, FileOutput, Settings, UploadCloud, Layers3, Clock3, Server,
  SlidersHorizontal, CircleDotDashed
} from "lucide-react";

const items = [
  ["Dashboard", LayoutDashboard, "dashboard"],
  ["Search & Explore", Search, "search"],
  ["Change Analysis", GitCompare, "change"],
  ["Similar Sites", Network, "similar"],
  ["Clustering", Layers3, "clustering"],
  ["Temporal Viewer", Clock3, "temporal"],
  ["Review Queue", ClipboardCheck, "review"],
  ["Data Ingestion", UploadCloud, "ingest"],
  ["Data Catalog", Database, "catalog"],
  ["Analytics", BarChart3, "analytics"],
  ["Export & Provenance", FileOutput, "export"],
  ["System Status", Server, "status"],
  ["Settings", Settings, "settings"]
];

export default function Sidebar({page,setPage, reviewCount}) {
  return <aside className="sidebar">
    <div className="brand compactBrand">
      <div className="flag"><i></i><i></i><i></i></div>
      <div><b>Sudarshan</b><span>Semantic Retrieval + Multi-Temporal Change</span></div>
    </div>
    <div className="navGroupLabel">ANALYST WORKSPACE</div>
    <nav>
      {items.map(([label,Icon,id]) =>
        <button key={id} className={page===id?"nav active":"nav"} onClick={()=>setPage(id)}>
          <Icon size={16}/><span>{label}</span>
          {id==="review" && <em>{reviewCount}</em>}
        </button>
      )}
    </nav>
    <div className="sideFooter">
      <div>Observe</div><div>Understand</div><div>Secure</div>
    </div>
  </aside>
}
