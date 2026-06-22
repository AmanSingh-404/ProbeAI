from langchain.tools import tool
# pyrefly: ignore [missing-import]
from tavily import TavilyClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from rich import print
import os
import requests
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query:str) -> str:
    """Search the web for recent and relaible information on a topic. return titles , URLs ans snippets"""
    results = tavily.search(query=query,max_results=5)

    out = []

    for r in results['results']:
        out.append(f"Title:{r['title']}\n{r['url']}\nSnippet: {r['content'][:300]}...\n")
    
    return "\n----\n".join(out)

print(web_search.invoke("latest news about AI"))


# @tool
# def web_scrape(url:str) -> str:
#     """Scrape a single URL and return the full text content (first 2000 chars)."""
#     try:
#         response = requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=10)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.content,"html.parser")

#         text = soup.get_text()
#         clean = " ".join(text.split())
#         return clean[:2000]

#     except Exception as e:
#         return f"Error scraping {url}: {str(e)[:200]}"