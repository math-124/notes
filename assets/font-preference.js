let initialized = false;
function render({ el }) {
  if (initialized) return;
  initialized = true;
  // One shared display filter works for SVG, PNG, and interactive WebGL plots.
  document.body.insertAdjacentHTML('beforeend', `<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" style="position:absolute;pointer-events:none">
  <defs><filter id="notes-dark-diagram-colors" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <!-- Detect chromatic pixels. Neutral backgrounds, axes, and labels use
         a separate lightness reversal; vector hues are never inverted. -->
    <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1 -1 0 0 0" result="rg"/>
    <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 1 -1 0 0" result="gb"/>
    <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  -1 0 1 0 0" result="br"/>
    <feMerge result="chroma"><feMergeNode in="rg"/><feMergeNode in="gb"/><feMergeNode in="br"/></feMerge>
    <feComponentTransfer in="chroma" result="base-color-mask"><feFuncA type="table" tableValues="0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"/></feComponentTransfer>
    <!-- Dark green has low chroma; keep it colored without classifying
         blue-gray plot typography as an accent. -->
    <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 20 -20 0 0" result="green-mask"/>
    <feMerge result="color-mask"><feMergeNode in="base-color-mask"/><feMergeNode in="green-mask"/></feMerge>
    <!-- Pale colored surfaces become dark tinted surfaces, so bright vector
         strokes remain visible over translucent planes and shaded regions. -->
    <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  .333333 .333333 .333333 0 0" result="lightness"/>
    <feComponentTransfer in="lightness" result="pale-mask"><feFuncA type="table" tableValues="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1"/></feComponentTransfer>
    <feComposite in="color-mask" in2="pale-mask" operator="out" result="strong-mask"/>
    <feComponentTransfer in="SourceGraphic" result="muted">
      <feFuncR type="linear" slope="0.25"/><feFuncG type="linear" slope="0.25"/><feFuncB type="linear" slope="0.25"/>
    </feComponentTransfer>
    <feComposite in="muted" in2="color-mask" operator="in" result="muted-colored"/>
    <feComposite in="muted-colored" in2="pale-mask" operator="in" result="surfaces"/>
    <feComponentTransfer in="SourceGraphic" result="tinted">
      <feFuncR type="linear" slope="0.5" intercept="0.5"/>
      <feFuncG type="linear" slope="0.5" intercept="0.5"/>
      <feFuncB type="linear" slope="0.5" intercept="0.5"/>
    </feComponentTransfer>
    <!-- Neutral labels (including Plotly's blue-gray ink) use an affine
         grayscale reversal, so antialiased edges cannot develop halos. -->
    <feColorMatrix in="SourceGraphic" type="saturate" values="0" result="grayscale"/>
    <feComponentTransfer in="grayscale" result="neutral">
      <feFuncR type="linear" slope="-0.85" intercept="0.95"/>
      <feFuncG type="linear" slope="-0.85" intercept="0.95"/>
      <feFuncB type="linear" slope="-0.85" intercept="0.95"/>
    </feComponentTransfer>
    <feComposite in="tinted" in2="strong-mask" operator="in" result="colored"/>
    <feComposite in="neutral" in2="color-mask" operator="out" result="uncolored"/>
    <!-- Add complementary masks instead of stacking translucent layers;
         preserve coverage at the antialiased boundaries. -->
    <feComposite in="uncolored" in2="surfaces" operator="arithmetic" k2="1" k3="1" result="base"/>
    <feComposite in="base" in2="colored" operator="arithmetic" k2="1" k3="1"/>
  </filter></defs>
</svg>`);
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
