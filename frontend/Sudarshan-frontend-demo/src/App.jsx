import React, {useState} from "react";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import SearchPage from "./components/SearchPage";
import SiteAnalysis from "./components/SiteAnalysis";
import Ingestion from "./components/Ingestion";
import Analytics from "./components/Analytics";
import Dashboard from "./components/Dashboard";
import ReviewQueue, { reviewsSeed } from "./components/ReviewQueue";
import SimilarSites from "./components/SimilarSites";
import Clustering from "./components/Clustering";
import TemporalViewer from "./components/TemporalViewer";
import Catalog from "./components/Catalog";
import ExportProvenance from "./components/ExportProvenance";
import SystemStatus from "./components/SystemStatus";
import Settings from "./components/Settings";

export default function App(){
 const [page,setPage]=useState("dashboard");
 const [siteId,setSiteId]=useState("SITE-A");
 const [reviews,setReviews]=useState(reviewsSeed);
 const openSite=(id)=>{setSiteId(id);setPage("change")};
 const reviewCount=reviews.filter(r=>r.status==="Pending"||r.status==="Needs Review").length;
 const updateReview=(id,status)=>{
   const mapped=status==="confirmed"?"Confirmed":status==="rejected"?"Rejected":"Pending";
   setReviews(rs=>rs.map(r=>r.id===id?{...r,status:mapped,updatedAt:new Date().toLocaleTimeString()}:r));
 };
 let content;
 switch(page){
  case "dashboard": content=<Dashboard setPage={setPage} openSite={openSite}/>; break;
  case "search": content=<SearchPage onOpen={openSite}/>; break;
  case "change": content=<SiteAnalysis siteId={siteId} onBack={()=>setPage("search")} onSetSite={setSiteId} onReview={updateReview}/>; break;
  case "similar": content=<SimilarSites openSite={openSite}/>; break;
  case "clustering": content=<Clustering/>; break;
  case "temporal": content=<TemporalViewer siteId={siteId}/>; break;
  case "review": content=<ReviewQueue reviews={reviews} setReviews={setReviews} onOpen={openSite}/>; break;
  case "ingest": content=<Ingestion/>; break;
  case "catalog": content=<Catalog/>; break;
  case "analytics": content=<Analytics/>; break;
  case "export": content=<ExportProvenance/>; break;
  case "status": content=<SystemStatus/>; break;
  case "settings": content=<Settings/>; break;
  default: content=<Dashboard setPage={setPage} openSite={openSite}/>;
 }
 return <div className="app"><Sidebar page={page} setPage={setPage} reviewCount={reviewCount}/><div className="main"><Topbar/><main>{content}</main></div></div>
}
