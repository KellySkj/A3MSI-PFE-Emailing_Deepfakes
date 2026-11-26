// Gestion de l'envoi des emails

import transporter from "../config/mailer.js";
import "dotenv/config";

export async function sendMail(to, subject, text, html) {
    const info = await transporter.sendMail({
        from: process.env.SMTP_USER,
        to,
        subject,
        text,
        html
    })

    return info;
}