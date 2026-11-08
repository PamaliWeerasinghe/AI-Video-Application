import json
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from app.videoState import VideoState

SELECTED_NICHE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "selected_niche.json"


def _parse_topic(response: str) -> tuple[str, str]:
    topic = response.strip()
    if not topic:
        raise ValueError("empty topic response")

    title, separator, description = topic.partition(" - ")
    if not separator:
        return topic, ""
    title = title.strip()
    if not title:
        raise ValueError("empty topic title")
    return title, description.strip()


def _load_selected_niche() -> tuple[str, str] | None:
    if not SELECTED_NICHE_PATH.exists():
        return None

    selected_niche = json.loads(SELECTED_NICHE_PATH.read_text(encoding="utf-8"))
    if not isinstance(selected_niche, dict):
        raise ValueError("The saved niche must be a JSON object.")

    title = selected_niche.get("topic")
    description = selected_niche.get("short_description")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("The saved niche must include a non-empty topic.")
    if not isinstance(description, str):
        raise ValueError("The saved niche must include a string short_description.")

    return title.strip(), description.strip()


def _save_selected_niche(title: str, description: str) -> None:
    SELECTED_NICHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SELECTED_NICHE_PATH.write_text(
        json.dumps(
            {"topic": title, "short_description": description},
            indent=2,
        ),
        encoding="utf-8",
    )


def strategist(state: VideoState):
    selected_niche = _load_selected_niche()
    if selected_niche is not None:
        title, description = selected_niche
        print(f"Strategist: Reusing selected niche: {title}")
        return {"topic": title, "short_description": description}

    print("Strategist: Finding one popular niche using DuckDuckGo...")

    search_tool = DuckDuckGoSearchRun()
    search_query = "trending visual niches Facebook Reels TikTok 2026"
    search_results = search_tool.invoke(search_query)

    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
    prompt = PromptTemplate.from_template(
        """
        You are an elite social media strategist specializing in Facebook Reels and TikTok monetization.
        Analyze these recent search results:
        {search_results}

        Select exactly ONE currently popular, broad video niche supported by the search results.
        Choose a niche suitable for many distinct short-form scripts, not a single video idea.
        Do not list alternatives or explain your reasoning. Return only the niche title and a short
        description, separated by " - ".
        """
    )

    chain = prompt | llm
    response = chain.invoke({"search_results": search_results})
    title, description = _parse_topic(response.content)
    _save_selected_niche(title, description)
    print(f"Strategist: Selected niche: {title}")
    return {"topic": title, "short_description": description}