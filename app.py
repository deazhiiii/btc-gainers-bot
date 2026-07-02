import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=btc"
    "&order=market_cap_desc"
    "&per_page=250"
    "&page=1"
    "&price_change_percentage=1h,24h,7d"
    "&sparkline=false"
)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BTC Gainers Scanner</title>
<style>
:root{
  --bg:#0d0d0f;--surface:#161618;--surface2:#1e1e21;--surface3:#252528;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.13);
  --text:#e8e8ea;--muted:#888890;--faint:#444448;
  --green:#4ade80;--green-bg:rgba(74,222,128,0.10);--green-b:rgba(74,222,128,0.28);
  --red:#f87171;--red-bg:rgba(248,113,113,0.10);--red-b:rgba(248,113,113,0.28);
  --amber:#fbbf24;--amber-bg:rgba(251,191,36,0.10);--amber-b:rgba(251,191,36,0.25);
  --blue:#60a5fa;--blue-bg:rgba(96,165,250,0.10);--blue-b:rgba(96,165,250,0.28);
  --font:'JetBrains Mono','Fira Code','Cascadia Code',monospace;--r:6px;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:13px;min-height:100vh;}
.topbar{background:var(--surface);border-bottom:1px solid var(--border);padding:10px 20px;
  display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:20;}
.logo{font-size:14px;font-weight:700;letter-spacing:.08em;}
.logo em{color:var(--amber);font-style:normal;}
.live-pill{display:flex;align-items:center;gap:6px;background:var(--green-bg);
  border:1px solid var(--green-b);border-radius:20px;padding:3px 10px;}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.live-label{font-size:10px;color:var(--green);letter-spacing:.06em;}
.updated{font-size:11px;color:var(--muted);}
.wrap{max-width:1300px;margin:0 auto;padding:16px 20px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:14px;}
.sc{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:10px 14px;}
.sl{font-size:10px;color:var(--muted);letter-spacing:.09em;text-transform:uppercase;margin-bottom:3px;}
.sv{font-size:20px;font-weight:700;}
.g{color:var(--green);}.r{color:var(--red);}.a{color:var(--amber);}.b{color:var(--blue);}
.toolbar{display:flex;gap:6px;align-items:center;margin-bottom:10px;flex-wrap:wrap;}
.sep{width:1px;height:20px;background:var(--border2);margin:0 4px;}
.lbl{font-size:10px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;}
.btn{background:transparent;border:1px solid var(--border2);color:var(--muted);
  font-family:var(--font);font-size:11px;padding:5px 11px;border-radius:var(--r);
  cursor:pointer;transition:all .15s;white-space:nowrap;}
.btn:hover{background:var(--surface2);color:var(--text);}
.btn.ag{background:var(--green-bg);color:var(--green);border-color:var(--green-b);}
.btn.aa{background:var(--amber-bg);color:var(--amber);border-color:var(--amber-b);}
.btn.ab{background:var(--blue-bg);color:var(--blue);border-color:var(--blue-b);}
.btn.ar{background:var(--red-bg);color:var(--red);border-color:var(--red-b);}
.thr{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;
  background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:8px 14px;}
.thr label{font-size:11px;color:var(--muted);}
#thV{color:var(--green);font-weight:700;min-width:36px;display:inline-block;}
input[type=range]{accent-color:var(--green);width:130px;cursor:pointer;}
.sw{margin-left:auto;}
#srch{background:var(--surface);border:1px solid var(--border);color:var(--text);
  font-family:var(--font);font-size:12px;padding:5px 12px;border-radius:var(--r);
  outline:none;width:170px;}
#srch:focus{border-color:var(--border2);}
#srch::placeholder{color:var(--faint);}
#wBar{background:var(--surface);border:1px solid var(--amber-b);border-radius:var(--r);
  padding:8px 14px;margin-bottom:10px;display:none;flex-wrap:wrap;gap:6px;align-items:center;}
.wl{font-size:10px;color:var(--amber);letter-spacing:.08em;text-transform:uppercase;margin-right:4px;}
.wc{background:var(--surface2);border:1px solid var(--border2);border-radius:4px;
  padding:3px 8px;font-size:11px;color:var(--text);cursor:pointer;display:inline-flex;align-items:center;gap:5px;}
