import re

with open('c:/Hackathon tracker/hackathon-tracker/backend/app/main.py', 'r') as f:
    content = f.read()

handler_code = """
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import json

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("\\n" + "="*50)
    print("422 VALIDATION ERROR")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {exc.body}")
    print(f"Errors: {json.dumps(exc.errors(), default=str, indent=2)}")
    print("="*50 + "\\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )
"""

if 'RequestValidationError' not in content:
    content = content.replace('app = FastAPI(', handler_code + '\\napp = FastAPI(')
    with open('c:/Hackathon tracker/hackathon-tracker/backend/app/main.py', 'w') as f:
        f.write(content)
