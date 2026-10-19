# $ run this on python 3.13 and below or on colab 
# below code is executed on colab 
# !pip install -U crewai "crewai[litellm]"



from google.colab import userdata
OPENROUTER_API_KEY = userdata.get('OPENROUTER_API_KEY')
import os 
from crewai import Agent,Task,Crew,Process,LLM 
# configure deepseek through openrouter 
llm = LLM(model="openrouter/deepseek/deepseek-v4.1-flash",
          base_url = "https://openrouter.ai/api/v1",
          api_key = OPENROUTER_API_KEY)
researcher = Agent(
    role = "Research analyst",
    goal = " Research a topic and provide accurate findings",
    backstory = "You are a detail oriented research analyst",
    llm = llm, verbose = True
)
task = Task(description = "Explain how multi agent systems work.",
            expected_output="A consice explanation with key components and use cases",
            agent=researcher)
crew = Crew(agents = [researcher],tasks=[task],process = Process.sequential,verbose=True)

results = await crew.kickoff_async()
print(results)
