// jummai-jobs worker
// Cron every 2h: fetch fresh Job Bank + UHN Ontario care/admin roles, compose
// jobs.json, and redeploy the static site (index.html + jobs.json + netlify.toml)
// to Netlify so the board always shows only recent (<12h) openings.
//
// Cloudflare's egress IPs are trusted by Job Bank (validated), unlike GitHub's.
//
// Secrets (wrangler secret put):
//   NETLIFY_TOKEN  Netlify deploy API token
//   NETLIFY_SITE_ID
//   SITE_ORIGIN    e.g. https://jummai-job-finder.netlify.app

const AGE_HOURS = 12;
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36";

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(run(env));
  },
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return new Response("jummai-jobs worker ok", { headers: { "content-type": "text/plain" } });
    }
    ctx.waitUntil(run(env)); // manual trigger for debugging
    return new Response("triggered", { headers: { "content-type": "text/plain" } });
  },
};

async function run(env) {
  const jobs = [];
  try { jobs.push(...await fetchJobBank()); } catch (e) { console.log("jobbank err", String(e)); }
  try { jobs.push(...await fetchUHN()); } catch (e) { console.log("uhn err", String(e)); }

  // freshness filter + region sort
  const now = Date.now();
  const fresh = jobs
    .filter(j => j.releasedDate ? (now - j.releasedTS) < AGE_HOURS * 3600e3 : true)
    .sort((a, b) => (b.releasedTS||0) - (a.releasedTS||0));

  console.log("composed jobs:", fresh.length);
  await deployToNetlify(env, fresh);
}

async function fetchJobBank() {
  const out = [];
  const seen = new Set();
  const queries = ["personal support worker", "health care aide", "caregiver",
                   "home support worker", "developmental service worker"];
  const UG = ["von canada","bayshore","cbi","se health","paramed","home instead","comfort keepers","nurse finder","sunrise senior living corporate","nurses next door","right at home","carepartners","we care home health"];
  const CARE = ["support worker","caregiver","care aide","care giver","psw","personal support"];
  const EXCLUDE = ["registered nurse","rn -","rpn","nurse practitioner","physician","intern"];
  for (const q of queries) {
    const url = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=" +
      encodeURIComponent(q) + "&locationstring=Ontario&sort=D&source=1";
    let html = "";
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const r = await fetch(url, { headers: { "user-agent": UA } });
        html = await r.text();
        break;
      } catch (e) { await sleep(3000 * (attempt + 1)); }
    }
    await sleep(4000);
    const re = /<article[^>]*>([\s\S]*?)<\/article>/g;
    let m;
    while ((m = re.exec(html))) {
      const a = m[1];
      const title = (a.match(/noctitle">\s*([^<]+)/) || [])[1];
      if (!title) continue;
      const t = title.trim().toLowerCase();
      if (!CARE.some(k => t.includes(k))) continue;
      if (EXCLUDE.some(k => t.includes(k))) continue;
      const emp = strip((a.match(/<li class="business">\s*([\s\S]*?)<\/li>/) || [])[1] || "Employer");
      if (UG.some(k => emp.toLowerCase().includes(k))) continue;
      const loc = strip((a.match(/<li class="location">[\s\S]*?<\/span>\s*([\s\S]*?)<\/li>/) || [])[1] || "Ontario");
      // Ontario-only (drop other provinces)
      const lc = loc.toLowerCase();
      const provCode = (lc.match(/\(([a-z]{2})\)\s*$/) || lc.match(/\(([a-z]{2})\)/) || [])[1];
      if (provCode && provCode !== "on") continue;
      const payRaw = (a.match(/<li class="salary">[\s\S]*?Salary\s*([\s\S]*?)<\/li>/) || [])[1];
      const pay = strip(payRaw || "See posting");
      const payMin = (pay.match(/\$(\d{2}(?:\.\d{1,2})?)/) || [])[1] ? parseFloat((pay.match(/\$(\d{2}(?:\.\d{1,2})?)/))[1]) : null;
      const dateRaw = strip((a.match(/<li class="date">\s*([\s\S]*?)<\/li>/) || [])[1] || "");
      let releasedTS = 0;
      let released = null;
      if (dateRaw) {
        const mm = dateRaw.match(/(\w{3,9})\s+(\d{1,2}),\s+(\d{4})/);
        if (mm) { released = `${mm[3]}-${mon(mm[1])}-${mm[2].padStart(2,"0")}`;
          releasedTS = Date.parse(released + "T13:00:00"); }
      }
      const linkm = (a.match(/href="([^"]*jobposting\/\d+[^"]*)"/) || [])[1];
      const link = linkm ? "https://www.jobbank.gc.ca" + unescape(linkm) : "";
      const key = t;
      if (seen.has(key)) continue;
      seen.add(key);
      // region
      let region = "unknown";
      if (/north york|willowdale|northcliffe|donalda|bayview/.test(lc)) region = "north-york";
      else if (/toronto|scarborough|etobicoke|mississauga|markham|richmond hill|vaughan|thornhill|brampton|ajax|pickering|whitby|oshawa/.test(lc)) region = "ttc-reachable";
      else if (/hamilton|burlington|oakville|milton|newmarket|aurora|barrie|guelph|kitchener|london|kingston|ottawa|quinte|belleville|timmins|north bay/.test(lc)) region = "other-ontario";
      out.push({
        e: emp, title: title.trim(), cat: "psw", remote_capable: false,
        tier: "ltco", loc, region, match: "direct", pay, payMin,
        type: "See posting", link,
        search: "https://www.google.com/search?q=" + encodeURIComponent(title.trim()),
        hl: ["Posted on Job Bank Canada"],
        req: title.trim() + " — apply via Job Bank.",
        live: true, releasedDate: released, releasedTS, closes: null,
      });
    }
  }
  return out;
}

