import time
import streamlit as st
from Agents import build_read_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(page_title="research.exec()", page_icon="◆", layout="wide")

# ----------------------------------------------------------------------------
# Design system: control-room HUD
# bg: near-black w/ grid, accent: signal amber, telemetry green, alert red
# type: IBM Plex Mono (display/data) + Inter (body)
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#07090a;
  --panel:#0e1213;
  --panel-2:#111615;
  --line:#202726;
  --line-bright:#33403d;
  --text:#dcdecd;
  --muted:#697370;
  --accent:#ffb13c;
  --accent-soft:#3d2c10;
  --ok:#5fe39a;
  --ok-soft:#0f2e1e;
  --red:#ff5c5c;
}

html, body, [class*="css"]{ font-family:'Inter', sans-serif; }

.stApp{
  background:
    linear-gradient(rgba(7,9,10,0.93), rgba(7,9,10,0.97)),
    repeating-linear-gradient(0deg, transparent 0 27px, var(--line) 27px 28px),
    repeating-linear-gradient(90deg, transparent 0 27px, var(--line) 27px 28px);
  background-size: 100% 100%, 28px 28px, 28px 28px;
  color:var(--text);
}
#MainMenu, header, footer{visibility:hidden;}

/* scanline sweep */
@keyframes sweep { 0%{ transform:translateY(-100%); } 100%{ transform:translateY(100vh); } }
.scanline{
  position:fixed; left:0; right:0; height:140px; top:0; z-index:9999;
  background:linear-gradient(to bottom, transparent, rgba(255,177,60,0.035), transparent);
  animation:sweep 7s linear infinite;
  pointer-events:none;
}

/* ---- HUD top bar ---- */
.hud-bar{
  display:flex; justify-content:space-between; align-items:baseline;
  font-family:'IBM Plex Mono', monospace;
  font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase;
  color:var(--muted);
  border-bottom:1px solid var(--line);
  padding-bottom:0.6rem; margin-bottom:1.4rem;
}
.hud-bar span.live{ color:var(--ok); }
.hud-dot{ display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--ok); margin-right:6px;
  box-shadow:0 0 6px var(--ok); animation:blink 1.6s ease-in-out infinite; }
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:0.25;} }

/* ---- Hero ---- */
.rig-hero{ padding:0.4rem 0 1.8rem 0; margin-bottom:1.6rem; border-bottom:1px solid var(--line); }
.rig-eyebrow{
  font-family:'IBM Plex Mono', monospace; color:var(--accent); font-size:0.78rem;
  letter-spacing:0.2em; text-transform:uppercase; margin-bottom:0.7rem;
}
.rig-title{
  font-family:'IBM Plex Mono', monospace; font-weight:700; font-size:3rem;
  letter-spacing:-0.02em; color:var(--text); margin:0; line-height:1;
  text-shadow:0 0 18px rgba(255,177,60,0.18);
}
.rig-title .blink-cursor{
  display:inline-block; width:0.5ch; background:var(--accent); margin-left:4px;
  animation:cursorblink 1.1s steps(1) infinite;
}
@keyframes cursorblink{ 0%,49%{opacity:1;} 50%,100%{opacity:0;} }
.rig-sub{ color:var(--muted); font-size:0.95rem; margin-top:0.7rem; max-width:600px; line-height:1.5; }

/* ---- Pipeline rail ---- */
.rail{ display:flex; flex-direction:column; border-left:1px solid var(--line); margin-left:14px; }
.rail-node{ position:relative; padding:0 0 0 28px; }
.rail-dot{
  position:absolute; left:-7px; top:6px; width:13px; height:13px; border-radius:50%;
  background:var(--bg); border:2px solid var(--line); transition:all 0.3s ease;
}
@keyframes pulse-glow{
  0%{ box-shadow:0 0 0 0 rgba(255,177,60,0.55); }
  70%{ box-shadow:0 0 0 9px rgba(255,177,60,0); }
  100%{ box-shadow:0 0 0 0 rgba(255,177,60,0); }
}
.rail-dot.active{ border-color:var(--accent); background:var(--accent); animation:pulse-glow 1.6s ease-out infinite; }
.rail-dot.done{ border-color:var(--ok); background:var(--ok); }

