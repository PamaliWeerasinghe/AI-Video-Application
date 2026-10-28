from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from app.videoState import VideoState


def _parse_topic(response: str) -> tuple[str, str]:
    topic = response.strip()
    if not topic:
        raise ValueError("empty topic response")

    title, separator, description = topic.partition(" - ")
    if not separator:
        return topic, ""
    return title.strip(), description.strip()


def strategist(state: VideoState):
    print("Strategist: Researching real-time Facebook trends using DuckDuckGo...")

    # 1. Use a simple string for the web search
    search_tool = DuckDuckGoSearchRun()
    search_query = "trending visual niches Facebook Reels TikTok 2026"
    search_results = search_tool.invoke(search_query)

    # 2. Initialize the LLM
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

    # 3. Create a prompt to synthesize the search results
    prompt = PromptTemplate.from_template(
        """
        You are an elite social media strategist specializing in Facebook Reels and TikTok monetization.
        Your goal is to identify highly viral, visually satisfying, and high-retention broad niches based on recent search data.
        
        Analyze the following recent web search results about current trending niches:
        
        {search_results}
        
        Based on these trends, pick EXACTLY ONE highly engaging video niche that relies on satisfying visuals, rapid transformations, or sensory details.
        Do not explain your reasoning. Return only the niche title and a short description, separated by " - ".
        """
    )

    # Chain the prompt and LLM together
    chain = prompt | llm

    # Generate the topic
    response = chain.invoke({"search_results": search_results})
    final_topic = response.content.strip()
    title, description = _parse_topic(final_topic)
    # print(f"Strategist: Selected topic - {final_topic}")
    return {"topic": title, "short_description": description}