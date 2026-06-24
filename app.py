import time
import streamlit as st
from agents import build_read_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(page_title="research.exec()", page_icon="◆", layout="wide")

# ----------------------------------------------------------------------------
# Design system: "signal circuit" — each stage is a node with its own
# wavelength. A pulse of light travels the rail as data moves downstream.
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#07090a;
  --panel:#0e1213;
  --panel-2:#10141a;
  --line:#202726;
  --line-bright:#34403d;
  --text:#dcdecd;
  --muted:#697370;

  --c-search:#4dd9ff;
  --c-search-soft:#0f2a33;
  --c-read:#b18bff;
  --c-read-soft:#241b3d;
  --c-write:#ffb13c;
  --c-write-soft:#3d2c10;
  --c-critique:#ff6b81;
  --c-critique-soft:#3d1620;

  --ok:#5fe39a;
  --red:#ff5c5c;
}

html, body, [class*="css"]{ font-family:'Inter', sans-serif; }

.stApp{
  background:
    radial-gradient(circle at 15% 0%, rgba(77,217,255,0.05), transparent 38%),
    radial-gradient(circle at 85% 15%, rgba(255,177,60,0.05), transparent 40%),
    linear-gradient(rgba(7,9,10,0.94), rgba(7,9,10,0.98)),
    repeating-linear-gradient(0deg, transparent 0 27px, var(--line) 27px 28px),
    repeating-linear-gradient(90deg, transparent 0 27px, var(--line) 27px 28px);
  background-size: 100% 100%, 100% 100%, 100% 100%, 28px 28px, 28px 28px;
  color:var(--text);
}
#MainMenu, header, footer{visibility:hidden;}

@keyframes fadeUp{ from{ opacity:0; transform:translateY(10px);} to{ opacity:1; transform:translateY(0);} }
@keyframes sweep { 0%{ transform:translateY(-100%); } 100%{ transform:translateY(100vh); } }
.scanline{
  position:fixed; left:0; right:0; height:140px; top:0; z-index:9999;
  background:linear-gradient(to bottom, transparent, rgba(255,177,60,0.03), transparent);
  animation:sweep 8s linear infinite;
  pointer-events:none;
}

.hud-bar{
  display:flex; justify-content:space-between; align-items:baseline;
  font-family:'IBM Plex Mono', monospace; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase;
  color:var(--muted); border-bottom:1px solid var(--line); padding-bottom:0.6rem; margin-bottom:1.4rem;
  animation:fadeUp 0.5s ease both;
}
.hud-bar span.live{ color:var(--ok); }
.hud-dot{ display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--ok); margin-right:6px;
  box-shadow:0 0 6px var(--ok); animation:blink 1.6s ease-in-out infinite; }
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:0.25;} }

.rig-hero{ padding:0.4rem 0 1.8rem 0; margin-bottom:1.6rem; border-bottom:1px solid var(--line); }
.rig-eyebrow{
  font-family:'IBM Plex Mono', monospace; color:#ffb13c; font-size:0.78rem; letter-spacing:0.2em;
  text-transform:uppercase; margin-bottom:0.7rem; animation:fadeUp 0.5s ease 0.05s both;
}
.rig-title{
  font-family:'IBM Plex Mono', monospace; font-weight:700; font-size:3rem; letter-spacing:-0.02em;
  color:var(--text); margin:0; line-height:1; text-shadow:0 0 22px rgba(255,177,60,0.15);
  animation:fadeUp 0.5s ease 0.1s both;
}
.rig-title .blink-cursor{ display:inline-block; width:0.5ch; background:#ffb13c; margin-left:4px;
  animation:cursorblink 1.1s steps(1) infinite; }
@keyframes cursorblink{ 0%,49%{opacity:1;} 50%,100%{opacity:0;} }
.rig-sub{ color:var(--muted); font-size:0.95rem; margin-top:0.7rem; max-width:600px; line-height:1.5;
  animation:fadeUp 0.5s ease 0.15s both; }

