// Intermédiaire entre backend Node et API FastAPI

const PYTHON_API_URL = "http://127.0.0.1:8001";

// Demande à Python de générer un scénario avec Gemini
export async function generateScenario(contexte) {
    const response = await fetch(`${PYTHON_API_URL}/generate`, {
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

// Demande à Python les informations d'un service depuis SQLite via FastAPI
export async function getServiceData(service) {
    const response = await fetch(
        `${PYTHON_API_URL}/services/${encodeURIComponent(service)}`
    );

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Erreur API Python (${response.status}) : ${error}`);
    }

    return await response.json();
}
