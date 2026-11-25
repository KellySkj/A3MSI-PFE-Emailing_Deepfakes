import fs from "fs";
const path = "./exportGroupMembers_2026-11-18.csv";

function cleanEmail(email) {
  if (!email) return "";
  if (email.includes("#EXT#")) {
    const [partieExterne, domaineInterne] = email.split("#EXT#"); // ["aurelie.nass_esme.fr", "@test1PFE.onmicrosoft.com"]
    const dernierUnderscore = partieExterne.lastIndexOf("_");

    if (dernierUnderscore !== -1) {
      const identifiant = partieExterne.slice(0, dernierUnderscore); // "aurelie.nass"
      return identifiant + domaineInterne.trim(); // "aurelie.nass@test1PFE.onmicrosoft.com"
    }
  }
  return email.trim().toLowerCase();
}

function readCSVFile(filePath) {
  const data = fs.readFileSync(filePath, "utf-8").replace(/^\uFEFF/, ""); // Remove BOM if present
  const lines = data.split("\n");
  if (lines.length < 2) {
    throw new Error("CSV file is empty or does not contain enough data.");
  }
  const delimiter = lines[0].includes(",") ? "," : ";";
  const headers = lines[0]
    .split(delimiter)
    .map((col) => col.replace(/"|"$/g, "").trim());

  const indexDisplayName = headers.indexOf("displayName");
  const indexUpn = headers.indexOf("userPrincipalName");

  if (indexDisplayName === -1 || indexUpn === -1) {
    throw new Error(
      "CSV file does not contain required headers: displayName and userPrincipalName.",
    );
  }

  console.log("========Liste des utilsateurs========");
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]
      .split(delimiter)
      .map((col) => col.replace(/"|"$/g, "").trim());
    const name = line[indexDisplayName];
    const email = cleanEmail(line[indexUpn]);
    console.log(`Nom: ${name}, Email: ${email}`);
  }
}

readCSVFile(path);
