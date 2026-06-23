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

    #  reader agent
    reader_agent = build_read_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}',"
            f"pick the most relevant URL and scrape it for deeper content. \n\n"
            f"Search Results:\n{state['search_results' ] [ : 800] }"
            )]
    })
    
    state["scraprd_content"] = reader_result['messages'][-1].content
    print("---scraped content ---\n",state["scraprd_content"])

    # writer chain
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results' ]} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content' ]}"
    )
    
    writer_result = write_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    state["report"] = writer_result
    print("---Final Report---\n",state["report"])

    # critic chain
    critic_result = critic_chain.invoke({
        "report": state["report"]
    })

    state["feedback"] = critic_result
    print("---feedback---\n",state["feedback"])

    return state
    
if __name__ == "__main__":
    result = run_research_pipeline("What is the current state of AI research in 2026?")