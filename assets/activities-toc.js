(() => {
  const SECTION_ATTR = "data-activities-toc";
  const SECTION_ID = "activities-toc";
  const ACTIVITY_TITLE_RE = /^activity\s+\d+/i;
  let scheduled = false;
  let lastKey = null;
  let lastLocation = null;

  const normalizeText = (text) => text.replace(/\s+/g, " ").trim();

  const slugify = (text) => {
    const base = text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
    if (!base) return "activity";
    return base.startsWith("activity") ? base : `activity-${base}`;
  };

  const ensureUniqueId = (base) => {
    let candidate = base;
    let i = 2;
    while (document.getElementById(candidate)) {
      candidate = `${base}-${i}`;
      i += 1;
    }
    return candidate;
  };

  const findTocContainer = () => document.querySelector(".bd-toc");

  const findContentsSection = (tocContainer) => {
    const details = Array.from(tocContainer.querySelectorAll("details"));
    return (
      details.find((item) => {
        const summary = item.querySelector("summary");
        if (!summary) return false;
        const label = normalizeText(summary.textContent || "");
        return /contents/i.test(label);
      }) || null
    );
  };

  const getContentRoot = () =>
    document.querySelector("main") ||
    document.querySelector(".bd-content") ||
    document.body;

  const isTopLevelActivity = (block) =>
    !block.parentElement?.closest(".admonition");

  const sortByDocumentOrder = (items) =>
    items.sort((a, b) => {
      if (a.block === b.block) return 0;
      const position = a.block.compareDocumentPosition(b.block);
      if (position & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
      if (position & Node.DOCUMENT_POSITION_PRECEDING) return 1;
      return 0;
    });

  const findActivityBlocks = () => {
    const root = getContentRoot();
    const candidates = Array.from(
      root.querySelectorAll(
        ".admonition.tip, .admonition[data-admonition='tip'], .admonition-tip"
      )
    );

    return sortByDocumentOrder(
      candidates
        .map((block) => {
          const titleEl = block.querySelector(".admonition-title");
          if (!titleEl) return null;
          const titleText = normalizeText(titleEl.textContent || "");
          if (!ACTIVITY_TITLE_RE.test(titleText)) return null;
          if (!isTopLevelActivity(block)) return null;
          return { block, titleEl, titleText };
        })
        .filter(Boolean),
    );
  };

  const buildActivitiesSection = (tocContainer, contentsSection, activities) => {
    const existing = tocContainer.querySelector(`[${SECTION_ATTR}]`);
    if (existing) existing.remove();
    if (activities.length === 0) return;

    const details = document.createElement("details");
    details.setAttribute(SECTION_ATTR, "true");
    details.id = SECTION_ID;

    if (contentsSection) {
      details.className = contentsSection.className;
      if (contentsSection.hasAttribute("open")) {
        details.setAttribute("open", "open");
      }
    } else {
      const sampleDetails = tocContainer.querySelector("details");
      if (sampleDetails) details.className = sampleDetails.className;
    }

    const summary = document.createElement("summary");
    if (contentsSection) {
      const contentsSummary = contentsSection.querySelector("summary");
      if (contentsSummary) summary.className = contentsSummary.className;
    }
    summary.textContent = "Activities";
    details.appendChild(summary);

    const contentsList = contentsSection
      ? contentsSection.querySelector("ul, ol")
      : null;
    const list = document.createElement(contentsList?.tagName || "ul");
    if (contentsList?.className) list.className = contentsList.className;

    const sampleItem = contentsSection
      ? contentsSection.querySelector("li")
      : null;
    const sampleLink = contentsSection
      ? contentsSection.querySelector("a")
      : null;

    activities.forEach(({ block, titleEl, titleText }) => {
      let targetId = block.id || titleEl.id;
      if (!targetId) {
        targetId = ensureUniqueId(slugify(titleText));
        block.id = targetId;
      }

      const li = document.createElement("li");
      if (sampleItem?.className) li.className = sampleItem.className;

      const link = document.createElement("a");
      if (sampleLink?.className) link.className = sampleLink.className;
      link.href = `#${targetId}`;
      link.textContent = titleText;

      li.appendChild(link);
      list.appendChild(li);
    });

    details.appendChild(list);

    const insertParent = contentsSection?.parentNode || tocContainer;
    if (contentsSection?.nextSibling) {
      insertParent.insertBefore(details, contentsSection.nextSibling);
    } else {
      insertParent.appendChild(details);
    }
  };

  const render = () => {
    const tocContainer = findTocContainer();
    if (!tocContainer) return;

    const contentsSection = findContentsSection(tocContainer);
    const activities = findActivityBlocks();
    const key = activities.map((item) => item.titleText).join("|");
    const locationKey = `${window.location.pathname}${window.location.hash}`;
    const existing = tocContainer.querySelector(`[${SECTION_ATTR}]`);

    if (
      key === lastKey &&
      locationKey === lastLocation &&
      ((key && existing) || (!key && !existing))
    ) {
      return;
    }

    lastKey = key;
    lastLocation = locationKey;
    buildActivitiesSection(tocContainer, contentsSection, activities);
  };

  const scheduleRender = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      render();
    });
  };

  document.addEventListener("DOMContentLoaded", scheduleRender);
  window.addEventListener("hashchange", scheduleRender);
  window.addEventListener("popstate", scheduleRender);

  const observer = new MutationObserver(scheduleRender);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
