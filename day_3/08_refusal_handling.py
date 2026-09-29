# Refusal handling means representing a model refusal explicitly in our structured response, 
# so our application can detect and handle it programmatically instead of treating 
# every model response as a successful answer
# We don't want to assume every LLM response is a successful answer.
#  So we make refusal an explicit part of the response schema


from pydantic import BaseModel
class Response(BaseModel):
    answer:str
    refused: bool

result = Response.model_validate(
    {
        "answer": "hello world",
        "refused" : True
    }
)
if result.refused:
    print("The model refused the request, handle refusal")
else:
    print("process the answer")
    print("answer :",result.answer)
