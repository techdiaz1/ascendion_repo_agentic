from jsonschema import validate,ValidationError,FormatChecker
from email_validator import validate_email,ValidatedEmail #pip install email-validator

data = {
    "name" : "Arib",
    "age" : 28,
    "email" : "demo@ascendion.com",
    "role":"developer"
}
schema = {
    "type":"object",
    "properties": {
        "name":{"type":"string","minLength":3},
        "age":{"type":"integer","minimum":0},
        "email":{"type":"string","format":"email"},
        "role":{"type":"string","enum":["developer","designer","manager"]}
    },
"required":["name","age","email","role"],"additionalProperties":False
}
try:
    validate(instance=data,schema=schema,format_checker=FormatChecker())
    validate_email(data['email'])
    print("Valid JSON output")
except ValidationError as e:
    print("Invalid JSON output")
    print(e.message)
