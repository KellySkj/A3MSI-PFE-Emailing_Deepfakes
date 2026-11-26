import express from "express";
import {sendMail} from "./email/emailService.js";
import {verifyMailer} from "./config/mailer.js";
import {generateScenario} from "./gemini/geminiClient.js";

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

// essai generation de mail
app.post("/emails/generate", async (req, res) => {
    try {
        const scenario = await generateScenario(req.body.contexte);

        res.json({
            message: "Scénario généré avec succès",
            scenario
        });

    } catch (error) {
        console.error("Erreur de génération :", error);

        res.status(500).json({
            error: "Impossible de générer le scénario"
        });
    }
});

// Envoi de mails générés
app.post("/emails/generate-and-send", async (req, res) => {
    try {
        // 1. Générer le scénario avec Gemini
        const scenario = await generateScenario(req.body.contexte);

        // 2. Envoyer le mail avec Nodemailer
        const info = await sendMail(
            req.body.to,
            scenario.objet_email,
            scenario.corps_email,
            scenario.html_email
        );

        // 3. Retourner le résultat
        res.json({
            message: "Scénario généré et email envoyé avec succès",
            messageId: info.messageId,
            scenario: scenario
        });

    } catch (error) {
        console.error("Erreur lors de la génération ou de l'envoi :", error);

        res.status(500).json({
            error: "Impossible de générer ou envoyer le mail"
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
