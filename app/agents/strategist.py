import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from app.videoState import VideoState
from app.videoState import VideoState


def strategist(state: VideoState):
    print("Strategist: Researching real-time Facebook trends using DuckDuckGo...")

    #Initializing the free DuckDuckGo Search Tool
    search_tool = DuckDuckGoSearchRun()

    #Execute the search
    search_query = "What are the most viral and trending topics on Facebook Reels this week?"
    search_results = search_tool.invoke(search_query)

    #Initialize the LLM
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

    #Create a prompt to synthesize the search results
    prompt = PromptTemplate.from_template(
        """
        You are an expert social media strategist for Facebook Reels. 
        Analyze the following recent web search results about current trending topics:
        
        {search_results}
        
        Based on these trends, pick EXACTLY ONE highly engaging video topic that would go viral on Facebook.
        Do not explain your reasoning. Just return the topic title.
        """
    )

    #Chain the prompt and LLM together
    chain = prompt | llm

    #Generate the topic
    response = chain.invoke({"search_results": search_results})
    final_topic = response.content.strip()
    # print(f"Strategist: Selected topic - {final_topic}")
    return {"Strategist Selected Topic: ": final_topic}
