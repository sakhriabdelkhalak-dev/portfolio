// Exercise the real submit handler without opening a mail client or sending mail.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const listeners = new Map();
const elements = new Map();
for (const id of ['menuToggle', 'navLinks', 'year', 'contactForm', 'formNote']) {
  elements.set(id, {
    addEventListener(name, handler) { listeners.set(`${id}:${name}`, handler); },
    querySelectorAll() { return []; },
    textContent: '',
  });
}
const fakeWindow = {location: {href: ''}};
const context = vm.createContext({
  window: fakeWindow,
  document: {getElementById: id => elements.get(id), addEventListener() {}},
  FormData: class { constructor(values) { this.values = values; } get(name) { return this.values[name]; } },
  Date,
});
vm.runInContext(fs.readFileSync(new URL('../script.js', import.meta.url), 'utf8'), context);
const submit = listeners.get('contactForm:submit');
assert.equal(typeof submit, 'function');
let prevented = false;
submit({preventDefault() { prevented = true; }, currentTarget: {
  name: 'Test & Démo', email: 'tester@example.com', message: 'Bonjour\nQuestion ? & réponse',
}});
assert.ok(prevented);
const composed = new URL(fakeWindow.location.href);
assert.equal(composed.protocol, 'mailto:');
assert.equal(composed.pathname, 'sakhriabdelkhalak@gmail.com');
assert.equal(composed.searchParams.get('subject'), 'Contact portfolio — Test & Démo');
assert.equal(composed.searchParams.get('body'), 'Nom : Test & Démo\nEmail : tester@example.com\n\nBonjour\nQuestion ? & réponse');
fakeWindow.location.href = '';
submit({preventDefault() {}, currentTarget: {name: ' ', email: 'tester@example.com', message: ' '}});
assert.equal(fakeWindow.location.href, '', 'Empty fields must not open an email draft');
console.log('Contact passed: correct recipient, accents/special characters, line breaks and empty-field handling. No email was sent.');