.wc:hover{border-color:var(--amber-b);color:var(--amber);}
.tw{border:1px solid var(--border);border-radius:10px;overflow:hidden;}
table{width:100%;border-collapse:collapse;}
thead tr{background:var(--surface);}
th{padding:8px 10px;text-align:left;font-size:10px;color:var(--muted);font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;border-bottom:1px solid var(--border);white-space:nowrap;}
th.tr2,td.tr2{text-align:right;}th.tc,td.tc{text-align:center;}
tbody tr{border-bottom:1px solid var(--border);transition:background .1s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:var(--surface2);}
tbody tr.pinned{background:rgba(251,191,36,.04);border-left:2px solid var(--amber);}
td{padding:6px 10px;vertical-align:middle;white-space:nowrap;}
.rank{color:var(--faint);font-size:11px;}
.star{background:none;border:none;cursor:pointer;font-size:14px;padding:0 2px;color:var(--faint);transition:color .15s;}
.star.on,.star:hover{color:var(--amber);}
.cc{display:flex;align-items:center;gap:8px;}
.ci{width:22px;height:22px;border-radius:50%;flex-shrink:0;}
.csym{font-weight:700;font-size:12px;color:var(--blue);cursor:pointer;
  text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s;}
.csym:hover{border-bottom-color:var(--blue);}
.cname{font-size:10px;color:var(--muted);}
.price{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;}
.pct{font-weight:600;font-variant-numeric:tabular-nums;font-size:12px;}
.pct.pos{color:var(--green);}.pct.neg{color:var(--red);}.pct.neu{color:var(--muted);}
.bw{display:flex;align-items:center;gap:6px;justify-content:flex-end;}
.bb{width:55px;height:5px;background:var(--surface3);border-radius:3px;overflow:hidden;}
.bf{height:100%;border-radius:3px;transition:width .4s;}
.bfp{background:var(--green);}.bfn{background:var(--red);}
.sig{display:inline-block;font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700;letter-spacing:.05em;}
.sig.BUY{background:var(--green-bg);color:var(--green);border:1px solid var(--green-b);}
.sig.SELL{background:var(--red-bg);color:var(--red);border:1px solid var(--red-b);}
.sig.HOLD{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-b);}
.acts{display:flex;gap:4px;justify-content:flex-end;}
.act{background:var(--surface2);border:1px solid var(--border);color:var(--muted);
  font-family:var(--font);font-size:10px;padding:3px 7px;border-radius:4px;
  cursor:pointer;text-decoration:none;transition:all .12s;white-space:nowrap;}
.act:hover{background:var(--surface3);color:var(--text);}
.act.tv{border-color:var(--blue-b);color:var(--blue);}.act.tv:hover{background:var(--blue-bg);}
.act.bnb{border-color:var(--amber-b);color:var(--amber);}.act.bnb:hover{background:var(--amber-bg);}
.act.cp.done{border-color:var(--green-b);color:var(--green);}
#toast{position:fixed;bottom:20px;right:20px;background:var(--surface2);border:1px solid var(--green-b);
  color:var(--green);font-size:12px;padding:8px 16px;border-radius:var(--r);
  opacity:0;pointer-events:none;transition:opacity .2s;z-index:100;}
#toast.show{opacity:1;}
.footer{font-size:11px;color:var(--muted);margin-top:10px;display:flex;gap:16px;flex-wrap:wrap;}
.footer b{color:var(--text);}
.empty,.errmsg{text-align:center;padding:3rem;color:var(--muted);}
.errmsg{color:var(--red);}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">BTC<em>/</em>GAINERS <span style="font-size:11px;font-weight:400;color:var(--muted)">scanner</span></div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div class="live-pill"><div class="live-dot"></div><span class="live-label">LIVE</span></div>
    <div class="updated" id="upd">connecting…</div>
  </div>
</div>

