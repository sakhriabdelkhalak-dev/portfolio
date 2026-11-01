/* Pure application logic shared by the interface and its regression tests. */
(function (root) {
  'use strict';
  const STATUSES = [
    {id: 'draft', label: 'À préparer', color: '#8a91a3'},
    {id: 'sent', label: 'Envoyée', color: '#5889c5'},
    {id: 'followed', label: 'Relancée', color: '#b48c43'},
    {id: 'interview', label: 'Entretien', color: '#4e8b76'},
    {id: 'offer', label: 'Offre reçue', color: '#9b78b4'},
    {id: 'closed', label: 'Clôturée', color: '#9b9da3'},
  ];
  const statusIds = new Set(STATUSES.map(status => status.id));
  const isTerminal = record => ['offer', 'closed'].includes(record.status);
  function isoDate(date = new Date()) {
    return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-');
  }
  function validDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return false;
    const [year, month, day] = value.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.getFullYear() === year && date.getMonth() === month - 1 && date.getDate() === day;
  }
  function normalize(input) {
    if (!input || typeof input !== 'object') throw new Error('Candidature invalide.');
    const record = {
      id: String(input.id || ''), company: String(input.company || '').trim(), role: String(input.role || '').trim(),
      status: input.status, appliedDate: input.appliedDate, followUp: input.followUp || '',
      url: String(input.url || '').trim(), notes: String(input.notes || '').trim(), deletedAt: input.deletedAt || null,
    };
    if (!record.id || record.id.length > 100) throw new Error('Identifiant invalide.');
    if (!record.company || record.company.length > 80 || !record.role || record.role.length > 100) throw new Error('Renseignez une entreprise et un poste.');
    if (!statusIds.has(record.status)) throw new Error('Choisissez un statut valide.');
    if (!validDate(record.appliedDate)) throw new Error('Choisissez une date de candidature valide.');
    if (record.followUp && (!validDate(record.followUp) || record.followUp < record.appliedDate)) throw new Error('La relance doit être à la date de candidature ou après.');
    if (record.url) {
      let parsed;
      try { parsed = new URL(record.url); } catch (_) { throw new Error('Le lien doit être une adresse http:// ou https:// valide.'); }
      if (!['http:', 'https:'].includes(parsed.protocol) || record.url.length > 1000) throw new Error('Le lien doit commencer par http:// ou https://.');
      record.url = parsed.href;
    }
    if (record.notes.length > 2000) throw new Error('Les notes sont limitées à 2 000 caractères.');
    if (record.deletedAt && !validDate(record.deletedAt)) throw new Error('Date d’archivage invalide.');
    return record;
  }
  const due = (record, today = isoDate()) => !record.deletedAt && record.status !== 'draft' && !isTerminal(record) && !!record.followUp && record.followUp <= today;
  function visible(records, options = {}) {
    const query = String(options.query || '').trim().toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const today = options.today || isoDate();
    const filtered = records.filter(record => {
      if (options.nav === 'trash' ? !record.deletedAt : !!record.deletedAt) return false;
      if (options.nav === 'due' && !due(record, today)) return false;
      if (options.nav === 'interview' && record.status !== 'interview') return false;
      if (options.status && record.status !== options.status) return false;
      const text = `${record.company} ${record.role} ${record.notes}`.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      return !query || text.includes(query);
    });
    return filtered.sort((a, b) => options.sort === 'company' ? a.company.localeCompare(b.company, 'fr') : options.sort === 'followup' ? (a.followUp || '9999').localeCompare(b.followUp || '9999') || b.appliedDate.localeCompare(a.appliedDate) : b.appliedDate.localeCompare(a.appliedDate) || a.company.localeCompare(b.company, 'fr'));
  }
  function metrics(records, today = isoDate()) {
    const active = records.filter(record => !record.deletedAt);
    return {total: active.length, pending: active.filter(record => !isTerminal(record) && record.status !== 'draft').length, interviews: active.filter(record => record.status === 'interview').length, due: active.filter(record => due(record, today)).length, trash: records.filter(record => record.deletedAt).length};
  }
  function toCSV(records) {
    const headers = ['Entreprise', 'Poste', 'Statut', 'Date de candidature', 'Prochaine relance', 'Lien', 'Notes', 'Dans la corbeille'];
    const cell = value => {
      let text = String(value ?? '');
      // Keep spreadsheet software from treating user-entered text as a formula.
      if (/^\s*[=+\-@]/.test(text) || /^[\t\r]/.test(text)) text = "'" + text;
      return '"' + text.replace(/"/g, '""') + '"';
    };
    const rows = records.map(record => [record.company, record.role, STATUSES.find(status => status.id === record.status)?.label || '', record.appliedDate, record.followUp, record.url, record.notes, record.deletedAt ? 'Oui' : 'Non']);
    return '\ufeff' + [headers, ...rows].map(row => row.map(cell).join(';')).join('\r\n');
  }
  function demoRecords(today = new Date()) {
    const date = offset => { const d = new Date(today.getFullYear(), today.getMonth(), today.getDate()); d.setDate(d.getDate() + offset); return isoDate(d); };
    const examples = [
      ['Atelier Horizon', 'Développeur web junior', 'interview', -8, 2, 'Préparer la présentation de mes projets.'],
      ['Studio Azur', 'Intégrateur WordPress', 'sent', -5, 0, 'Prévoir un message de suivi court et personnalisé.'],
      ['Nova Créative', 'Assistant support informatique', 'followed', -12, -1, 'Dernière relance envoyée la semaine passée.'],
      ['Collectif Bloom', 'Développeur front-end', 'sent', -3, 4, 'Relire la description du poste avant de relancer.'],
      ['Maison Pixel', 'Intégrateur web', 'draft', 0, 3, 'Adapter mon CV et sélectionner les projets à présenter.'],
      ['Équipe Latitude', 'Technicien informatique', 'closed', -20, null, 'Exemple d’une candidature clôturée.'],
    ];
    return examples.map((item, i) => normalize({id: `demo-${i}`, company: item[0], role: item[1], status: item[2], appliedDate: date(item[3]), followUp: item[4] === null ? '' : date(item[4]), notes: item[5], url: '', deletedAt: null}));
  }
  const api = {STATUSES, isoDate, validDate, normalize, due, visible, metrics, toCSV, demoRecords, isTerminal};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CapPro = api;
})(typeof globalThis !== 'undefined' ? globalThis : window);
