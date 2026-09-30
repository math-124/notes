function render({ el } = {}) {
  // Keep one controller across client-side navigation and content-hashed copies
  // of the MyST widget. Its render hook runs after the page has hydrated.
  if (window.__math124ReadingSettings) return;
  window.__math124ReadingSettings = true;
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
  const stylesheet = el?.querySelector('link[rel="stylesheet"]');
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
      input.checked = input.value === preference;
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

  const settings = document.createElement('dialog');
  settings.id = 'notes-reading-settings';
  settings.className = 'notes-reading-settings';
  settings.setAttribute('aria-labelledby', 'notes-reading-settings-title');
  settings.innerHTML = `
    <div class="notes-settings-heading">
      <h2 id="notes-reading-settings-title">Reading settings</h2>
      <button type="button" class="notes-settings-close" aria-label="Close reading settings">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg>
      </button>
    </div>
    <fieldset><legend>Font</legend><div class="notes-font-options">
      ${['default', 'palatino'].map((value) => `<label class="notes-settings-choice notes-font-choice">
        <input type="radio" name="notes-font" value="${value}" class="font-preference-input">
        <span class="notes-choice-content"><span class="notes-font-sample notes-font-${value}" aria-hidden="true">Aa</span>
          <span>${value === 'default' ? 'Default' : 'Palatino'}</span><span class="notes-choice-check" aria-hidden="true">✓</span>
        </span>
      </label>`).join('')}
    </div></fieldset>
    <fieldset><legend>Color</legend><div class="notes-color-options">
      ${appearances.map((value) => `<label class="notes-settings-choice notes-color-choice">
        <input type="radio" name="notes-appearance" value="${value}" class="appearance-preference-input">
        <span class="notes-choice-content"><span class="notes-color-sample notes-sample-${value}" aria-hidden="true">Aa</span>
          <span>${value[0].toUpperCase() + value.slice(1)}</span><span class="notes-choice-check" aria-hidden="true">✓</span>
        </span>
      </label>`).join('')}
    </div></fieldset>
    <button type="button" class="notes-settings-done">Done</button>`;
  document.body.append(settings);

  const mobile = window.matchMedia('(max-width: 639px)');
  let settingsButton;
  let modal = false;
  let previousOverflow = '';
  let openPath = location.pathname;
  const positionSettings = () => {
    if (!settings.open || !settingsButton) return;
    if (modal) {
      // A wide equation can enlarge the layout viewport on phones. Anchor the
      // sheet to the visible viewport so its Done button cannot fall offscreen.
      const viewport = window.visualViewport;
      const height = viewport?.height || document.documentElement.clientHeight;
      settings.style.width = `${Math.min(document.documentElement.clientWidth, viewport?.width || window.innerWidth)}px`;
      settings.style.maxHeight = `${height - 16}px`;
      settings.style.bottom = 'auto';
      settings.style.right = 'auto';
      settings.style.left = `${viewport?.offsetLeft || 0}px`;
      settings.style.top = `${(viewport?.offsetTop || 0) + height - settings.offsetHeight}px`;
      return;
    }
    const rect = settingsButton.getBoundingClientRect();
    const viewportWidth = document.documentElement.clientWidth;
    const width = Math.min(320, viewportWidth - 24);
    settings.style.top = `${rect.bottom + 8}px`;
    settings.style.left = `${Math.max(12, Math.min(rect.right - width, viewportWidth - width - 12))}px`;
    settings.style.maxHeight = `${Math.max(120, window.innerHeight - rect.bottom - 20)}px`;
  };
  const closeSettings = () => {
    if (!settings.open) return;
    settings.close();
    document.body.style.overflow = previousOverflow;
    settingsButton?.setAttribute('aria-expanded', 'false');
    settingsButton?.focus({ preventScroll: true });
  };
  const openSettings = () => {
    if (settings.open) return;
    previousOverflow = document.body.style.overflow;
    modal = mobile.matches;
    openPath = location.pathname;
    ['top', 'left', 'right', 'bottom', 'width', 'max-height'].forEach((property) => settings.style.removeProperty(property));
    if (modal) {
      settings.showModal();
      document.body.style.overflow = 'hidden';
    } else {
      settings.show();
    }
    settingsButton?.setAttribute('aria-expanded', 'true');
    positionSettings();
    settings.querySelector('.notes-settings-close').focus({ preventScroll: true });
  };
  settings.querySelectorAll('.notes-settings-close, .notes-settings-done').forEach((button) => {
    button.addEventListener('click', closeSettings);
  });
  settings.addEventListener('cancel', (event) => {
    event.preventDefault();
    closeSettings();
  });
  settings.addEventListener('click', (event) => {
    const rect = settings.getBoundingClientRect();
    if (event.target === settings && (event.clientX < rect.left || event.clientX > rect.right ||
        event.clientY < rect.top || event.clientY > rect.bottom)) closeSettings();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && settings.open) {
      event.preventDefault();
      closeSettings();
    }
  });
  document.addEventListener('pointerdown', (event) => {
    if (settings.open && !modal && !settings.contains(event.target) &&
        !settingsButton?.contains(event.target)) closeSettings();
  });
  window.addEventListener('resize', () => {
    if (settings.open && modal !== mobile.matches) {
      closeSettings();
      openSettings();
    }
    positionSettings();
  });
  window.visualViewport?.addEventListener('resize', positionSettings);
  window.visualViewport?.addEventListener('scroll', positionSettings);

  const mount = () => {
    if (settings.open && location.pathname !== openPath) closeSettings();
    const toolbar = document.querySelector('.myst-top-nav-bar');
    const search = toolbar?.querySelector('.myst-search-bar');
    if (!toolbar || !search) return;
    search.parentElement.classList.add('notes-toolbar-tools');
    if (!toolbar.querySelector('.notes-settings-button')) {
      settingsButton = document.createElement('button');
      settingsButton.type = 'button';
      settingsButton.className = 'notes-settings-button';
      settingsButton.title = 'Reading settings';
      settingsButton.setAttribute('aria-label', 'Reading settings');
      settingsButton.setAttribute('aria-haspopup', 'dialog');
      settingsButton.setAttribute('aria-controls', settings.id);
      settingsButton.setAttribute('aria-expanded', String(settings.open));
      settingsButton.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M4 7h3m4 0h9M4 17h9m4 0h3"/><circle cx="9" cy="7" r="2"/><circle cx="15" cy="17" r="2"/></svg>`;
      settingsButton.addEventListener('click', () => settings.open ? closeSettings() : openSettings());
      search.insertAdjacentElement('afterend', settingsButton);
      document.documentElement.dataset.notesSettings = 'ready';
    }
    const title = toolbar.querySelector('.myst-home-link');
    if (title && !title.querySelector('.notes-course-title-short')) {
      title.firstElementChild?.classList.add('notes-course-title-full');
      const shortTitle = document.createElement('span');
      shortTitle.className = 'notes-course-title-short';
      shortTitle.textContent = 'Math 124';
      title.append(shortTitle);
    }
    // Match the desktop link row itself, not links inside an open overflow menu.
    const links = Array.from(search.parentElement.children).find((child) => child.querySelector(':scope > a'));
    links?.classList.add('notes-toolbar-links');
    const more = toolbar.querySelector('.myst-action-menu');
    if (more) {
      more.parentElement.classList.add('notes-toolbar-more');
      more.querySelector('button')?.setAttribute('aria-label', 'Course resources');
    }

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
    // MyST replaces navigation during client-side routing; coalesce math/widget mutations.
    let mountPending = false;
    new MutationObserver(() => {
      if (mountPending) return;
      mountPending = true;
      requestAnimationFrame(() => { mountPending = false; mount(); });
    }).observe(document.body, { childList: true, subtree: true });
    document.addEventListener('change', (event) => {
      if (event.target.matches('.appearance-preference-input')) {
        applyAppearance(event.target.value);
        try { localStorage.setItem(appearanceKey, appearance); } catch { /* Keep the current-page choice. */ }
        return;
      }
      if (!event.target.matches('.font-preference-input')) return;
      const value = event.target.value;
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
