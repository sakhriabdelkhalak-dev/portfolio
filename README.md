# Portfolio de Sakhri Abdelkhalak

Portfolio personnel en français : projets web, compétences, parcours,
CV et coordonnées professionnelles.

[Consulter le portfolio](https://sakhriabdelkhalak-dev.github.io/portfolio/)

## Structure

- `index.html` : page statique générée.
- `portfolio.css` : présentation responsive du portfolio.
- `script.js` : menu accessible, navigation et préparation d’un email.
- `assets/` : portrait, captures réelles des projets et favicon.
- `CV_Sakhri_Abdelkhalak.pdf` : CV fourni par l’auteur.
- `demos/` : versions statiques des projets WordPress.
- `tools/` : génération, export et vérifications.

## Mettre à jour le contenu

Modifier les informations dans `tools/build_portfolio.py`, puis exécuter :

```sh
python tools/build_portfolio.py
```

Les projets personnels et adaptations de modèles sont identifiés dans les
cartes. Les captures montrent les sites de démonstration réellement publiés.

## Vérifier et prévisualiser

La vérification HTML utilise Python avec `lxml`. La vérification du formulaire
utilise uniquement les modules intégrés de Node.js et n’envoie aucun email.

```sh
python tools/verify_portfolio.py
node tools/verify_contact.mjs
node tools/verify_cap_pro.cjs
python -m http.server 8766 --bind 127.0.0.1
```

La publication sur GitHub Pages se fait depuis la racine de la branche `main`.
Le site ne nécessite aucun serveur PHP ni étape de compilation.

Le formulaire du portfolio prépare un email dans la messagerie du visiteur ;
il n’effectue pas d’envoi côté serveur. Les formulaires des démos WordPress
sont désactivés et identifiés comme démonstrations.

Pour réexporter les projets WordPress, consulter [les outils](tools/README.md).

## Cap Pro

[Ouvrir l’application](https://sakhriabdelkhalak-dev.github.io/portfolio/demos/cap-pro/)

Cap Pro est une application originale de suivi des candidatures, conçue avec
assistance IA : tableau de bord, recherche, relances, liste/tableau, corbeille
et export CSV. Son espace personnel est sauvegardé dans le navigateur.
Le mode démo est séparé et utilise uniquement des exemples fictifs.
Consulter [le projet et ses limites](demos/cap-pro/README.md).
