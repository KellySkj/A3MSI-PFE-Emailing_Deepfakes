
import os
import time
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class Scenario(BaseModel):
    titre: str
    service: str
    objet_email: str
    corps_email: str
    indices_suspects: list[str]
    explication_pedagogique: str
    difficulte: str


contexte = {
    "service": "Comptabilité",
    "fonction": "Assistant comptable",
    "difficulte": "Très Avancée",
    "objectif": "Reconnaître une demande urgente inhabituelle",
}

prompt = f"""
Tu conçois des exercices de sensibilisation à la cybersécurité.

Crée un scénario fictif de phishing par e-mail destiné
à une simulation autorisée dans une entreprise pilote.

Contexte : {json.dumps(contexte, ensure_ascii=False)}

Contraintes :
- Utiliser uniquement des personnes et organisations fictives.
- Ne demander aucun mot de passe ni donnée personnelle réelle.
- Ne fournir aucun lien externe opérationnel.
- Rédiger en français.
- Inclure des indices permettant de détecter la tentative.
- Fournir une explication pédagogique claire.
"""

debut = time.perf_counter()

response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Scenario,
        temperature=0.7,
    ),
)

duree = time.perf_counter() - debut
scenario = Scenario.model_validate_json(response.text)

print(json.dumps(
    scenario.model_dump(),
    ensure_ascii=False,
    indent=2
))

usage = response.usage_metadata

print(f"\nDurée : {duree:.2f} secondes")

if usage:
    print("Tokens entrée :", usage.prompt_token_count)
    print("Tokens sortie :", usage.candidates_token_count)
    print("Tokens totaux :", usage.total_token_count)
