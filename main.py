# main.py
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from auth import authenticate_user, get_current_user
from schemas import (
    HistoryResponse,
    LoginRequest,
    LoginResponse,
    PromptRequest,
    PromptResponse,
)

from services.alternate_service import generate_llama_response as generate_from_llama


from storage.history import HistoryStore

app = FastAPI(
    title="LLaMA Prompt Backend",
    description="FastAPI backend that sends prompts to Replicate LLaMA model and stores history.",
    version="1.0.0",
)

# CORS (agar frontend se hit karna ho to)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod me restrict karna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

history_store = HistoryStore(file_path="history.json")


@app.post("/login/", response_model=LoginResponse, tags=["Auth"])
def login(payload: LoginRequest):
    """
    Accepts username and password, returns bearer token.
    """
    token = authenticate_user(payload.username, payload.password)
    return LoginResponse(access_token=token)


@app.post("/prompt/", response_model=PromptResponse, tags=["Prompt"])
async def send_prompt(
    payload: PromptRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Authenticated: send prompt to Replicate LLaMA model and return response.
    """
    # Call Replicate
    model_response = await generate_from_llama(payload.prompt)

    # Log in history
    history_item = history_store.log_interaction(
        username=current_user,
        prompt=payload.prompt,
        response=model_response,
    )

    return PromptResponse(
        prompt=history_item.prompt,
        response=history_item.response,
        timestamp=history_item.timestamp,
    )


@app.get("/history/", response_model=HistoryResponse, tags=["History"])
def get_history(
    current_user: str = Depends(get_current_user),
):
    """
    Authenticated: return user's prompt-response history.
    """
    history = history_store.get_history(current_user)
    return HistoryResponse(history=history)


@app.get("/", tags=["Meta"])
def root():
    return {
        "message": "LLaMA backend is running",
        "time": datetime.utcnow().isoformat(),
    }


# For running via: python main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
