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
    search_query = "What are the most viral and trending niches on Facebook Reels this week?"
    search_results = search_tool.invoke(search_query)

    #Initialize the LLM
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

    #Create a prompt to synthesize the search results
    prompt = PromptTemplate.from_template(
        """
        You are an expert social media strategist for Facebook Reels. 
        Analyze the following recent web search results about current trending niches:
        
        {search_results}
        
        Based on these trends, pick EXACTLY ONE highly engaging video niche that would go viral on Facebook.
        Do not explain your reasoning. Just return the niche title with a short description about the niche by 
        sepearing the nice and the description through a colon(:).
        """
    )

    #Chain the prompt and LLM together
    chain = prompt | llm

    #Generate the topic
    response = chain.invoke({"search_results": search_results})
    final_topic = response.content.strip()
    #split the final topic into title and description
    split_result = final_topic.split(": ",1)
    title = split_result[0]
    description = split_result[1] 
    print(f"Strategist: Selected topic - {final_topic}")
    return {"topic": title, "short_description": description}
    
