# reçoit le contexte et appelle l'API Gemini

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

from .gemini_service import generate_scenario
from ..data.employees import get_service_contexts, get_employees_by_service

app = FastAPI()


class GenerationRequest(BaseModel):
    contexte: dict[str, Any]

@app.get("/services/{service}")
def get_service(service: str):
    try:
        contexts = get_service_contexts()
        employees = get_employees_by_service()

        if service not in contexts:
            raise HTTPException(
                status_code=404,
                detail="Service introuvable"
            )

        return {
            "contexte": contexts[service],
            "employes": employees[service]
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Erreur de récupération du service :", error)
        raise HTTPException(
            status_code=500,
            detail="Impossible de récupérer le service"
        )

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
