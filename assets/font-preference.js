let initialized = false;
function render({ el }) {
  if (initialized) return;
  initialized = true;
  // MyST gives widget CSS a content-hashed URL. Apply it to the page as well
  // as the widget so returning visitors do not reuse an old myst-theme.css.
  const stylesheet = el.querySelector('link[rel="stylesheet"]');
  if (stylesheet) document.head.append(stylesheet.cloneNode(true));
  const key = 'math124-font';
  let preference = 'default';
  const appearanceKey = 'math124-appearance';
  const appearances = ['light', 'paper', 'dark'];
  let appearance = null;
  try { appearance = localStorage.getItem(appearanceKey); } catch { /* Use the current theme. */ }
  const apply = (value) => {
    const palatino = value === 'palatino';
    preference = palatino ? 'palatino' : 'default';
    document.documentElement.classList.toggle('font-palatino', palatino);
    document.querySelectorAll('.font-preference-input').forEach((input) => {
      input.checked = palatino;
    });
  };
  try { preference = localStorage.getItem(key) || 'default'; } catch { /* Use the default. */ }

  const syncAppearance = () => {
    const root = document.documentElement;
    root.dataset.notesAppearance = appearance;
    root.classList.toggle('dark', appearance === 'dark');
    root.classList.toggle('light', appearance !== 'dark');
    document.querySelectorAll('.appearance-preference-input').forEach((input) => {
      input.checked = input.value === appearance;
    });
  };
  const applyAppearance = (value) => {
    appearance = appearances.includes(value) ? value : 'light';
    // Keep MyST's React theme state in sync, including dialogs and navigation.
    if (document.documentElement.classList.contains('dark') !== (appearance === 'dark')) {
      document.querySelector('.myst-theme-button')?.click();
    }
    syncAppearance();
  };

  const mount = () => {
    document.querySelectorAll('.article.footer.myst-primary-sidebar-footer').forEach((footer) => {
      if (footer.querySelector('.font-preference')) return;
      footer.insertAdjacentHTML('beforeend', "<div class=\"font-preference\">\n  <span class=\"font-preference-title\">Font</span>\n  <label class=\"font-preference-control\">\n    <span>Default</span>\n    <input type=\"checkbox\" role=\"switch\" aria-label=\"Use Palatino font\" class=\"font-preference-input\">\n    <span class=\"font-preference-track\" aria-hidden=\"true\"></span>\n    <span class=\"font-preference-palatino\">Palatino</span>\n  </label>\n</div>\n");
      const fieldset = document.createElement('fieldset');
      fieldset.className = 'appearance-preference';
      fieldset.innerHTML = `<legend>Appearance</legend><div class="appearance-options">${appearances.map((value) => `
        <label class="appearance-option">
          <input class="appearance-preference-input" type="radio" name="notes-appearance" value="${value}">
          <span>${value[0].toUpperCase() + value.slice(1)}</span>
        </label>`).join('')}</div>`;
      footer.querySelector('.font-preference').append(fieldset);
      apply(preference);
      syncAppearance();
    });
  };
  const init = () => {
    if (!appearances.includes(appearance)) {
      appearance = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }
    applyAppearance(appearance);
    apply(preference);
    mount();
    // Theme changes rewrite the root class list; preserve the reading preference.
    new MutationObserver(() => {
      if (document.documentElement.classList.contains('font-palatino') !== (preference === 'palatino')) {
        apply(preference);
      }
      if (document.documentElement.classList.contains('dark') !== (appearance === 'dark')) {
        syncAppearance();
      }
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    // MyST replaces sidebar contents during client-side navigation.
    new MutationObserver(mount).observe(document.documentElement, { childList: true, subtree: true });
    document.addEventListener('change', (event) => {
      if (event.target.matches('.appearance-preference-input')) {
        applyAppearance(event.target.value);
        try { localStorage.setItem(appearanceKey, appearance); } catch { /* Keep the current-page choice. */ }
        return;
      }
      if (!event.target.matches('.font-preference-input')) return;
      const value = event.target.checked ? 'palatino' : 'default';
      apply(value);
      try { localStorage.setItem(key, value); } catch { /* Keep the current-page choice. */ }
    });
  };
  init();
  window.addEventListener('storage', (event) => {
    if (event.key === key || event.key === null) apply(event.newValue);
    if (event.key === appearanceKey || event.key === null) applyAppearance(event.newValue);
  });
}
export default { render };