async function fetchUHN() {
  const out = [];
  const url = "https://api.smartrecruiters.com/v1/companies/UniversityHealthNetwork/postings?limit=250";
  const r = await fetch(url, { headers: { "user-agent": UA } });
  const data = await r.json();
  const CARE = ["support worker","caregiver","care aide","health care aide","psw","personal support"];
  const OFFICE = ["coordinator","administrative assistant","clerical","clerk","records","program assistant","admin","resource","intake","scheduler","assistant"];
  const EXCLUDE = ["nurse","rpn","rn-","physician","intern","resident","technologist","pharmacist","therapist"];
  for (const c of (data.content || [])) {
    const name = (c.name || "").trim();
    const low = name.toLowerCase();
    if (EXCLUDE.some(k => low.includes(k))) continue;
    const isCare = CARE.some(k => low.includes(k));
    const isOffice = OFFICE.some(k => low.includes(k));
    if (!isCare && !isOffice) continue;
    const locObj = c.location || {};
    const loc = locObj.city || "Toronto";
    const addr = (locObj.address || "") + " " + (locObj.fullLocation || "");
    let region = "unknown";
    const ll = (addr + " " + loc).toLowerCase();
    if (/north york|emmett|wilson|donalda|willowdale/.test(ll)) region = "north-york";
    else if (/toronto|university|college|elizabeth|bathurst|dundas/.test(ll)) region = "ttc-reachable";
    const dated = c.releasedDate || "";
    const released = dated.slice(0, 10);
    const releasedTS = dated ? Date.parse(dated) : 0;
    const sections = c.sections || {};
    const desc = stripObj(sections.jobDescription) + " " + stripObj(sections.qualifications);
    const reqText = (desc || name).slice(0, 800);
    out.push({
      e: "University Health Network (UHN)", title: name,
      cat: isOffice ? "admin" : "psw",
      remote_capable: isOffice, tier: "hospital", loc, region,
      match: isOffice ? "adjacent" : "direct",
      pay: "See posting", payMin: null, type: "See posting",
      link: c.applyUrl || c.postingUrl || "",
      search: "https://www.google.com/search?q=" + encodeURIComponent(name),
      hl: [], req: reqText, live: true,
      releasedDate: released, releasedTS, closes: null,
    });
  }
  return out;
}

