import streamlit as st
from pipeline import run_research_pipeline

st.set_page_config(page_title="Multi-Agent Research System", page_icon="🔎", layout="wide")

st.title("🔎 Multi-Agent Research System")
st.caption("Search Agent → Reader Agent → Writer Chain → Critic Chain")

# Keep results across reruns
if "state" not in st.session_state:
    st.session_state.state = None

with st.form("research_form"):
    topic = st.text_input("Enter a research topic", placeholder="e.g. Impact of AI on renewable energy")
    submitted = st.form_submit_button("Run Research Pipeline", use_container_width=True)

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        # Placeholders for each step so we can update them live
        step1 = st.status("Step 1 — Search Agent is working...", expanded=True)
        step2_box = st.empty()
        step3_box = st.empty()
        step4_box = st.empty()

        state = {}
        try:
            # --- Step 1: Search Agent ---
            from Agents import build_read_agent, build_search_agent, writer_chain, critic_chain

            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = search_result["messages"][-1].content
            step1.update(label="Step 1 — Search Agent finished ✅", state="complete")
            with step1:
                st.markdown("**Search Results**")
                st.write(state["search_results"])

            # --- Step 2: Reader Agent ---
            step2 = step2_box.status("Step 2 — Reader Agent is scraping top resources...", expanded=True)
            reader_agent = build_read_agent()
            reader_result = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            })
            state["scraped_content"] = reader_result["messages"][-1].content
            step2.update(label="Step 2 — Reader Agent finished ✅", state="complete")
            with step2:
                st.markdown("**Scraped Content**")
                st.write(state["scraped_content"])

            # --- Step 3: Writer Chain ---
            step3 = step3_box.status("Step 3 — Writer is drafting the report...", expanded=True)
            research_combined = (
                f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({
                "topic": topic,
                "research": research_combined
            })
            step3.update(label="Step 3 — Writer finished ✅", state="complete")
            with step3:
                st.markdown("**Draft Report**")
                st.write(state["report"])

            # --- Step 4: Critic Chain ---
            step4 = step4_box.status("Step 4 — Critic is reviewing the report...", expanded=True)
            state["feedback"] = critic_chain.invoke({
                "report": state["report"]
            })
            step4.update(label="Step 4 — Critic finished ✅", state="complete")
            with step4:
                st.markdown("**Critic Feedback**")
                st.write(state["feedback"])

            st.session_state.state = state
            st.success("Research pipeline completed!")

        except Exception as e:
            st.error(f"Pipeline failed: {e}")

# --- Final results section (persists after rerun) ---
if st.session_state.state:
    st.divider()
    st.header("📄 Final Results")

    tab1, tab2, tab3, tab4 = st.tabs(["Search Results", "Scraped Content", "Report", "Critic Feedback"])

    with tab1:
        st.write(st.session_state.state.get("search_results", ""))
    with tab2:
        st.write(st.session_state.state.get("scraped_content", ""))
    with tab3:
        st.write(st.session_state.state.get("report", ""))
    with tab4:
        st.write(st.session_state.state.get("feedback", ""))

    st.download_button(
        "⬇️ Download Report",
        data=str(st.session_state.state.get("report", "")),
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=True,
    )