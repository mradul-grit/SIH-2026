import React from "react";
import { CheckCircle2, AlertTriangle, Info } from "lucide-react";

export function PageTitle({title,subtitle,actions}){
  return <div className="pageTitle"><div><h1>{title}</h1><p>{subtitle}</p></div><div className="titleActions">{actions}</div></div>
}

export function StatCard({label,value,note,icon:Icon}){
  return <div className="metricCard"><div className="metricIcon"><Icon size={17}/></div><small>{label}</small><b>{value}</b>{note && <span>{note}</span>}</div>
}

export function StatusBadge({status}){
  const cls = status.toLowerCase().includes("supp") || status.toLowerCase().includes("reject") ? "badge warn" : status.toLowerCase().includes("high") || status.toLowerCase().includes("confirm") ? "badge good" : "badge";
  return <span className={cls}>{status}</span>
}

export function InfoLine({label,value,kind="info"}){
  const Icon = kind === "ok" ? CheckCircle2 : kind === "warn" ? AlertTriangle : Info;
  return <div className="infoLine"><Icon size={14}/><span>{label}</span><b>{value}</b></div>
}
