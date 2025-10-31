import os, requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Replace this with your real front-end origin(s)
ALLOWED_ORIGINS = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StylePayload(BaseModel):
    pattern: str
    collar: str
    persona: str
    word: str | None = ""

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/fashion-catalog/")
def fashion_catalog(p: StylePayload):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Server missing OPENAI_API_KEY")

    prompt = f"""
    Suggest exactly one REAL, live online fashion brand catalog URL (full https URL)
    that best matches these traits. Return ONLY the URL, nothing else.

    Pattern: {p.pattern}
    Collar: {p.collar}
    Persona vibe: {p.persona}
    One-word self description: {p.word or ""}
    """

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-5-nano",
                "messages": [
                    {"role": "system", "content": "Return only a single https URL. No commentary."},
                    {"role": "user", "content": prompt.strip()},
                ],
            },
            timeout=15
        )
        r.raise_for_status()
        url = r.json()["choices"][0]["message"]["content"].strip().split()[0]
        if not url.startswith("http"):
            url = "https://www2.hm.com/en_in/men/shop-by-product/shirts.html"
        return {"url": url}
    except Exception:
        raise HTTPException(status_code=502, detail="OpenAI upstream failed")
