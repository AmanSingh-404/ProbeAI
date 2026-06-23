from Agents import build_read_agent,build_search_agent, write_chain, critic_chain

def run_research_pipeline(topic:str) -> dict:

    state = {}

    # search agent working
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages":[("user", f"find recent, relaible and detailed information about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content
    print("---Search Results ---\n",state["search_results"])