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


@tool
def scrape_url(url: str) -> str:
    """ Scrape  and return clean text  content  from given URL for deeper reading. """
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(['style','script','head','footer', 'nav']):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Error scraping {url}: {e}"