/* ---- Panel / card ---- */
.panel{
  background:linear-gradient(180deg, var(--panel), var(--panel-2));
  border:1px solid var(--line); border-radius:3px; padding:1.15rem 1.35rem; margin-bottom:1.1rem;
  position:relative; overflow:hidden;
}
.panel.active{ border-color:var(--accent-soft); box-shadow:0 0 0 1px var(--accent-soft), 0 0 22px -8px var(--accent); }
.panel.done{ border-color:var(--line-bright); }
.panel-top{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.55rem; }
.panel-label{
  font-family:'IBM Plex Mono', monospace; font-size:0.74rem; letter-spacing:0.13em;
  text-transform:uppercase; color:var(--muted);
}
.panel-label.active{ color:var(--accent); }
.panel-label.done{ color:var(--ok); }
.panel-time{ font-family:'IBM Plex Mono', monospace; font-size:0.7rem; color:var(--muted); }
.panel-body{ font-size:0.92rem; line-height:1.6; color:var(--text); white-space:pre-wrap; }

/* ---- Inputs ---- */
.stTextInput input{
  background:var(--panel) !important; border:1px solid var(--line) !important; color:var(--text) !important;
  font-family:'IBM Plex Mono', monospace !important; border-radius:2px !important; padding:0.75rem 0.95rem !important;
}
.stTextInput input:focus{ border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent) !important; }
.stTextInput label{
  font-family:'IBM Plex Mono', monospace; font-size:0.75rem; letter-spacing:0.12em;
  text-transform:uppercase; color:var(--muted) !important;
}
.stButton button, .stFormSubmitButton button{
  background:var(--accent) !important; color:#1a1206 !important; border:none !important;
  font-family:'IBM Plex Mono', monospace !important; font-weight:600 !important; letter-spacing:0.08em !important;
  text-transform:uppercase !important; font-size:0.82rem !important; border-radius:2px !important;
  padding:0.75rem 1rem !important; transition:all 0.15s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover{
  opacity:0.9; box-shadow:0 0 18px -2px var(--accent);
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{ gap:0; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{
  font-family:'IBM Plex Mono', monospace; font-size:0.78rem; letter-spacing:0.09em;
  text-transform:uppercase; color:var(--muted);
}
.stTabs [aria-selected="true"]{ color:var(--accent) !important; border-bottom-color:var(--accent) !important; }

.status-tag{
  display:inline-block; font-family:'IBM Plex Mono', monospace; font-size:0.68rem; letter-spacing:0.1em;
  padding:0.15rem 0.55rem; border:1px solid var(--line); border-radius:2px; color:var(--muted);
}
.status-tag.ok{ color:var(--ok); border-color:var(--ok); background:var(--ok-soft); }
.status-tag.run{ color:var(--accent); border-color:var(--accent-soft); background:var(--accent-soft); }

hr{ border-color:var(--line) !important; }
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HUD bar
# ----------------------------------------------------------------------------
st.markdown("""
<div class="hud-bar">
  <span><span class="hud-dot"></span><span class="live">SYSTEM ONLINE</span> · multi-agent rig v1</span>
  <span>MODE: SEARCH · READ · WRITE · CRITIQUE</span>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown("""
<div class="rig-hero">
  <div class="rig-eyebrow">Autonomous Research Rig — 4-stage pipeline</div>
  <div class="rig-title">research.exec()<span class="blink-cursor">&nbsp;</span></div>
  <div class="rig-sub">Four agents, one chain of custody: a topic goes in, a reviewed report comes out.
  Each stage hands its output downstream — watch the rail light up as the rig works.</div>
</div>
""", unsafe_allow_html=True)

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

left, right = st.columns([1, 2.2], gap="large")

with left:
    with st.form("research_form"):
        topic = st.text_input("Topic", placeholder="e.g. impact of AI on renewable energy")
        submitted = st.form_submit_button("Run pipeline", use_container_width=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    if not submitted and st.session_state.state is None:
        rail_html = "<div class='rail'>"
        for s in STAGES:
            rail_html += f"""
            <div class="rail-node" style="margin-bottom:1.4rem;">
              <div class="rail-dot"></div>
              <div class="panel-label">{STAGE_LABELS[s]}</div>
            </div>
            """
        rail_html += "</div>"
        st.markdown(rail_html, unsafe_allow_html=True)
    elif st.session_state.state:
        rail_html = "<div class='rail'>"
        for s in STAGES:
            t = st.session_state.elapsed.get(s, "")
            rail_html += f"""
            <div class="rail-node" style="margin-bottom:1.1rem;">
              <div class="rail-dot done"></div>
              <div class="panel-label done">{STAGE_LABELS[s]}</div>
              <div class="panel-time">{t}</div>
            </div>
            """
        rail_html += "</div>"
        st.markdown(rail_html, unsafe_allow_html=True)

with right:
    rail_box = st.empty()

    def render_rail(active_idx, done_flags, elapsed):
        rail_html = "<div class='rail'>"
        for i, s in enumerate(STAGES):
            dot_cls, label_cls = "rail-dot", "panel-label"
            t = ""
            if done_flags[i]:
                dot_cls += " done"; label_cls += " done"
                t = elapsed.get(s, "")
            elif i == active_idx:
                dot_cls += " active"; label_cls += " active"
                t = "running…"
            rail_html += f"""
            <div class="rail-node" style="margin-bottom:0.5rem;">
              <div class="{dot_cls}"></div>
              <div class="{label_cls}">{STAGE_LABELS[s]}</div>
              <div class="panel-time">{t}</div>
            </div>
            """
        rail_html += "</div>"
        rail_box.markdown(rail_html, unsafe_allow_html=True)

    panel_boxes = [st.empty() for _ in STAGES]

    def render_panel(idx, title, content, status, elapsed_str=""):
        cls = "active" if status == "active" else ("done" if status == "done" else "")
        if status == "done":
            tag = f'<span class="status-tag ok">done · {elapsed_str}</span>'
        elif status == "active":
            tag = '<span class="status-tag run">running…</span>'
        else:
            tag = ""
        panel_boxes[idx].markdown(f"""
        <div class="panel {cls}">
          <div class="panel-top">
            <div class="panel-label {cls}">{title}</div>
            {tag}
          </div>
          <div class="panel-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)

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
            render_panel(0, STAGE_LABELS["search"], "Querying sources…", "active")
            t0 = time.time()
            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = search_result["messages"][-1].content
            elapsed["search"] = f"{time.time()-t0:.2f}s"
            done[0] = True
            render_panel(0, STAGE_LABELS["search"], state["search_results"], "done", elapsed["search"])

            # Stage 2 — Read
            render_rail(1, done, elapsed)
            render_panel(1, STAGE_LABELS["read"], "Scraping selected source…", "active")
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
            render_panel(1, STAGE_LABELS["read"], state["scraped_content"], "done", elapsed["read"])

            # Stage 3 — Write
            render_rail(2, done, elapsed)
            render_panel(2, STAGE_LABELS["write"], "Drafting report…", "active")
            t0 = time.time()
            research_combined = (
                f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
            elapsed["write"] = f"{time.time()-t0:.2f}s"
            done[2] = True
            render_panel(2, STAGE_LABELS["write"], state["report"], "done", elapsed["write"])

            # Stage 4 — Critique
            render_rail(3, done, elapsed)
            render_panel(3, STAGE_LABELS["critique"], "Reviewing draft…", "active")
            t0 = time.time()
            state["feedback"] = critic_chain.invoke({"report": state["report"]})
            elapsed["critique"] = f"{time.time()-t0:.2f}s"
            done[3] = True
            render_panel(3, STAGE_LABELS["critique"], state["feedback"], "done", elapsed["critique"])

            render_rail(3, done, elapsed)
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
    st.markdown(f"""
    <div class="hud-bar" style="border-bottom:none; margin-bottom:0.8rem;">
      <span class="rig-eyebrow" style="margin:0;">Output</span>
      <span>TOTAL RUNTIME: {total:.2f}s</span>
    </div>
    """, unsafe_allow_html=True)

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