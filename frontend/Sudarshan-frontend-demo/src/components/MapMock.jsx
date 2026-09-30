import React from "react";

export default function MapMock({compact=false, selected="SITE-A"}) {
  const dots = [
    [15,28,"red"],[25,50,"orange"],[39,22,"blue"],[52,40,"red"],[64,27,"cyan"],
    [72,55,"orange"],[82,34,"red"],[36,71,"blue"],[59,67,"orange"],[76,73,"cyan"],
    [23,79,"red"],[88,61,"blue"]
  ];
  return <div className={"mapMock " + (compact ? "compact" : "")}>
    <div className="mapGrid"></div>
    <div className="mountains m1"></div><div className="mountains m2"></div>
    <div className="river"></div>
    <div className="aoi"></div>
    {dots.map((d,i)=><span key={i} className={"mapDot "+d[2]+(i===0?" selectedDot":"")} style={{left:d[0]+"%",top:d[1]+"%"}} title={i===0?selected:""} />)}
    <span className="mapLabel l1">Northern Region</span>
    <span className="mapLabel l2">River Corridor</span>
    <span className="mapLabel l3">AOI</span>
    <div className="scale">10 km</div>
    <div className="mapBadge">LOCAL DEMO MAP</div>
    <div className="mapControls"><button>+</button><button>-</button><button>◉</button></div>
  </div>
}
