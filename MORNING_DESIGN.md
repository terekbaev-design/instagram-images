# Carrousel du matin — design OBLIGATOIRE

Règle de l'utilisateur (05/10/2026) : le carrousel du matin (formation des brokers StepDream) a TOUJOURS ce design, sans exception :

- Fond clair lavande (dégradé), logo STEP DREAM Real Estate L.L.C. en haut à gauche (refs/style-cover.jpg), compteur « 01 / 08 » en haut à droite
- Titres en capitales (Oswald), première ligne en noir, mot-clé en violet
- Une photo de Dubaï par slide, étalonnage violet-bleu, fondue à droite ou en bas
- Cartes blanches avec icônes violettes, bouton « Листай » sur la slide 1
- **Slide 1 : TOUJOURS le rond avec la photo de Беслан** (`refs/beslan-circle.jpg`, logo STEP DREAM dans le cercle au-dessus de sa tête), en haut à droite, anneau violet + bordure blanche, et **le nom « Беслан Терекбаев » dessous** (règle du 07/10/2026). Dessiné automatiquement par `compose.py` sur la slide n° 1 ; le titre reste à gauche du rond.
- **Dernière slide : TOUJOURS la slide d'abonnement** `{"n": N, "kind": "subscribe"}` : « ПОДПИШИСЬ, ЧТОБЫ НЕ ПРОПУСТИТЬ », « Каждый день здесь выходит новое бесплатное обучение для брокеров. », ✓ Бесплатно / Новый урок каждое утро / Практика, а не теория, bouton « Подписаться + ». Texte fixe dans `compose.py`, ne pas le réécrire. La check-list récap et « Напишите «БРОКЕР» в Direct » passent sur l'avant-dernière slide.
- Pied de page « STEP DREAM / ПРАКТИКА БРОКЕРА » et @terekbaev

Toujours produit avec `tools/compose.py` à partir d'un spec JSON (texte posé en code, jamais généré par l'IA dans l'image) :
`python3 compose.py spec.json fv ref.jpg ph out beslan-circle.jpg` (6e argument = refs/beslan-circle.jpg). compose.py refuse de tourner si la dernière slide n'est pas `subscribe` ou si la photo du rond manque.
Interdit : tout autre design (fond bleu nuit, doré, slides générées entièrement par un modèle d'image, etc.).

Références validées : tools/spec-2026-10-04.json, tools/spec-2026-10-05.json.