<div class="wrap">
  <div class="stats" id="stats">
    <div class="sc"><div class="sl">Loading</div><div class="sv a">—</div></div>
  </div>

  <div class="toolbar">
    <span class="lbl">Timeframe</span>
    <button class="btn ag" id="tf-1h"  onclick="setTf('1h',this)">1H</button>
    <button class="btn"    id="tf-24h" onclick="setTf('24h',this)">24H</button>
    <button class="btn"    id="tf-7d"  onclick="setTf('7d',this)">7D</button>
    <div class="sep"></div>
    <span class="lbl">Show</span>
    <button class="btn ab" id="v-gainers" onclick="setView('gainers',this)">&#8593; Gainers</button>
    <button class="btn"    id="v-all"     onclick="setView('all',this)">All</button>
    <button class="btn"    id="v-losers"  onclick="setView('losers',this)">&#8595; Losers</button>
    <button class="btn"    id="v-watch"   onclick="setView('watchlist',this)">&#9733; Watchlist</button>
    <div class="sep"></div>
    <span class="lbl">Sort</span>
    <button class="btn ag" id="s-perf" onclick="setSort('perf',this)">Performance</button>
    <button class="btn"    id="s-mcap" onclick="setSort('mcap',this)">Market Cap</button>
    <div class="sep"></div>
    <span class="lbl">Market</span>
    <button class="btn ag" id="m-perp" onclick="setMkt('perp',this)">Perp (.P)</button>
    <button class="btn"    id="m-spot" onclick="setMkt('spot',this)">Spot</button>
  </div>

  <div class="thr">
    <span class="lbl">Min gain:</span>
    <input type="range" id="thr" min="0" max="20" step="0.5" value="0" oninput="setThr(this.value)">
    <span id="thV">0%</span>
    <div class="sw"><input id="srch" placeholder="Search coin…" oninput="renderTable()"></div>
  </div>

  <div id="wBar"><span class="wl">&#9733; Watching</span><span id="wChips"></span></div>

  <div class="tw">
    <table>
      <thead>
        <tr>
          <th style="width:28px"></th>
          <th style="width:32px">#</th>
          <th>Coin</th>
          <th class="tr2">Price (BTC)</th>
          <th class="tr2">1H %</th>
          <th class="tr2">24H %</th>
          <th class="tr2">7D %</th>
          <th class="tr2">Strength</th>
          <th class="tc">Signal</th>
          <th class="tr2">Actions</th>
        </tr>
      </thead>
      <tbody id="tbody">
        <tr><td colspan="10" class="empty">Fetching live BTC data…</td></tr>
      </tbody>
    </table>
  </div>

  <div class="footer">
    <span>Source: <b>CoinGecko</b></span>
    <span>Base: <b>BTC</b></span>
    <span id="fc">—</span>
    <span>Refresh: <b>60s</b></span>
    <span>Click <b>symbol</b> or <b>TV</b> to open TradingView chart &nbsp;|&nbsp;
          &#9733; watchlist &nbsp;|&nbsp; &#128203; copy pair</span>
  </div>
</div>
<div id="toast">Copied!</div>

<script>
var coins=[], tf='1h', view='gainers', srt='perf', mkt='perp', minG=0;
var wl=JSON.parse(localStorage.getItem('btcw')||'[]');

