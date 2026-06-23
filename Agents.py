from langchain.agents import  create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search,scrape_url
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.3
)

# 1. create build_search_agent 
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# 2. create web_scrape agent
def build_read_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


write_prompt = ChatPromptTemplate.from_messages([
    ('system',  "You are an expert  research writer. Write clear, structured and insughtful reports."),
    ("human", """Write a detailed research  report  on the topic below
    Topic : {topic}
    Research Gathered:
    {research}

    Structure the report as:
    - Intriduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be deatiled, factual and professional.
    
    """),
])

# create write_chain
write_chain = write_prompt | llm | StrOutputParser()

# critic chain

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()