/* ---- Circuit rail ---- */
.rail{ position:relative; display:flex; flex-direction:column; margin-left:14px; }
.rail::before{
  content:''; position:absolute; left:0; top:8px; bottom:8px; width:1px; background:var(--line);
}
.rail.flowing::after{
  content:''; position:absolute; left:-2px; top:0; width:5px; height:5px; border-radius:50%;
  background:#fff; box-shadow:0 0 10px 2px #fff;
  animation:travel 2.2s ease-in-out infinite;
}
@keyframes travel{
  0%{ top:0; opacity:0; }
  8%{ opacity:1; }
  92%{ opacity:1; }
  100%{ top:100%; opacity:0; }
}
.rail-node{ position:relative; padding:0 0 0 28px; }
.rail-dot{
  position:absolute; left:-7px; top:6px; width:13px; height:13px; border-radius:50%;
  background:var(--bg); border:2px solid var(--line); transition:all 0.3s ease; z-index:2;
}
.rail-dot.active.s-search{ border-color:var(--c-search); background:var(--c-search); animation:glow-search 1.5s ease-out infinite; }
.rail-dot.active.s-read{ border-color:var(--c-read); background:var(--c-read); animation:glow-read 1.5s ease-out infinite; }
.rail-dot.active.s-write{ border-color:var(--c-write); background:var(--c-write); animation:glow-write 1.5s ease-out infinite; }
.rail-dot.active.s-critique{ border-color:var(--c-critique); background:var(--c-critique); animation:glow-critique 1.5s ease-out infinite; }
@keyframes glow-search{ 0%{box-shadow:0 0 0 0 rgba(77,217,255,0.55);} 70%{box-shadow:0 0 0 9px rgba(77,217,255,0);} 100%{box-shadow:0 0 0 0 rgba(77,217,255,0);} }
@keyframes glow-read{ 0%{box-shadow:0 0 0 0 rgba(177,139,255,0.55);} 70%{box-shadow:0 0 0 9px rgba(177,139,255,0);} 100%{box-shadow:0 0 0 0 rgba(177,139,255,0);} }
@keyframes glow-write{ 0%{box-shadow:0 0 0 0 rgba(255,177,60,0.55);} 70%{box-shadow:0 0 0 9px rgba(255,177,60,0);} 100%{box-shadow:0 0 0 0 rgba(255,177,60,0);} }
@keyframes glow-critique{ 0%{box-shadow:0 0 0 0 rgba(255,107,129,0.55);} 70%{box-shadow:0 0 0 9px rgba(255,107,129,0);} 100%{box-shadow:0 0 0 0 rgba(255,107,129,0);} }
.rail-dot.done{ border-color:var(--ok); background:var(--ok); }

/* ---- Panel with HUD corner brackets ---- */
.panel{
  background:linear-gradient(180deg, var(--panel), var(--panel-2));
  border:1px solid var(--line); border-radius:2px; padding:1.15rem 1.35rem; margin-bottom:1.1rem;
  position:relative; animation:fadeUp 0.35s ease both;
}
.panel::before, .panel::after,
.panel .corner-br, .panel .corner-bl{
  content:''; position:absolute; width:10px; height:10px; opacity:0.7;
}
.panel::before{ top:-1px; left:-1px; border-top:2px solid var(--accent-c); border-left:2px solid var(--accent-c); }
.panel::after{ top:-1px; right:-1px; border-top:2px solid var(--accent-c); border-right:2px solid var(--accent-c); }
.panel.s-search{ --accent-c:var(--c-search); }
.panel.s-read{ --accent-c:var(--c-read); }
.panel.s-write{ --accent-c:var(--c-write); }
.panel.s-critique{ --accent-c:var(--c-critique); }
.panel.idle::before, .panel.idle::after{ border-color:var(--line-bright); opacity:0.5; }
.panel.active{ box-shadow:0 0 26px -10px var(--accent-c); }

.panel-top{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.55rem; }
.panel-label{ font-family:'IBM Plex Mono', monospace; font-size:0.74rem; letter-spacing:0.13em; text-transform:uppercase; color:var(--muted); }
.panel-label.active.s-search{ color:var(--c-search); }
.panel-label.active.s-read{ color:var(--c-read); }
.panel-label.active.s-write{ color:var(--c-write); }
.panel-label.active.s-critique{ color:var(--c-critique); }
.panel-label.done{ color:var(--ok); }
.panel-time{ font-family:'IBM Plex Mono', monospace; font-size:0.7rem; color:var(--muted); }
.panel-body{ font-size:0.92rem; line-height:1.6; color:var(--text); white-space:pre-wrap; }