function ch(c,t){
  if(t==='1h')  return c.price_change_percentage_1h_in_currency||0;
  if(t==='24h') return c.price_change_percentage_24h_in_currency||0;
  return c.price_change_percentage_7d_in_currency||0;
}
function fp(v){if(!v)return'—';if(v<1e-8)return v.toExponential(2);if(v<0.0001)return v.toFixed(8);return v.toFixed(6);}
function pf(v){if(v===null||v===undefined)return'—';return(v>=0?'+':'')+v.toFixed(2)+'%';}
function pc(v){return v>0?'pos':v<0?'neg':'neu';}
function sig(c){var s=[ch(c,'1h'),ch(c,'24h'),ch(c,'7d')];var p=s.filter(function(x){return x>0;}).length;return p>=2?'BUY':p===0?'SELL':'HOLD';}
function tvUrl(sym){var p=sym.toUpperCase()+'USDT';return mkt==='perp'?'https://www.tradingview.com/chart/?symbol=BINANCE:'+p+'.P':'https://www.tradingview.com/chart/?symbol=BINANCE:'+p;}
function bnbUrl(sym){var p=sym.toUpperCase()+'USDT';return mkt==='perp'?'https://www.binance.com/en/futures/'+p:'https://www.binance.com/en/trade/'+p+'?type=spot';}
function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(function(){t.classList.remove('show');},1500);}
function copyPair(sym,el){var p=sym.toUpperCase()+'USDT'+(mkt==='perp'?'.P':'');navigator.clipboard.writeText(p).then(function(){el.textContent='Copied!';el.classList.add('done');toast('Copied: '+p);setTimeout(function(){el.textContent='Copy';el.classList.remove('done');},1500);});}
function toggleW(sym){var i=wl.indexOf(sym);if(i===-1)wl.push(sym);else wl.splice(i,1);localStorage.setItem('btcw',JSON.stringify(wl));updateWBar();renderTable();}
function rmW(s){wl=wl.filter(function(x){return x!==s;});localStorage.setItem('btcw',JSON.stringify(wl));updateWBar();renderTable();}
function updateWBar(){var bar=document.getElementById('wBar');var ch2=document.getElementById('wChips');if(!wl.length){bar.style.display='none';return;}bar.style.display='flex';ch2.innerHTML=wl.map(function(s){return'<span class="wc" onclick="rmW(\''+s+'\')">'+s+' &#x2715;</span>';}).join('');}
function clrTool(ids,active,cls){ids.forEach(function(id){document.getElementById(id).className='btn';});active.className='btn '+cls;}
function setTf(t,b){tf=t;clrTool(['tf-1h','tf-24h','tf-7d'],b,'ag');renderTable();}
function setView(v,b){view=v;clrTool(['v-gainers','v-all','v-losers','v-watch'],b,'ab');renderTable();}
function setSort(s,b){srt=s;clrTool(['s-perf','s-mcap'],b,'aa');renderTable();}
function setMkt(m,b){mkt=m;clrTool(['m-perp','m-spot'],b,'ag');renderTable();}
function setThr(v){minG=parseFloat(v);document.getElementById('thV').textContent=v+'%';renderTable();}

function getPerformanceSet(){
  var q=document.getElementById('srch').value.toUpperCase().trim();
  var set=coins.filter(function(c){return !q||c.symbol.toUpperCase().includes(q)||c.name.toUpperCase().includes(q);});
  if(view==='watchlist') set=set.filter(function(c){return wl.includes(c.symbol.toUpperCase());});
  else if(view==='gainers') set=set.filter(function(c){return ch(c,tf)>=minG;});
  else if(view==='losers')  set=set.filter(function(c){return ch(c,tf)<=-minG;});
  else if(minG>0) set=set.filter(function(c){return Math.abs(ch(c,tf))>=minG;});

  set.sort(function(a,b){return view==='losers'?ch(a,tf)-ch(b,tf):ch(b,tf)-ch(a,tf);});
  if(view!=='watchlist') set=set.slice(0,80);
  return set;
}

