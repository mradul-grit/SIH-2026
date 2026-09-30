import React from "react";
import { Settings as SettingsIcon } from "lucide-react";
import { PageTitle } from "./PagePrimitives";

export default function Settings(){
 return <div className="page"><PageTitle title="Settings" subtitle="Demo configuration and display controls." actions={<SettingsIcon size={18}/>} /><section className="panel settingsPanel">{[['Demo mode','Enabled','Fixture values clearly labelled'],['Network access','Blocked','No runtime external calls'],['Archive size','32 items target','Small controlled dataset'],['Theme','Dark analyst UI','Reference workstation style'],['Auto-play timeline','Off','Manual demo control']].map(([a,b,c])=><div className="settingRow" key={a}><div><b>{a}</b><span>{c}</span></div><strong>{b}</strong></div>)}</section></div>
}
