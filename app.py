import streamlit as st
from Agents import build_read_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(page_title="Research Pipeline", page_icon="◆", layout="wide")

# ----------------------------------------------------------------------------
# Design system: terminal / signal-lab aesthetic
# bg: near-black, body: IBM Plex Mono / Inter, accent: signal amber
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#0a0c0b;
  --panel:#101413;
  --line:#23282a;
  --text:#d9dad2;
  --muted:#7a8079;
  --accent:#ffb13c;
  --accent-dim:#5c4520;
  --ok:#5fd98a;
}

html, body, [class*="css"]{
  font-family:'Inter', sans-serif;
}

.stApp{
  background:var(--bg);
  color:var(--text);
}

#MainMenu, header, footer{visibility:hidden;}

/* ---- Header / hero ---- */
.rig-hero{
  border-bottom:1px solid var(--line);
  padding:2.2rem 0 1.6rem 0;
  margin-bottom:2rem;
}
.rig-eyebrow{
  font-family:'IBM Plex Mono', monospace;
  color:var(--accent);
  font-size:0.78rem;
  letter-spacing:0.18em;
  text-transform:uppercase;
  margin-bottom:0.6rem;
}
.rig-title{
  font-family:'IBM Plex Mono', monospace;
  font-weight:700;
  font-size:2.4rem;
  letter-spacing:-0.01em;
  color:var(--text);
  margin:0;
}
.rig-sub{
  color:var(--muted);
  font-size:0.95rem;
  margin-top:0.5rem;
  max-width:560px;
}

/* ---- Pipeline rail (signature element) ---- */
.rail{
  display:flex;
  flex-direction:column;
  border-left:1px solid var(--line);
  margin-left:14px;
  padding-left:0;
}
.rail-node{
  position:relative;
  padding:0 0 0 28px;
  margin-bottom:0;
}
.rail-dot{
  position:absolute;
  left:-6px;
  top:6px;
  width:11px;
  height:11px;
  border-radius:50%;
  background:var(--bg);
  border:2px solid var(--line);
}
.rail-dot.active{
  border-color:var(--accent);
  background:var(--accent);
  box-shadow:0 0 0 4px var(--accent-dim);
}
.rail-dot.done{
  border-color:var(--ok);
  background:var(--ok);
}

/* ---- Panel / card ---- */
.panel{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:2px;
  padding:1.1rem 1.3rem;
  margin-bottom:1.1rem;
}
.panel-label{
  font-family:'IBM Plex Mono', monospace;
  font-size:0.72rem;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--muted);
  margin-bottom:0.5rem;
}
.panel-label.active{ color:var(--accent); }
.panel-label.done{ color:var(--ok); }
.panel-body{
  font-size:0.92rem;
  line-height:1.55;
  color:var(--text);
  white-space:pre-wrap;
}

/* ---- Inputs ---- */
.stTextInput input{
  background:var(--panel) !important;
  border:1px solid var(--line) !important;
  color:var(--text) !important;
  font-family:'IBM Plex Mono', monospace !important;
  border-radius:2px !important;
  padding:0.7rem 0.9rem !important;
}
.stTextInput input:focus{
  border-color:var(--accent) !important;
  box-shadow:0 0 0 1px var(--accent) !important;
}
.stTextInput label{
  font-family:'IBM Plex Mono', monospace;
  font-size:0.75rem;
  letter-spacing:0.1em;
  text-transform:uppercase;
  color:var(--muted) !important;
}