function renderTable(){
  if(!coins.length)return;

  var list=getPerformanceSet();

  if(srt==='mcap'){
    list=list.slice().sort(function(a,b){return (a.market_cap_rank||999)-(b.market_cap_rank||999);});
  }

  var maxA=Math.max.apply(null,list.map(function(c){return Math.abs(ch(c,tf));}));
  if(maxA<0.01)maxA=0.01;
  var html='';
  list.forEach(function(c,i){
    var h1=ch(c,'1h'),h24=ch(c,'24h'),h7=ch(c,'7d'),main=ch(c,tf);
    var bw=(Math.min(100,(Math.abs(main)/maxA)*100)).toFixed(1);
    var sg=sig(c);
    var sym=c.symbol.toUpperCase();
    var iw=wl.includes(sym);
    html+='<tr class="'+(iw?'pinned':'')+'">'
      +'<td class="tc"><button class="star '+(iw?'on':'')+'" onclick="toggleW(\''+sym+'\')" title="Watchlist">'+(iw?'&#9733;':'&#9734;')+'</button></td>'
      +'<td class="rank">'+(i+1)+'</td>'
      +'<td><div class="cc"><img class="ci" src="'+c.image+'" alt="" onerror="this.style.display=\'none\'" loading="lazy">'
        +'<div><a class="csym" href="'+tvUrl(c.symbol)+'" target="_blank" title="Open on TradingView: '+sym+'USDT'+(mkt==='perp'?'.P':'')+'">'
        +sym+'</a><div class="cname">'+c.name+'</div></div></div></td>'
      +'<td class="tr2 price">'+fp(c.current_price)+'</td>'
      +'<td class="tr2 pct '+pc(h1)+'">'+pf(h1)+'</td>'
      +'<td class="tr2 pct '+pc(h24)+'">'+pf(h24)+'</td>'
      +'<td class="tr2 pct '+pc(h7)+'">'+pf(h7)+'</td>'
      +'<td class="tr2"><div class="bw"><span class="pct '+pc(main)+'" style="font-size:11px">'+pf(main)+'</span>'
        +'<div class="bb"><div class="bf '+(main>=0?'bfp':'bfn')+'" style="width:'+bw+'%"></div></div></div></td>'
      +'<td class="tc"><span class="sig '+sg+'">'+sg+'</span></td>'
      +'<td class="tr2"><div class="acts">'
        +'<a class="act tv" href="'+tvUrl(c.symbol)+'" target="_blank" title="TradingView chart">&#128200; TV</a>'
        +'<a class="act bnb" href="'+bnbUrl(c.symbol)+'" target="_blank" title="Trade on Binance">&#8383; BNB</a>'
        +'<button class="act cp" onclick="copyPair(\''+c.symbol+'\',this)" title="Copy pair">Copy</button>'
        +'</div></td>'
      +'</tr>';
  });
  document.getElementById('tbody').innerHTML=html||'<tr><td colspan="10" class="empty">No coins match.</td></tr>';
  var g=coins.filter(function(c){return ch(c,'24h')>0;}).length;
  var l=coins.filter(function(c){return ch(c,'24h')<0;}).length;
  var top=coins.slice().sort(function(a,b){return ch(b,'24h')-ch(a,'24h');})[0];
  var topP=top?ch(top,'24h').toFixed(2):'—';
  var topS=top?top.symbol.toUpperCase():'—';
  document.getElementById('stats').innerHTML=
    '<div class="sc"><div class="sl">Gaining vs BTC 24h</div><div class="sv g">'+g+'</div></div>'
    +'<div class="sc"><div class="sl">Losing vs BTC 24h</div><div class="sv r">'+l+'</div></div>'
    +'<div class="sc"><div class="sl">Top Gainer 24h</div><div class="sv g">+'+topP+'%</div></div>'
    +'<div class="sc"><div class="sl">Leader Symbol</div><div class="sv b">'+topS+'</div></div>'
    +'<div class="sc"><div class="sl">Watchlist</div><div class="sv a">'+wl.length+' coins</div></div>'
    +'<div class="sc"><div class="sl">Total Tracked</div><div class="sv">'+coins.length+'</div></div>';
  document.getElementById('fc').innerHTML='Showing: <b>'+list.length+'</b>';
}

async function loadData(){
  try{
    var res=await fetch('/api/coins');
    var data=await res.json();
    if(data.error)throw new Error(data.error);
    coins=data;
    renderTable();
    updateWBar();
    document.getElementById('upd').textContent='updated '+new Date().toLocaleTimeString();
  }catch(e){
    document.getElementById('tbody').innerHTML='<tr><td colspan="10" class="errmsg">Error: '+e.message+'<br><small>Rate-limited? Retrying in 60s</small></td></tr>';
    document.getElementById('upd').textContent='error — retrying…';
  }
}
updateWBar();
loadData();
setInterval(loadData,60000);
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/coins")
def api_coins():
    try:
        resp = requests.get(COINGECKO_URL, timeout=15,
                            headers={"User-Agent": "btc-gainers-scanner/1.0"})
        resp.raise_for_status()
        data = resp.json()
        filtered = [c for c in data if c.get("symbol", "").lower() != "btc"]
        return jsonify(filtered)
    except requests.exceptions.Timeout:
        return jsonify({"error": "CoinGecko timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected: " + str(e)}), 500


if __name__ == "__main__":
    # Render (and most hosts) assign the port dynamically via the PORT
    # environment variable. Falls back to 5002 for local testing.
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
