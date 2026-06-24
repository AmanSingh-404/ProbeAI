# Multi-Agent Research Pipeline

A modular, multi-agent system that automates the research-to-report workflow: searching for sources, scraping the most relevant content, drafting a report, and critiquing the draft for quality. The pipeline can be run from the command line or through a Streamlit web interface.

## Overview

Given a topic, the system runs four sequential stages, each handled by a dedicated agent or chain:

1. **Search Agent** — queries the web for recent, reliable information on the topic.
2. **Reader Agent** — selects the most relevant source from the search results and scrapes it for deeper content.
3. **Writer Chain** — synthesizes the search results and scraped content into a structured report.
4. **Critic Chain** — reviews the drafted report and returns feedback for improvement.

Each stage's output is passed to the next, and the full pipeline state (search results, scraped content, report, and feedback) is returned at the end of the run.

## Project Structure

```
.
├── agents.py            # Agent and chain definitions (search agent, reader agent, writer chain, critic chain)
├── pipeline.py          # Orchestrates the four-stage pipeline; runnable from the command line
├── app.py               # Streamlit web interface for the pipeline
├── requirements.txt     # Python dependencies
└── README.md
```

## Requirements

- Python 3.12 or later
- Dependencies listed in `requirements.txt`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

The agents and chains in `agents.py` rely on language model and search API credentials. Set the required API keys as environment variables before running the project, either by exporting them in your shell or by placing them in a `.env` file in the project root:

```
# Example — replace with the keys your provider integrations require
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Refer to `agents.py` for the exact environment variables expected by your configured providers.

## Usage

### Command Line

Run the pipeline directly from the terminal:

```bash
python pipeline.py
```

You will be prompted to enter a research topic. The pipeline will print the progress and output of each stage as it executes.

### Web Interface

Launch the Streamlit interface:

```bash
streamlit run app.py
```

Enter a topic in the input field and run the pipeline. Each stage's status and output is displayed as it completes, and the final report, search results, scraped content, and critic feedback are available in separate tabs. The generated report can be downloaded as a Markdown file.

## How It Works

`pipeline.py` defines `run_research_pipeline(topic: str) -> dict`, which:

1. Builds and invokes the search agent with the topic, storing the result in `state["search_results"]`.
2. Builds and invokes the reader agent with the search results, storing the scraped content in `state["scraped_content"]`.
3. Combines the search results and scraped content and passes them to the writer chain, storing the output in `state["report"]`.
4. Passes the report to the critic chain, storing the resulting feedback in `state["feedback"]`.
5. Returns the complete `state` dictionary.

`app.py` reuses the same agents and chains directly, rendering live progress for each stage in the browser instead of the terminal.

## Extending the Pipeline

To modify or extend the system:

- Add or adjust agents and chains in `agents.py`.
- Update the stage sequence or state handling in `pipeline.py`.
- Reflect any new stages in `app.py` by adding a corresponding panel and rail entry.

## License

Specify your project's license here.
