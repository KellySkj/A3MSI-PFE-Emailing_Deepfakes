import express from "express";
import {sendMail} from "./email/emailService.js";
import {verifyMailer} from "./config/mailer.js";
import {generateScenario, getServiceData} from "./gemini/geminiClient.js";

// Création de l'application Express
const app = express();

// Port du serveur
const PORT = 3000;

// Permet de lire les données JSON reçues
app.use(express.json());

app.get("/health", (req, res) => {
    res.json({
        "status": "ok",
        "message": "API is running"
    })
})

// Génération d'un scénario à partir des données AD
app.post("/emails/generate", async (req, res) => {
    try {
        // 1. Récupérer le service demandé
        const {service} = req.body;

        if (!service) {
            return res.status(400).json({
                error: "Le service est obligatoire"
            });
        }

        // 2. Récupérer les données depuis SQLite via Python
        const data = await getServiceData(service);

        // 3. Envoyer uniquement le contexte professionnel à Gemini
        const contexteGemini = {
            ...data.contexte,
            difficulte: "Très avancée",
            objectif: "Évaluer la capacité à identifier une demande professionnelle inhabituelle"
        };

        const scenario = await generateScenario(contexteGemini);

        // 4. Sélectionner un employé pour le test
        const employeTest = data.employes.find(
            employe => employe.prenom === "Thomas"
        );

        if (!employeTest) {
            throw new Error("Employé de test introuvable");
        }

        const personnaliser = (contenu, prenom) => {
            return contenu
                .replaceAll("{{PRENOM}}", prenom)
                .replaceAll("{PRENOM}", prenom);
        };
        // 5. Personnaliser le corps du mail
        const emailPersonnalise = {
            objet: scenario.objet_email,
            texte: personnaliser(scenario.corps_email, employeTest.prenom),
            html: personnaliser(scenario.html_email, employeTest.prenom)
        };

        // 6. Retourner le résultat
        res.json({
            message: "Scénario généré et personnalisé avec succès",
            service: data.contexte.service,
            nombreDestinataires: data.employes.length,
            employeTest: employeTest.prenom,
            scenario,
            apercu: emailPersonnalise
        });

    } catch (error) {
        console.error("Erreur de génération :", error);

        res.status(500).json({
            error: "Impossible de générer le scénario"
        });
    }
});

const testEmail = process.env.TEST_EMAIL;
if (!testEmail) {
    throw new Error("TEST_EMAIL n'est pas configuré");
}

// Envoi de mails générés et personnalisés
app.post("/emails/generate-and-send", async (req, res) => {
    try {
        const {service} = req.body;

        if (!service) {
            return res.status(400).json({
                error: "Le service est obligatoire"
            });
        }

        // 1. Récupérer les employés et le contexte depuis SQLite
        const data = await getServiceData(service);

        // 2. Préparer le contexte pour Gemini
        const contexteGemini = {
            ...data.contexte,
            difficulte: "Très avancée",
            objectif: "Évaluer la capacité à identifier une demande professionnelle inhabituelle"
        };

        // 3. Générer le scénario
        const scenario = await generateScenario(contexteGemini);

        // 4. Sélectionner notre employé fictif
        const employeTest = data.employes.find(
            employe => employe.prenom === "Thomas"
        );

        if (!employeTest) {
            throw new Error("Employé de test introuvable");
        }

        // 5. Personnaliser le mail
        const personnaliser = (contenu, prenom) => {
            return contenu
                .replaceAll("{{PRENOM}}", prenom)
                .replaceAll("{PRENOM}", prenom);
        };

        const texte = personnaliser(
            scenario.corps_email,
            employeTest.prenom
        );

        const html = personnaliser(
            scenario.html_email,
            employeTest.prenom
        );

        // 6. Envoyer uniquement à notre adresse de test
        const info = await sendMail(
            testEmail,
            scenario.objet_email,
            texte,
            html
        );

        res.json({
            message: "Email de test envoyé avec succès",
            mode: "test",
            employeSimule: employeTest.prenom,
            messageId: info.messageId,
            scenario
        });

    } catch (error) {
        console.error("Erreur lors de l'envoi :", error);

        res.status(500).json({
            error: "Impossible de générer et envoyer le mail"
        });
    }
});

// Récupération des données d'un service
app.get("/services/:service", async (req, res) => {
    try {
        const data = await getServiceData(req.params.service);

        res.json(data);

    } catch (error) {
        console.error("Erreur de récupération :", error);

        res.status(500).json({
            error: "Impossible de récupérer les données du service"
        });
    }
});

// envoi de mails test
app.post("/emails/send", async (req, res) => {
    try {
        const info = await sendMail(
            req.body.to,
            req.body.subject,
            req.body.content
        );

        res.json({
            message: "Email envoyé avec succès",
            messageId: info.messageId,
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({error: "Erreur lors de l'envoi"});
    }
});

verifyMailer().then(() => console.log('Connexion SMTP réussie')).catch((error) => console.log('Erreur SMTP :', error));

// Démarrage du serveur
app.listen(PORT, () => {
    console.log(`Serveur démarré sur le port ${PORT}`);
});
