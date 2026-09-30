export const DEMO_PRIMARY_QUERY = "newly built structures near a river";
export const DEMO_SECONDARY_QUERY = "large vehicle concentrations on open ground";

export const demoQueries = [
  {
    id: "q1",
    query: DEMO_PRIMARY_QUERY,
    count: 8,
    label: "Construction near river",
    selectedId: "SITE-A",
  },
  {
    id: "q2",
    query: DEMO_SECONDARY_QUERY,
    count: 4,
    label: "Vehicle concentration",
    selectedId: "SITE-B",
  },
];

export const searchResults = [
  { id:"SITE-A", score:96.4, type:"Construction (New)", tag:"Near River", date:"10 observations", coords:"Demo AOI / verified locally", q:"q1", status:"High confidence", siteClass:"target" },
  { id:"SITE-B", score:91.7, type:"Vehicle / infrastructure pattern", tag:"Similar context", date:"7 observations", coords:"Demo AOI / verified locally", q:"q1", status:"Review", siteClass:"similar" },
  { id:"SITE-C", score:72.1, type:"Seasonal variation", tag:"Suppressed", date:"7 observations", coords:"Demo AOI / verified locally", q:"q1", status:"Suppressed", siteClass:"nochange" },
  { id:"SITE-D", score:48.7, type:"Possible change", tag:"Quality confounded", date:"6 observations", coords:"Demo AOI / verified locally", q:"q1", status:"Low evidence", siteClass:"quality" },
  { id:"SITE-E", score:89.5, type:"Vehicle concentration", tag:"Open Ground", date:"6 observations", coords:"Secondary demo set", q:"q2", status:"Review", siteClass:"secondary" },
  { id:"SITE-F", score:82.2, type:"Open-ground activity", tag:"SAR + Optical", date:"5 observations", coords:"Secondary demo set", q:"q2", status:"Review", siteClass:"secondary" },
  { id:"SITE-G", score:75.3, type:"Land activity", tag:"Possible change", date:"4 observations", coords:"Secondary demo set", q:"q2", status:"Needs review", siteClass:"secondary" },
  { id:"SITE-H", score:69.8, type:"Open-ground pattern", tag:"Low evidence", date:"3 observations", coords:"Secondary demo set", q:"q2", status:"Low evidence", siteClass:"secondary" }
];

export const sites = {
  "SITE-A": {
    id: "SITE-A",
    title: "New structures near river",
    type: "Construction (New)",
    confidence: 94,
    earliest: "First supported observation in the staged sequence",
    observations: 10,
    usable: 8,
    riverDistance: "Near mapped river corridor",
    query: DEMO_PRIMARY_QUERY,
    beforeLabel: "Baseline observation",
    afterLabel: "Latest usable observation",
    evidence: [
      "Persistent structural footprint across usable observations",
      "Spatial relationship with the selected river corridor",
      "Temporal persistence across later observations",
      "Quality checks passed for the selected evidence pair"
    ],
    quality: {
      "Cloud / Haze": "Low",
      "Seasonal Variation": "Low",
      "Shadow Effect": "Low",
      "Viewing Geometry": "Low",
      "Registration Error": "Low",
      "Sensor Inconsistency": "Low"
    },
    timeline: [
      ["Obs 01", "Baseline"],
      ["Obs 02", "No change"],
      ["Obs 03", "No change"],
      ["Obs 04", "Ground work"],
      ["Obs 05", "Change supported"],
      ["Obs 06", "Persistent"],
      ["Obs 07", "Persistent"],
      ["Obs 08", "Expansion"],
      ["Obs 09", "Persistent"],
      ["Obs 10", "Latest usable"]
    ]
  },
  "SITE-B": {
    id: "SITE-B",
    title: "Open-ground vehicle concentration",
    type: "Vehicle Concentration",
    confidence: 89,
    earliest: "Earliest supported observation is available in the local demo sequence",
    observations: 7,
    usable: 6,
    riverDistance: "Open ground context",
    query: DEMO_SECONDARY_QUERY,
    beforeLabel: "Earlier observation",
    afterLabel: "Latest usable observation",
    evidence: [
      "Repeated dense activity pattern across observations",
      "Open-ground context supports semantic query match",
      "Optical/SAR views are available for cross-checking",
      "Quality filters passed for the selected comparison"
    ],
    quality: {
      "Cloud / Haze": "Low",
      "Seasonal Variation": "Low",
      "Shadow Effect": "Low",
      "Viewing Geometry": "Medium",
      "Registration Error": "Low",
      "Sensor Inconsistency": "Low"
    },
    timeline: [
      ["Obs 01", "Baseline"],
      ["Obs 02", "Low activity"],
      ["Obs 03", "Low activity"],
      ["Obs 04", "Concentration"],
      ["Obs 05", "Persistent"],
      ["Obs 06", "Persistent"],
      ["Obs 07", "Latest usable"]
    ]
  },
  "SITE-C": {
    id: "SITE-C",
    title: "Seasonal variation control",
    type: "No physical change supported",
    confidence: 86,
    earliest: "No supported physical change",
    observations: 7,
    usable: 7,
    riverDistance: "Agricultural / seasonal context",
    query: DEMO_PRIMARY_QUERY,
    beforeLabel: "Dry season",
    afterLabel: "Wet season",
    evidence: [
      "Observed difference follows expected seasonal vegetation variation",
      "No persistent construction footprint is supported",
      "Temporal evidence does not confirm physical structural change"
    ],
    quality: {
      "Cloud / Haze": "Low",
      "Seasonal Variation": "High confounder",
      "Shadow Effect": "Low",
      "Viewing Geometry": "Low",
      "Registration Error": "Low",
      "Sensor Inconsistency": "Low"
    },
    timeline: [
      ["Obs 01", "Dry"], ["Obs 02", "Dry"], ["Obs 03", "Transition"], ["Obs 04", "Wet"], ["Obs 05", "Wet"], ["Obs 06", "Transition"], ["Obs 07", "Dry"]
    ]
  },
  "SITE-D": {
    id: "SITE-D",
    title: "Quality-confounded candidate",
    type: "Possible change - insufficient evidence",
    confidence: 49,
    earliest: "Not supported due to quality/confounders",
    observations: 6,
    usable: 3,
    riverDistance: "Unknown",
    query: DEMO_PRIMARY_QUERY,
    beforeLabel: "Clear observation",
    afterLabel: "Hazy observation",
    evidence: [
      "Haze and radiometric inconsistency reduce comparability",
      "Change candidate is not persistent in usable observations",
      "System suppresses the candidate rather than reporting a physical change"
    ],
    quality: {
      "Cloud / Haze": "High confounder",
      "Seasonal Variation": "Medium",
      "Shadow Effect": "Medium",
      "Viewing Geometry": "Medium",
      "Registration Error": "Medium",
      "Sensor Inconsistency": "Medium"
    },
    timeline: [
      ["Obs 01", "Clear"], ["Obs 02", "Clear"], ["Obs 03", "Haze"], ["Obs 04", "Haze"], ["Obs 05", "Partial"], ["Obs 06", "Clear"]
    ]
  }
};

