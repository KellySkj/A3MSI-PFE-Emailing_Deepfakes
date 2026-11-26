
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
    html_email : str
    indices_suspects: list[str]
    explication_pedagogique: str
    difficulte: str

def generate_scenario(contexte):

    prompt = f"""
    Tu conçois des exercices avancés de sensibilisation à la cybersécurité.

    Crée un scénario fictif de phishing par e-mail destiné
    à une simulation autorisée dans une entreprise pilote.

    Contexte professionnel :
    {json.dumps(contexte, ensure_ascii=False)}

    Le scénario doit être pertinent pour l'ensemble des postes
    représentés dans ce service.
    Ne suppose pas que tous les destinataires ont les mêmes
    responsabilités.

    OBJECTIF : DIFFICULTÉ TRÈS AVANCÉE

    Le scénario doit être réaliste et subtil.
    Il doit pouvoir sembler crédible lors d'une première lecture,
    sans contenir de signes caricaturaux de phishing.

    Contraintes rédactionnelles :
    - Rédiger en français naturel et professionnel.
    - Adapter le prétexte au service et aux postes concernés.
    - Utiliser un contexte de travail plausible et cohérent.
    - Employer un ton professionnel, sans fautes volontaires.
    - Éviter les formulations excessivement alarmistes.
    - Ne pas utiliser systématiquement une échéance urgente.
    - Éviter les signatures volontairement génériques ou suspectes.
    - Ne pas rendre les indices de détection trop évidents.
    - Ne pas inventer de procédures internes présentées comme réelles.
    - Le mail doit être adressé à une seule personne.
    - Commencer obligatoirement le corps du mail par "Bonjour {{PRENOM}},"
    - Ne jamais utiliser "Bonjour à toute l'équipe" ou une formule collective.
    - Conserver exactement le placeholder {{PRENOM}} dans le corps du mail.
    - Reprendre exactement ce même placeholder dans la version HTML.
    - Relire l'explication pédagogique pour éviter les erreurs de français.
    - Ne pas utiliser de termes incohérents avec le contexte professionnel.

    Contraintes de sécurité :
    - Utiliser uniquement des personnes et organisations fictives.
    - Ne demander aucun mot de passe, identifiant ou donnée personnelle.
    - Ne demander aucun paiement, virement ou changement de coordonnées bancaires.
    - Ne générer aucune URL, aucun lien cliquable ni domaine externe.
    - Ne créer aucun formulaire ou mécanisme de collecte.
    - Si une action est proposée, elle doit rester simulée et sans effet réel.

    Contenu pédagogique :
    - Inclure plusieurs indices suspects, mais discrets.
    - Les indices doivent être cohérents avec le scénario.
    - Expliquer précisément pourquoi ils doivent éveiller les soupçons.
    - Ne pas révéler les indices dans le corps du mail.

    Version HTML :
    - Générer une version HTML professionnelle du corps du mail.
    - Conserver exactement le même contenu et le même sens.
    - Utiliser du CSS inline et une mise en page responsive.
    - Utiliser uniquement des éléments compatibles avec les clients mail.
    - Ne pas utiliser JavaScript, de ressources externes ou de liens.
    - Ne pas utiliser de balise <a>.

    Difficulté :
    - Le champ difficulte doit obligatoirement être :
      "Très avancée"

    Retourner uniquement les champs définis dans le schéma Scenario.
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
    return {'scenario': scenario.model_dump(), 'duree': duree, 'usage': response.usage_metadata}

if __name__ == "__main__":
    contexte_test = {
        "service": "Comptabilite",
        "postes": [
            "Assistant comptable",
            "Assistante comptable",
            "Comptable",
            "Responsable comptable"
        ],
        "difficulte": "Avancee",
        "objectif": "Reconnaître une demande inhabituelle urgente"
    }

    resultat = generate_scenario(contexte_test)

    print(json.dumps(resultat['scenario'], ensure_ascii=False, indent=2))

    print(f"\nDurée : {resultat['duree']:.2f} secondes")

    usage = resultat['usage']

    if usage:
        print("Tokens entrée :", usage.prompt_token_count)
        print("Tokens sortie :", usage.candidates_token_count)
        print("Tokens totaux :", usage.total_token_count)