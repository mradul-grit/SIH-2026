import React, {useState} from "react";
import { Search, Image, Pentagon, SlidersHorizontal, Bookmark, Map, List, Sparkles, ChevronDown } from "lucide-react";
import MapMock from "./MapMock";
import { DEMO_PRIMARY_QUERY, DEMO_SECONDARY_QUERY, demoQueries, searchResults } from "../data/demoData";
import { PageTitle, StatusBadge } from "./PagePrimitives";

export default function SearchPage({onOpen}) {
  const [query,setQuery] = useState(DEMO_PRIMARY_QUERY);
  const [active,setActive] = useState("q1");
  const [view,setView] = useState("map");
  const current = demoQueries.find(x=>x.id===active) || demoQueries[0];
  const results = searchResults.filter(r=>r.q===active);

  const runQuery = (q) => {
    setQuery(q);
    setActive(q===DEMO_SECONDARY_QUERY?"q2":"q1");
  };

  return <div className="page">
    <PageTitle title="Search & Explore" subtitle="Semantic retrieval over a deliberately small local imagery archive." actions={<button className="ghost"><Sparkles size={14}/> Example Queries</button>} />
    <div className="searchTabs"><button className="active"><Search size={14}/> Text Search</button><button><Image size={14}/> Image Search</button><button><Pentagon size={14}/> Polygon Search</button><button><SlidersHorizontal size={14}/> Advanced Filters</button></div>
    <div className="searchLayout refined">
      <section className="panel searchPanel">
        <div className="sectionHeading"><span className="step">1</span><div><b>Natural-language query</b><small>Meaning-first retrieval</small></div></div>
        <div className="queryBox"><Search size={18}/><input value={query} onChange={e=>setQuery(e.target.value)} /><button onClick={()=>runQuery(query)}>Search</button></div>
        <div className="exampleStrip"><button onClick={()=>runQuery(DEMO_PRIMARY_QUERY)}>newly built structures near a river</button><button onClick={()=>runQuery(DEMO_SECONDARY_QUERY)}>large vehicle concentrations on open ground</button></div>
        <div className="sectionHeading"><span className="step">2</span><div><b>AOI</b><small>Spatial constraint</small></div></div>
        <div className="seg"><button className="selected">Draw on Map</button><button>Upload GeoJSON</button><button>Select from List</button></div>
        <div className="miniAoi"><Map size={16}/><div><b>Demo AOI</b><small>Selected region for the walkthrough</small></div><button>Clear</button></div>
        <div className="sectionHeading"><span className="step">3</span><div><b>Date range</b><small>Temporal constraint</small></div></div>
        <div className="dates"><span>2024-01-01</span><b>to</b><span>2026-09-30</span></div>
        <div className="quick"><button>3 months</button><button>6 months</button><button>1 year</button><button className="selected">Custom</button></div>
        <div className="sectionHeading"><span className="step">4</span><div><b>Sources / sensors</b><small>Filter by acquisition type</small></div></div>
        <div className="checks"><label><input type="checkbox" defaultChecked/> Sentinel-1 (SAR)</label><label><input type="checkbox" defaultChecked/> Sentinel-2 (Optical)</label><label><input type="checkbox"/> Landsat</label><label><input type="checkbox"/> Bhuvan</label></div>
        <div className="sectionHeading"><span className="step">5</span><div><b>Additional filters</b><small>Quality and metadata</small></div></div>
        <div className="filters"><div>Cloud cover<strong>&lt; 30%</strong></div><div>Region<strong>Demo AOI</strong></div><div>Resolution<strong>Available</strong></div><div>Product<strong>All approved</strong></div></div>
        <div className="buttonRow"><button className="ghost">Reset</button><button className="primary" onClick={()=>runQuery(query)}><Search size={15}/> Run semantic search</button></div>
      </section>
      <section className="resultsArea">
        <div className="resultHead"><div><b>Search Results</b> <span>({current.count} demo candidates)</span></div><div className="viewToggle"><button className={view==="map"?"selected":""} onClick={()=>setView("map")}><Map size={13}/> Map</button><button className={view==="list"?"selected":""} onClick={()=>setView("list")}><List size={13}/> List</button></div></div>
        {view==="map" && <MapMock selected={current.selectedId}/>} 
        <div className="resultToolbar"><span>Sorted by relevance</span><button><Bookmark size={13}/> Save Query</button><button><ChevronDown size={13}/> Confidence</button></div>
        <div className="resultGrid">
          {results.map((r,i)=><button className={"resultCard "+(i===0?"chosen":"")} key={r.id} onClick={()=>onOpen(r.id)}>
            <div className={"thumb "+r.siteClass}><div className="thumbRiver"></div><span>{i+1}</span></div>
            <div className="cardBody"><div className="cardTop"><b>{r.id}</b><strong>{r.score}%</strong></div><label>{r.type}</label><div className="tagRow"><em>{r.tag}</em><StatusBadge status={r.status}/></div><small>{r.coords}</small><small>{r.date}</small></div>
          </button>)}
        </div>
        <div className="resultFoot"><span>Local fixture results - not live inference</span><button className="ghost">Open selected site</button></div>
      </section>
    </div>
  </div>
}