export const clusters = [
  { id: 1, name: "Construction-like", sites: 4, similarity: "High" },
  { id: 2, name: "Open-ground activity", sites: 3, similarity: "Medium" },
  { id: 3, name: "River-adjacent", sites: 3, similarity: "High" },
  { id: 4, name: "Seasonal / low-change", sites: 2, similarity: "Control" }
];

export const demoAssets = [
  { id:"A-01", site:"SITE-A", date:"Observation 01", sensor:"Optical", quality:"Usable", role:"Baseline" },
  { id:"A-02", site:"SITE-A", date:"Observation 02", sensor:"Optical", quality:"Usable", role:"No change" },
  { id:"A-03", site:"SITE-A", date:"Observation 03", sensor:"Optical", quality:"Usable", role:"No change" },
  { id:"A-04", site:"SITE-A", date:"Observation 04", sensor:"Optical", quality:"Usable", role:"Ground work" },
  { id:"A-05", site:"SITE-A", date:"Observation 05", sensor:"Optical", quality:"Usable", role:"First supported change" },
  { id:"A-06", site:"SITE-A", date:"Observation 06", sensor:"Optical", quality:"Usable", role:"Persistence" },
  { id:"A-07", site:"SITE-A", date:"Observation 07", sensor:"SAR", quality:"Usable", role:"Cross-check" },
  { id:"A-08", site:"SITE-A", date:"Observation 08", sensor:"Optical", quality:"Usable", role:"Expansion" },
  { id:"A-09", site:"SITE-A", date:"Observation 09", sensor:"Optical", quality:"Usable", role:"Persistence" },
  { id:"A-10", site:"SITE-A", date:"Observation 10", sensor:"Optical", quality:"Usable", role:"Latest" },
  ...Array.from({length:22}, (_,i)=>({ id:`D-${String(i+1).padStart(2,'0')}`, site:["SITE-B","SITE-C","SITE-D","SECONDARY"][i%4], date:`Observation ${i+1}`, sensor:i%3===0?"SAR":"Optical", quality:i%5===0?"Review":"Usable", role:["Similar","Control","Quality control","Secondary"][i%4] }))
];

export const system = {
  archiveItems: 32,
  sites: 4,
  queries: 2,
  mode: "DEMO MODE - LOCAL PRECOMPUTED ARCHIVE",
  network: "Disabled for demo",
  index: "Fixture index loaded",
  model: "No live inference connected",
};

export const reviewsSeed = [
  { id:"SITE-A", status:"Pending", type:"Construction (New)", rationale:"Ranked match + temporal persistence" },
  { id:"SITE-C", status:"Suppressed", type:"Seasonal variation", rationale:"Seasonality explains apparent visual difference" },
  { id:"SITE-D", status:"Needs Review", type:"Possible change", rationale:"Image-quality confounder" }
];