.stButton button, .stFormSubmitButton button{
  background:var(--accent) !important;
  color:#1a1206 !important;
  border:none !important;
  font-family:'IBM Plex Mono', monospace !important;
  font-weight:600 !important;
  letter-spacing:0.06em !important;
  text-transform:uppercase !important;
  font-size:0.82rem !important;
  border-radius:2px !important;
  padding:0.7rem 1rem !important;
  transition:opacity 0.15s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover{
  opacity:0.85;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{
  gap:0;
  border-bottom:1px solid var(--line);
}
.stTabs [data-baseweb="tab"]{
  font-family:'IBM Plex Mono', monospace;
  font-size:0.78rem;
  letter-spacing:0.08em;
  text-transform:uppercase;
  color:var(--muted);
}
.stTabs [aria-selected="true"]{
  color:var(--accent) !important;
  border-bottom-color:var(--accent) !important;
}

.status-tag{
  display:inline-block;
  font-family:'IBM Plex Mono', monospace;
  font-size:0.7rem;
  letter-spacing:0.1em;
  padding:0.15rem 0.5rem;
  border:1px solid var(--line);
  border-radius:2px;
  color:var(--muted);
}
.status-tag.ok{ color:var(--ok); border-color:var(--ok); }

hr{ border-color:var(--line) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown("""
<div class="rig-hero">
  <div class="rig-eyebrow">Autonomous Research Rig — 4-stage pipeline</div>
  <div class="rig-title">research.exec()</div>
  <div class="rig-sub">Search → Read → Write → Critique. Each stage hands its output to the next.
  Enter a topic and watch the rig work in real time.</div>
</div>
""", unsafe_allow_html=True)

if "state" not in st.session_state:
    st.session_state.state = None

STAGES = ["search", "read", "write", "critique"]
STAGE_LABELS = {
    "search": "01 · Search Agent — gathering sources",
    "read": "02 · Reader Agent — scraping deep content",
    "write": "03 · Writer Chain — drafting the report",
    "critique": "04 · Critic Chain — reviewing the draft",
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
            <div class="rail-node" style="margin-bottom:1.3rem;">
              <div class="rail-dot"></div>
              <div class="panel-label">{STAGE_LABELS[s]}</div>
            </div>
            """
        rail_html += "</div>"
        st.markdown(rail_html, unsafe_allow_html=True)

with right:
    rail_box = st.empty()

    def render_rail(active_idx, done_flags):
        rail_html = "<div class='rail'>"
        for i, s in enumerate(STAGES):
            dot_cls = "rail-dot"
            label_cls = "panel-label"
            if done_flags[i]:
                dot_cls += " done"
                label_cls += " done"
            elif i == active_idx:
                dot_cls += " active"
                label_cls += " active"
            rail_html += f"""
            <div class="rail-node" style="margin-bottom:0.4rem;">
              <div class="{dot_cls}"></div>
              <div class="{label_cls}">{STAGE_LABELS[s]}</div>
            </div>
            """
        rail_html += "</div>"
        rail_box.markdown(rail_html, unsafe_allow_html=True)

    panel_boxes = [st.empty() for _ in STAGES]

    def render_panel(idx, title, content, status):
        cls = "active" if status == "active" else ("done" if status == "done" else "")
        tag = '<span class="status-tag ok">done</span>' if status == "done" else (
              '<span class="status-tag">running…</span>' if status == "active" else "")
        panel_boxes[idx].markdown(f"""
        <div class="panel">
          <div class="panel-label {cls}">{title} {tag}</div>
          <div class="panel-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)

if submitted:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        state = {}
        done = [False, False, False, False]
        try:
            render_rail(0, done)
            render_panel(0, STAGE_LABELS["search"], "Querying sources…", "active")

            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = search_result["messages"][-1].content
            done[0] = True
            render_panel(0, STAGE_LABELS["search"], state["search_results"], "done")

            render_rail(1, done)
            render_panel(1, STAGE_LABELS["read"], "Scraping selected source…", "active")

            reader_agent = build_read_agent()
            reader_result = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            })
            state["scraped_content"] = reader_result["messages"][-1].content
            done[1] = True
            render_panel(1, STAGE_LABELS["read"], state["scraped_content"], "done")

            render_rail(2, done)
            render_panel(2, STAGE_LABELS["write"], "Drafting report…", "active")

            research_combined = (
                f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
            done[2] = True
            render_panel(2, STAGE_LABELS["write"], state["report"], "done")

            render_rail(3, done)
            render_panel(3, STAGE_LABELS["critique"], "Reviewing draft…", "active")

            state["feedback"] = critic_chain.invoke({"report": state["report"]})
            done[3] = True
            render_panel(3, STAGE_LABELS["critique"], state["feedback"], "done")

            render_rail(3, done)
            st.session_state.state = state

        except Exception as e:
            st.error(f"Pipeline failed: {e}")

# ----------------------------------------------------------------------------
# Final results
# ----------------------------------------------------------------------------
if st.session_state.state:
    st.markdown("<hr style='margin:2.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='rig-eyebrow'>Output</div>", unsafe_allow_html=True)

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