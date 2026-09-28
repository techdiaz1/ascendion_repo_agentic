from openrouter import OpenRouter
import os 
import json
# import truststore
# truststore.inject_into_ssl()
from dotenv import load_dotenv
load_dotenv()

with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEy")) as client:
    response = client.chat.send(
        model = "deepseek/deepseek-v4.1-flash",
        messages = [
            {"role":"user","content":"Explain LLMs in brief"}
        ],max_tokens=10000
    )
    print(json.dumps(response.model_dump(),indent=2,ensure_ascii=False)) #pretty print as a JSON object 
    print("=======================================================================")
    print(response.choices[0].message.content) # LLM response
