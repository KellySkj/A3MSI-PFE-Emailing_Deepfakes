import express from "express";
import {sendMail} from "./email/emailService.js";
import {verifyMailer} from "./config/mailer.js";

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
