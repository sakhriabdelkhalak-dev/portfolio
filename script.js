const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');

menuToggle.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(isOpen));
});

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    menuToggle.setAttribute('aria-expanded', 'false');
  });
});

document.getElementById('year').textContent = new Date().getFullYear();

document.getElementById('contactForm').addEventListener('submit', (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const name = form.get('name');
  const email = form.get('email');
  const message = form.get('message');
  // Replace this address with your real email before publishing.
  const destination = 'VOTRE-EMAIL@example.com';
  const subject = encodeURIComponent(`Message portfolio de ${name}`);
  const body = encodeURIComponent(`Nom : ${name}\nEmail : ${email}\n\nMessage :\n${message}`);
  document.getElementById('formNote').textContent =
    'Votre application de messagerie va s’ouvrir. Remplacez d’abord l’adresse e-mail dans script.js.';
  window.location.href = `mailto:${destination}?subject=${subject}&body=${body}`;
});