.stTextInput input{
  background:var(--panel) !important; border:1px solid var(--line) !important; color:var(--text) !important;
  font-family:'IBM Plex Mono', monospace !important; border-radius:2px !important; padding:0.75rem 0.95rem !important;
}
.stTextInput input:focus{ border-color:#ffb13c !important; box-shadow:0 0 0 1px #ffb13c !important; }
.stTextInput label{
  font-family:'IBM Plex Mono', monospace; font-size:0.75rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted) !important;
}
.stButton button, .stFormSubmitButton button{
  background:#ffb13c !important; color:#1a1206 !important; border:none !important;
  font-family:'IBM Plex Mono', monospace !important; font-weight:600 !important; letter-spacing:0.08em !important;
  text-transform:uppercase !important; font-size:0.82rem !important; border-radius:2px !important;
  padding:0.75rem 1rem !important; transition:all 0.15s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover{ opacity:0.9; box-shadow:0 0 18px -2px #ffb13c; }

.stTabs [data-baseweb="tab-list"]{ gap:0; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{
  font-family:'IBM Plex Mono', monospace; font-size:0.78rem; letter-spacing:0.09em; text-transform:uppercase; color:var(--muted);
}
.stTabs [aria-selected="true"]{ color:#ffb13c !important; border-bottom-color:#ffb13c !important; }

.status-tag{
  display:inline-block; font-family:'IBM Plex Mono', monospace; font-size:0.68rem; letter-spacing:0.1em;
  padding:0.15rem 0.55rem; border:1px solid var(--line); border-radius:2px; color:var(--muted);
}
.status-tag.ok{ color:var(--ok); border-color:var(--ok); background:rgba(95,227,154,0.08); }
.status-tag.s-search{ color:var(--c-search); border-color:var(--c-search); background:var(--c-search-soft); }
.status-tag.s-read{ color:var(--c-read); border-color:var(--c-read); background:var(--c-read-soft); }
.status-tag.s-write{ color:var(--c-write); border-color:var(--c-write); background:var(--c-write-soft); }
.status-tag.s-critique{ color:var(--c-critique); border-color:var(--c-critique); background:var(--c-critique-soft); }

hr{ border-color:var(--line) !important; }
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hud-bar">'
    '<span><span class="hud-dot"></span><span class="live">SYSTEM ONLINE</span> · multi-agent rig v2</span>'
    '<span>MODE: SEARCH · READ · WRITE · CRITIQUE</span>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="rig-hero">'
    '<div class="rig-eyebrow">Autonomous Research Rig — 4-stage pipeline</div>'
    '<div class="rig-title">research.exec()<span class="blink-cursor">&nbsp;</span></div>'
    '<div class="rig-sub">Four agents, one chain of custody: a topic goes in, a reviewed report comes out. '
    'Watch the signal travel the rail as each stage hands its output downstream.</div>'
    '</div>',
    unsafe_allow_html=True
)

if "state" not in st.session_state:
    st.session_state.state = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = {}

STAGES = ["search", "read", "write", "critique"]
STAGE_LABELS = {
    "search": "01 · SEARCH AGENT — gathering sources",
    "read": "02 · READER AGENT — scraping deep content",
    "write": "03 · WRITER CHAIN — drafting the report",
    "critique": "04 · CRITIC CHAIN — reviewing the draft",
}
STAGE_CLASS = {"search": "s-search", "read": "s-read", "write": "s-write", "critique": "s-critique"}

left, right = st.columns([1, 2.2], gap="large")

with left:
    with st.form("research_form"):
        topic = st.text_input("Topic", placeholder="e.g. impact of AI on renewable energy")
        submitted = st.form_submit_button("Run pipeline", use_container_width=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    if not submitted and st.session_state.state is None:
        rail_html = "<div class='rail'>"
        for s in STAGES:
            rail_html += (
                '<div class="rail-node" style="margin-bottom:1.4rem;">'
                '<div class="rail-dot"></div>'
                f'<div class="panel-label">{STAGE_LABELS[s]}</div>'
                '</div>'
            )
        rail_html += "</div>"
        st.markdown(rail_html, unsafe_allow_html=True)
    elif st.session_state.state:
        rail_html = "<div class='rail'>"
        for s in STAGES:
            t = st.session_state.elapsed.get(s, "")
            rail_html += (
                '<div class="rail-node" style="margin-bottom:1.1rem;">'
                '<div class="rail-dot done"></div>'
                f'<div class="panel-label done">{STAGE_LABELS[s]}</div>'
                f'<div class="panel-time">{t}</div>'
                '</div>'
            )
        rail_html += "</div>"
        st.markdown(rail_html, unsafe_allow_html=True)

with right:
    rail_box = st.empty()

    def render_rail(active_idx, done_flags, elapsed, flowing=True):
        rail_cls = "rail flowing" if flowing else "rail"
        rail_html = f"<div class='{rail_cls}'>"
        for i, s in enumerate(STAGES):
            dot_cls, label_cls = "rail-dot", "panel-label"
            t = ""
            if done_flags[i]:
                dot_cls += " done"; label_cls += " done"
                t = elapsed.get(s, "")
            elif i == active_idx:
                dot_cls += f" active {STAGE_CLASS[s]}"; label_cls += f" active {STAGE_CLASS[s]}"
                t = "running…"
            rail_html += (
                '<div class="rail-node" style="margin-bottom:0.5rem;">'
                f'<div class="{dot_cls}"></div>'
                f'<div class="{label_cls}">{STAGE_LABELS[s]}</div>'
                f'<div class="panel-time">{t}</div>'
                '</div>'
            )
        rail_html += "</div>"
        rail_box.markdown(rail_html, unsafe_allow_html=True)

    panel_boxes = [st.empty() for _ in STAGES]

    def render_panel(idx, stage_key, title, content, status, elapsed_str=""):
        scls = STAGE_CLASS[stage_key]
        state_cls = "active" if status == "active" else ("done" if status == "done" else "idle")
        if status == "done":
            tag = f'<span class="status-tag ok">done · {elapsed_str}</span>'
        elif status == "active":
            tag = f'<span class="status-tag {scls}">running…</span>'
        else:
            tag = ""
        label_cls = f"panel-label {scls}" if status == "active" else ("panel-label done" if status == "done" else "panel-label")
        html = (
            f'<div class="panel {scls} {state_cls}">'
            f'<div class="panel-top">'
            f'<div class="{label_cls}">{title}</div>'
            f'{tag}'
            f'</div>'
            f'<div class="panel-body">{content}</div>'
            f'</div>'
        )
        panel_boxes[idx].markdown(html, unsafe_allow_html=True)

if submitted:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        state = {}
        elapsed = {}
        done = [False, False, False, False]
        try:
            # Stage 1 — Search
            render_rail(0, done, elapsed)
            render_panel(0, "search", STAGE_LABELS["search"], "Querying sources…", "active")
            t0 = time.time()
            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = search_result["messages"][-1].content
            elapsed["search"] = f"{time.time()-t0:.2f}s"
            done[0] = True
            render_panel(0, "search", STAGE_LABELS["search"], state["search_results"], "done", elapsed["search"])

            # Stage 2 — Read
            render_rail(1, done, elapsed)
            render_panel(1, "read", STAGE_LABELS["read"], "Scraping selected source…", "active")
            t0 = time.time()
            reader_agent = build_read_agent()
            reader_result = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            })
            state["scraped_content"] = reader_result["messages"][-1].content
            elapsed["read"] = f"{time.time()-t0:.2f}s"
            done[1] = True
            render_panel(1, "read", STAGE_LABELS["read"], state["scraped_content"], "done", elapsed["read"])

            # Stage 3 — Write
            render_rail(2, done, elapsed)
            render_panel(2, "write", STAGE_LABELS["write"], "Drafting report…", "active")
            t0 = time.time()
            research_combined = (
                f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
            elapsed["write"] = f"{time.time()-t0:.2f}s"
            done[2] = True
            render_panel(2, "write", STAGE_LABELS["write"], state["report"], "done", elapsed["write"])

            # Stage 4 — Critique
            render_rail(3, done, elapsed)
            render_panel(3, "critique", STAGE_LABELS["critique"], "Reviewing draft…", "active")
            t0 = time.time()
            state["feedback"] = critic_chain.invoke({"report": state["report"]})
            elapsed["critique"] = f"{time.time()-t0:.2f}s"
            done[3] = True
            render_panel(3, "critique", STAGE_LABELS["critique"], state["feedback"], "done", elapsed["critique"])

            render_rail(3, done, elapsed, flowing=False)
            st.session_state.state = state
            st.session_state.elapsed = elapsed
            st.rerun()

        except Exception as e:
            st.error(f"Pipeline failed: {e}")

# ----------------------------------------------------------------------------
# Final results
# ----------------------------------------------------------------------------
if st.session_state.state:
    st.markdown("<hr style='margin:2.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)
    total = sum(float(v.replace("s", "")) for v in st.session_state.elapsed.values()) if st.session_state.elapsed else 0
    st.markdown(
        '<div class="hud-bar" style="border-bottom:none; margin-bottom:0.8rem;">'
        '<span class="rig-eyebrow" style="margin:0;">Output</span>'
        f'<span>TOTAL RUNTIME: {total:.2f}s</span>'
        '</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Search", "Scraped", "Report", "Critique"])
    with tab1:
        st.markdown(f"<div class='panel-body'>{st.session_state.state.get('search_results','')}</div>", unsafe_allow_html=True)
    with tab2:
        st.markdown(f"<div class='panel-body'>{st.session_state.state.get('scraped_content','')}</div>", unsafe_allow_html=True)
    with tab3:
        st.markdown(f"<div class='panel-body'>{st.session_state.state.get('report','')}</div>", unsafe_allow_html=True)
    with tab4:
        st.markdown(f"<div class='panel-body'>{st.session_state.state.get('feedback','')}</div>", unsafe_allow_html=True)

    st.download_button(
        "↓ Download report (.md)",
        data=str(st.session_state.state.get("report", "")),
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=False,
    )