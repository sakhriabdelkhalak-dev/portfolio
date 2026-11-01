# Cap Pro

Application de suivi des candidatures conçue avec assistance IA pour le
portfolio de Sakhri Abdelkhalak. HTML, CSS et JavaScript natifs, sans compilation
ni serveur d’application.

## Fonctionnalités

- Tableau de bord et distribution des statuts.
- Ajout, modification et changement de statut d’une candidature.
- Dates de suivi et vue des relances dues, sans envoi automatique de messages.
- Recherche insensible aux accents, filtres et tri.
- Affichage en liste ou en tableau par statut.
- Corbeille avec restauration, sans suppression définitive.
- Export CSV de la vue affichée, avec accents, guillemets et retours à la ligne.
- Espace personnel conservé dans le navigateur et démonstration indépendante.

Les entreprises et candidatures de la démo sont fictives. Les modifications de
ces exemples ne sont pas conservées. Une nouvelle candidature est toujours
ajoutée à l’espace personnel, même lorsqu’elle est créée depuis la démo.

## Exécuter et vérifier

Depuis la racine du dépôt :

```sh
python -m http.server 8766 --bind 127.0.0.1
node tools/verify_cap_pro.cjs
```

Ouvrir `http://127.0.0.1:8766/demos/cap-pro/`.

`core.js` contient les règles de validation, dates, filtres, statistiques et
export. `app.js` gère l’interface et le stockage. `app.css` couvre les mises en
page ordinateur et mobile. Les vérifications du cœur n’utilisent aucune
dépendance externe.

## Données

Les données ne sont transmises à aucun serveur. L’espace personnel utilise la
clé locale `cap-pro.records.v1`; le choix démo/personnel utilise une clé distincte.
Les données sont propres à un navigateur et à une adresse de site : elles ne
synchronisent pas entre appareils et peuvent disparaître si le stockage du
navigateur est effacé. Le CSV permet d’en garder une copie ; il n’existe pas
d’import automatique. Un échec de stockage est signalé, sans écraser des données
illisibles existantes.

Les liens d’offres sont limités à HTTP/HTTPS, les saisies affichées sont échappées,
et les cellules CSV pouvant être interprétées comme des formules sont protégées.
