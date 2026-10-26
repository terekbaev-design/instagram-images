# Design du carrousel éducatif (validé par l'utilisateur le 26/10/2026)

Remplace l'ancien design lavande de MORNING_DESIGN.md (abandonné le 26/10/2026).
Même style que les carrousels actu Dubaï du soir (evening/2026-10-03).

- Format 1080×1350 (4:5), JPEG.
- Fond : une photo DIFFÉRENTE par slide, réaliste, chaude et sombre (coucher de soleil, heure bleue, nuit),
  dégradé noir vers le bas pour la lisibilité. Pas de visages en gros plan (personnes de dos ou de loin).
- Titres : Oswald gras, capitales, jaune (#F5C400) et blanc. Texte : Roboto, blanc.
- Gros numéro doré dégradé « 01 », « 02 »… en haut à gauche des slides de conseil.
- Compteur « 01 / 08 » en haut à droite (01 en jaune), flèches à chevrons jaunes.
- Phrase prête à dire : encadré sombre à bord jaune, texte jaune entre guillemets.
- Slide 1 : rond photo de Беслан (refs/beslan-circle.jpg) en haut à gauche, anneau jaune, nom dessous ;
  titre en 2–3 lignes + sous-titre + bouton jaune « ЛИСТАЙ ›››».
- Avant-dernière : check-list sur panneau sombre + bouton « НАПИШИТЕ «БРОКЕР» В DIRECT ».
- Dernière : abonnement fixe « ОБУЧЕНИЕ ДЛЯ БРОКЕРОВ КАЖДЫЙ ВЕЧЕР », grand rond photo, « ПОДПИСАТЬСЯ + ».

Outil : `tools/edu_compose.py` (texte posé en code) — exemple validé : `tools/spec-edu-exemple.json`.

## Photos (Higgsfield z_image, 3:4)
Varier les sujets à chaque carrousel et à chaque slide, en lien avec le thème :
- Immobilier : intérieurs de luxe, salon avec vue, villa avec piscine, penthouse, clés remises,
  chantier de tour avec grues, maquette architecturale, hall d'immeuble, terrasse, vue aérienne d'un quartier
  (Downtown, Marina, Palm Jumeirah, Business Bay, Creek Harbour, JVC, Dubai Hills).
- Formation / travail : salle de réunion avec vue, mentor et élève de dos, bureau d'agence, carnet et stylo
  sur une table (sans écriture lisible), séance de travail en équipe, café de travail à Dubaï.
- Dubaï : skyline, Burj Khalifa, Sheikh Zayed Road, marina, plage JBR, Museum of the Future vu de loin.
Chaque prompt se termine par : « warm golden-hour or night light, dark lower third, cinematic, photorealistic.
Absolutely no text, no letters, no signs, no logos, no documents, no papers, no screens. »
Ne jamais générer Беслан avec l'IA. Une génération à la fois (generate_image_batch avec 1 requête puis jobs_wait).
