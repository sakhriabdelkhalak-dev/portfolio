"""Build the static French portfolio from verified CV and project information."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
projects = [
    dict(id='finovate', title='Finovate', category='Site vitrine', kind='Démonstration',
         image='finovate-preview.jpg', url='demos/finovate/', tags=['WordPress', 'Elementor', 'Astra'],
         description='Un site de présentation autour des services financiers, avec plusieurs pages et une navigation commune.',
         role='Adaptation d’un modèle WordPress, mise en page Elementor et intégration des contenus.'),
    dict(id='cap-pro', title='Cap Pro', category='Application web', kind='Application originale',
         image='cap-pro-preview.jpg', url='demos/cap-pro/', tags=['JavaScript', 'HTML / CSS', 'Stockage local'],
         description='Une application de suivi des candidatures : tableau de bord, recherche, statuts, relances et export CSV.',
         role='Conception avec assistance IA, interface responsive, gestion des données locales et vérification des interactions.'),
    dict(id='loop-market', title='Loop Market', category='E-commerce', kind='Application originale',
         image='loop-market-preview.jpg', url='demos/loop-market/', tags=['JavaScript', 'HTML / CSS', 'Stockage local'],
         description='Une petite boutique audio : six produits, recherche, filtres, favoris et panier avec récapitulatif simulé.',
         role='Conception avec assistance IA, interface responsive, visuels générés et gestion du panier. Démonstration sans paiement réel.'),
    dict(id='dar-el-grill', title='Dar El Grill', category='Restaurant', kind='Démonstration',
         image='dar-el-grill-preview.jpg', url='https://sakhriabdelkhalak-dev.github.io/dar-el-grill/', tags=['HTML', 'CSS', 'JavaScript'],
         description='Un site de restaurant qui présente les spécialités, le menu et l’univers de l’établissement.',
         role='Intégration HTML et CSS, menu filtrable en JavaScript et adaptation aux écrans mobiles.'),
    dict(id='marketing-agency', title='Marketing Agency', category='Agence', kind='Démonstration',
         image='marketing-agency-preview.jpg', url='demos/marketing-agency/', tags=['WordPress', 'Neve'],
         description='Un site d’agence avec présentation des activités, réalisations, blog et page de contact.',
         role='Adaptation du thème Neve, personnalisation de l’accueil et organisation des pages.'),
    dict(id='avengers', title='Avengers Assemble', category='Site thématique', kind='Projet personnel',
         image='avengers-preview.jpg', url='demos/avengers/', tags=['WordPress', 'Elementor', 'Astra'],
         description='Un projet consacré aux héros Marvel, avec des pages de personnages et une galerie de visuels.',
         role='Création de pages Elementor, intégration des images, onglets et carrousels.'),
]

def tags(items):
    return '<ul class="tags">' + ''.join(f'<li>{escape(item)}</li>' for item in items) + '</ul>'

def card(project, index):
    p = {key: escape(value) if isinstance(value, str) else value for key, value in project.items()}
    return f'''<article class="project-card" id="{p['id']}">
      <a class="project-preview" href="{p['url']}" target="_blank" rel="noopener" aria-label="Voir le site {p['title']} (nouvel onglet)"><img src="assets/{p['image']}" alt="Capture réelle du site {p['title']}" width="1265" height="721" loading="lazy"></a>
      <div class="project-info"><div class="project-topline"><span>{index:02d} / {p['category']}</span><span class="project-kind">{p['kind']}</span></div><h3>{p['title']}</h3><p>{p['description']}</p><p class="project-role"><strong>Mon travail :</strong> {p['role']}</p>{tags(project['tags'])}<a class="project-link" href="{p['url']}" target="_blank" rel="noopener">Voir le projet <span aria-hidden="true">↗</span><span class="sr-only"> {p['title']} (nouvel onglet)</span></a></div>
    </article>'''

def timeline(items):
    return '<ol class="timeline">' + ''.join(f'<li><span class="timeline-date">{escape(date)}</span><h4>{escape(title)}</h4><p>{escape(place)}</p></li>' for date, title, place in items) + '</ol>'

cards = '\n'.join(card(project, i) for i, project in enumerate(projects, 1))
experience = timeline([
    ('2019 — 2022', 'Service de vente', 'TechWoodArt · Tanger'),
    ('2015 — 2018', 'Opérateur', 'Yazaki · Tanger'),
    ('Avril — Mai 2015', 'Service à l’ONEP', 'ONEP · Ouezzane'),
])
education = timeline([
    ('2012 — 2014', 'Technicien spécialisé en développement informatique', 'Institut Spécialisé de Technologie Appliquée · Ouezzane'),
    ('2011 — 2012', 'Baccalauréat scientifique — Sciences physiques', 'Lycée Ibn Zohr · Ouezzane'),
])

page = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Sakhri Abdelkhalak, développeur web à Mohammedia : WordPress, Elementor, HTML, CSS et JavaScript. Découvrez ses projets et son parcours.">
  <meta name="theme-color" content="#0a1116">
  <meta property="og:title" content="Sakhri Abdelkhalak — Développeur web">
  <meta property="og:description" content="Projets web, WordPress et Elementor. Basé à Mohammedia, Maroc.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://sakhriabdelkhalak-dev.github.io/portfolio/">
  <title>Sakhri Abdelkhalak | Développeur Web — WordPress &amp; Elementor</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="portfolio.css?v=20261101-pro">
</head>
<body>
  <a class="skip-link" href="#contenu">Aller au contenu</a>
  <header class="site-header"><nav class="nav container" aria-label="Navigation principale">
    <a class="brand" href="#accueil" aria-label="Sakhri Abdelkhalak — accueil"><span class="brand-mark" aria-hidden="true">SA</span><span>Sakhri Abdelkhalak</span></a>
    <button class="menu-toggle" id="menuToggle" aria-label="Ouvrir le menu" aria-controls="navLinks" aria-expanded="false" type="button"><span aria-hidden="true">☰</span></button>
    <div class="nav-links" id="navLinks"><a href="#projets">Projets</a><a href="#competences">Compétences</a><a href="#apropos">Parcours</a><a class="mobile-cv-link" href="#cv">Mon CV</a><a href="#contact">Contact</a></div>
    <a class="btn btn-outline nav-cta" href="#cv">Mon CV <span aria-hidden="true">↗</span></a>
  </nav></header>
  <main id="contenu">
    <section class="hero section" id="accueil" aria-labelledby="hero-title"><div class="container hero-grid">
      <div class="hero-copy"><p class="eyebrow"><span class="status-dot" aria-hidden="true"></span>Développement web · Mohammedia, Maroc</p><h1 id="hero-title">Sakhri<br><span>Abdelkhalak.</span></h1><h2>Développeur web<br>WordPress &amp; Elementor</h2><p class="hero-text">Je réalise des sites vitrines et des projets web avec WordPress, Elementor, HTML, CSS et JavaScript. Je recherche une opportunité en développement web ou en support informatique.</p><div class="hero-actions"><a class="btn" href="#projets">Découvrir mes projets <span aria-hidden="true">↘</span></a><a class="btn btn-outline" href="#contact">Me contacter</a></div><div class="social-links"><a href="https://github.com/sakhriabdelkhalak-dev" target="_blank" rel="noopener noreferrer">GitHub ↗<span class="sr-only"> (nouvel onglet)</span></a><a href="mailto:sakhriabdelkhalak@gmail.com">Écrire un email ↗</a></div></div>
      <aside class="profile-card" aria-label="Mon profil"><div class="portrait-wrap"><img class="portrait" src="assets/portrait-sakhri.jpg" alt="Portrait de Sakhri Abdelkhalak" width="323" height="433" fetchpriority="high"></div><div class="profile-info"><p class="profile-kicker">Mon profil</p><p class="profile-diploma">Technicien spécialisé<br>en développement informatique</p><p class="profile-location">Mohammedia, Maroc<br><span>Télétravail ou présentiel</span></p><a href="#cv" class="text-link">Consulter mon CV ↗</a></div></aside>
    </div></section>
    <section class="section projects-section" id="projets" aria-labelledby="projects-title"><div class="container">
      <div class="section-heading heading-row"><div><p class="eyebrow">Une sélection de réalisations</p><h2 id="projects-title">Mes projets web<span class="accent">.</span></h2></div><p>Des projets personnels pour mettre mes compétences en pratique, du site vitrine à l’intégration web.</p></div>
      <div class="project-grid">__PROJECTS__</div>
      <p class="projects-note">Les sites WordPress sont présentés dans des versions de démonstration. Leurs formulaires ne transmettent pas de messages.</p>
    </div></section>
    <section class="section skills-section" id="competences" aria-labelledby="skills-title"><div class="container">
      <div class="section-heading"><p class="eyebrow">Outils &amp; pratique</p><h2 id="skills-title">Mes compétences<span class="accent">.</span></h2><p>Des technologies utilisées dans mes projets, complétées par ma formation en développement informatique.</p></div>
      <div class="skills-grid">
        <article class="skill-group"><span class="skill-number" aria-hidden="true">01</span><h3>WordPress &amp; intégration</h3><p>Mise en page avec Elementor, personnalisation de thèmes et organisation de sites de présentation.</p>__WP_TAGS__<a class="text-link" href="#finovate">Voir Finovate ↗</a></article>
        <article class="skill-group"><span class="skill-number" aria-hidden="true">02</span><h3>Développement web</h3><p>Intégration de pages, styles adaptés aux différentes tailles d’écran et interactions en JavaScript.</p>__WEB_TAGS__<a class="text-link" href="#cap-pro">Voir Cap Pro ↗</a></article>
        <article class="skill-group"><span class="skill-number" aria-hidden="true">03</span><h3>Bases &amp; outils</h3><p>Connaissances en programmation, bases de données et algorithmique. Publication de projets avec GitHub Pages.</p>__TOOLS_TAGS__<a class="text-link" href="#cv">Consulter mon parcours ↗</a></article>
      </div><p class="tools-note">Également dans ma boîte à outils : Word, Excel, PowerPoint, Photoshop et Inkscape.</p>
    </div></section>
    <section class="section about-section" id="apropos" aria-labelledby="about-title"><div class="container">
      <div class="about-intro"><div><p class="eyebrow">À propos de moi</p><h2 id="about-title">Un parcours polyvalent,<br>une orientation web<span class="accent">.</span></h2></div><div><p>Diplômé en développement informatique, j’ai travaillé dans la vente et en entreprise. Mes projets personnels me permettent aujourd’hui de développer ma pratique du web.</p><p>Je souhaite rejoindre une équipe en développement web ou en support informatique, à distance ou en présentiel. En dehors de l’informatique, je pratique la guitare.</p></div></div>
      <div class="journey-grid" id="parcours"><div class="journey-column"><h3>Expérience professionnelle</h3>__EXPERIENCE__</div><div class="journey-column"><h3>Formation</h3>__EDUCATION__</div></div>
      <div class="languages"><h3>Langues</h3><ul><li><strong>Arabe</strong><span>Langue maternelle</span></li><li><strong>Anglais</strong><span>Bon niveau</span></li><li><strong>Français</strong><span>Niveau moyen</span></li><li><strong>Allemand</strong><span>Niveau moyen</span></li></ul></div>
    </div></section>
    <section class="section cv-section" id="cv" aria-labelledby="cv-title"><div class="container"><div class="cv-banner"><div><p class="eyebrow">Mon parcours en un document</p><h2 id="cv-title">Mon CV</h2><p>Retrouvez ma formation, mes expériences et mes compétences dans mon CV au format PDF.</p></div><div class="cv-actions"><a class="btn" href="CV_Sakhri_Abdelkhalak.pdf" target="_blank" rel="noopener">Voir mon CV ↗<span class="sr-only"> (PDF, nouvel onglet)</span></a><a class="btn btn-outline" href="CV_Sakhri_Abdelkhalak.pdf" download="CV-Sakhri-Abdelkhalak.pdf">Télécharger le PDF ↓</a></div></div></div></section>
    <section class="section contact-section" id="contact" aria-labelledby="contact-title"><div class="container contact-grid">
      <div class="contact-copy"><p class="eyebrow">Échangeons</p><h2 id="contact-title">Une opportunité<br>ou un projet<span class="accent"> ?</span></h2><p>Vous recherchez un profil pour un poste en développement web ou en support informatique ? Je serai heureux d’échanger avec vous.</p><ul class="contact-list"><li><span>Email</span><a href="mailto:sakhriabdelkhalak@gmail.com">sakhriabdelkhalak@gmail.com</a></li><li><span>Téléphone</span><a href="tel:+212601345358">+212 6 01 34 53 58</a></li><li><span>Localisation</span><p>Mohammedia, Maroc</p></li></ul><a class="text-link" href="https://github.com/sakhriabdelkhalak-dev" target="_blank" rel="noopener noreferrer">Mon profil GitHub ↗<span class="sr-only"> (nouvel onglet)</span></a></div>
      <form class="contact-form" id="contactForm" action="mailto:sakhriabdelkhalak@gmail.com" method="post" enctype="text/plain"><h3>Préparer un email</h3><div class="form-row"><label for="contactName">Votre nom<input id="contactName" name="name" autocomplete="name" required maxlength="100" placeholder="Nom et prénom"></label><label for="contactEmail">Votre email<input id="contactEmail" name="email" type="email" autocomplete="email" required maxlength="254" placeholder="vous@exemple.com"></label></div><label for="contactMessage">Votre message<textarea id="contactMessage" name="message" rows="5" required maxlength="5000" placeholder="Présentez votre projet ou votre opportunité…"></textarea></label><button class="btn" type="submit">Préparer l’email ↗</button><p class="form-note" id="formNote" role="status">Le bouton ouvre votre application de messagerie avec un email prérempli. L’envoi se fait depuis votre messagerie.</p><noscript><p class="form-note">Vous pouvez aussi m’écrire directement à <a href="mailto:sakhriabdelkhalak@gmail.com">sakhriabdelkhalak@gmail.com</a>.</p></noscript></form>
    </div></section>
  </main>
  <footer><div class="container footer-inner"><p>© <span id="year">2026</span> Sakhri Abdelkhalak</p><p>Développement web · Mohammedia, Maroc</p><a href="#accueil">Retour en haut ↑</a></div></footer>
  <script src="script.js?v=20261101-pro" defer></script>
</body>
</html>
'''
for key, value in {
    '__PROJECTS__': cards, '__EXPERIENCE__': experience, '__EDUCATION__': education,
    '__WP_TAGS__': tags(['WordPress', 'Elementor', 'Astra', 'Neve']),
    '__WEB_TAGS__': tags(['HTML', 'CSS', 'JavaScript']),
    '__TOOLS_TAGS__': tags(['PHP', 'MySQL', 'C# / C++', 'GitHub']),
}.items():
    page = page.replace(key, value)
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print(f'Portfolio HTML generated: {len(projects)} projects, one CV section, verified contact details.')