function stripObj(v) {
  return (v && v.text) ? String(v.text).replace(/<[^>]+>/g, " ") : "";
}
function strip(s) {
  return String(s || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}
function unescape(s) { return s.replace(/&amp;/g, "&"); }
function mon(m) { const map = {jan:"01",feb:"02",mar:"03",apr:"04",may:"05",jun:"06",jul:"07",aug:"08",sep:"09",oct:"10",nov:"11",dec:"12"}; return map[(m||"").toLowerCase().slice(0,3)] || "01"; }
function sleep(ms) { return new Promise(res => setTimeout(res, ms)); }

// ---- Netlify deploy: fetch current index.html, zip with fresh jobs.json, deploy ----
async function deployToNetlify(env, jobs) {
  const origin = env.SITE_ORIGIN || "https://jummai-job-finder.netlify.app";
  const jobsJson = JSON.stringify(jobs);
  // fetch the live index.html + netlify.toml so we don't have to embed the whole site
  const indexRes = await fetch(origin + "/index.html", { headers: { "user-agent": UA } });
  const indexHtml = await indexRes.text();
  const tomlRes = await fetch(origin + "/netlify.toml", { headers: { "user-agent": UA } });
  const toml = tomlRes.ok ? await tomlRes.text() : "[build]\n  publish = \".\"\n";

  const zip = makeZip({
    "index.html": indexHtml,
    "jobs.json": jobsJson,
    "netlify.toml": toml,
  });

  const resp = await fetch("https://api.netlify.com/api/v1/sites/" + env.NETLIFY_SITE_ID + "/deploys", {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + env.NETLIFY_TOKEN,
      "Content-Type": "application/zip",
    },
    body: zip,
  });
  const body = await resp.text();
  console.log("netlify deploy status", resp.status, "state", (body.slice(0, 300)));
}

// Minimal ZIP writer (stored, no compression) with CRC32
function makeZip(files) {
  const crcTable = makeCrcTable();
  let localParts = [];
  let centralParts = [];
  let offset = 0;
  const names = Object.keys(files);
  for (const name of names) {
    const data = new TextEncoder().encode(files[name]);
    const nameBytes = new TextEncoder().encode(name);
    const crc = crc32(data, crcTable);
    const fields = [
      le32(0x04034b50), // local file header signature
      le16(20), // version needed
      le16(0), // flags
      le16(0), // method stored
      le16(0), le16(0), // time/date
      le32(crc), le32(data.length), le32(data.length),
      le16(nameBytes.length), le16(0),
    ];
    const localHeader = concat(fields, nameBytes, data);
    localParts.push(localHeader);
    centralParts.push(
      concat([le32(0x02014b50), le16(20), le16(20), le16(0), le16(0),
        le16(0), le16(0), le32(crc), le32(data.length), le32(data.length),
        le16(nameBytes.length), le16(0), le16(0), le16(0), le16(0), le32(0), le32(offset)], nameBytes)
    );
    offset += localHeader.length;
  }
  const central = concat(...centralParts);
  const endRecord = concat([le32(0x06054b50), le16(0), le16(0),
    le16(names.length), le16(names.length), le32(central.length), le32(offset), le16(0)]);
  const allBytes = concat(...localParts, central, endRecord);
  return new Blob([allBytes], { type: "application/zip" });
}
function makeCrcTable() { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) { c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1); } t[n] = c >>> 0; } return t; }
function crc32(data, table) { let c = 0xFFFFFFFF; for (const b of data) { c = table[(c ^ b) & 0xFF] ^ (c >>> 8); } return (c ^ 0xFFFFFFFF) >>> 0; }
function le16(v) { return new Uint8Array([v & 255, (v >>> 8) & 255]); }
function le32(v) { return new Uint8Array([v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255]); }
function concat(...parts) {
  const all = [];
  const pushBytes = (p) => {
    if (p instanceof Uint8Array) { all.push(...Array.from(p)); }
    else if (p instanceof Array) { p.forEach(pushBytes); }
    else { all.push(...Array.from(new TextEncoder().encode(p))); }
  };
  for (const p of parts) pushBytes(p);
  return new Uint8Array(all);
}
