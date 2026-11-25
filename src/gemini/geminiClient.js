// Intermédiaire entre backend Node et API FastAPI


const GEMINI_API_URL = "http://127.0.0.1:8001/generate";

export async function generateScenario(contexte) {
    const response = await fetch(GEMINI_API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({contexte})
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Erreur API Python (${response.status}) : ${error}`);
    }

    const scenario = await response.json();

    return scenario;
}
