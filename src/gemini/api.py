# reçoit le contexte et appelle l'API Gemini

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .gemini_service import generate_scenario

app = FastAPI()


class GenerationRequest(BaseModel):
    contexte: dict[str, str]


@app.post("/generate")
def generate(request: GenerationRequest):
    try:
        resultat = generate_scenario(request.contexte)

        # On transmet juste le scénario
        return resultat["scenario"]

    except Exception as error:
        print("Erreur de génération :", error)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la génération du scénario"
        )
