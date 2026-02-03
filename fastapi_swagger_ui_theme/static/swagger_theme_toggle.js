(function () {
  const storageKey = "swagger-docs-theme"; // "dark" | "light"

  function prefersDarkNow() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  // Create exactly ONE button instance per page load.
  function createButton() {
    const btn = document.createElement("button");
    btn.id = "swagger-theme-toggle";
    btn.type = "button";
    btn.title = "Toggle theme";
    btn.setAttribute("aria-label", "Toggle theme");
    btn.style.lineHeight = "0";

    btn.innerHTML = `
      <span class="icon-sun" aria-hidden="true" style="display:none">
        <svg class="swagger-theme-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm0-16a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0V3a1 1 0 0 1 1-1Zm0 18a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1Zm10-8a1 1 0 0 1-1 1h-1a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1ZM4 12a1 1 0 0 1-1 1H2a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1Zm15.07-7.07a1 1 0 0 1 0 1.41l-.71.71a1 1 0 0 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0ZM7.05 17.95a1 1 0 0 1 0 1.41l-.71.71a1 1 0 0 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0Zm12.02 1.41a1 1 0 0 1-1.41 0l-.71-.71a1 1 0 1 1 1.41-1.41l.71.71a1 1 0 0 1 0 1.41ZM7.76 6.34A1 1 0 0 1 6.34 7.76l-.71-.71A1 1 0 1 1 7.05 5.64l.71.71Z"/>
        </svg>
      </span>
      <span class="icon-moon" aria-hidden="true" style="display:none">
        <svg class="swagger-theme-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M21 14.5A8.5 8.5 0 0 1 9.5 3a7 7 0 1 0 11.5 11.5Z"/>
        </svg>
      </span>
    `;

    return btn;
  }

function moveOpenApiLinkAboveDescription() {
  const info = document.querySelector(".swagger-ui .information-container .info");
  if (!info) return false;

  const link = info.querySelector("a.link");
  const description = info.querySelector(".info__description");

  if (!link || !description) return false;

  // Zaten doğru yerdeyse dokunma
  if (link.nextElementSibling === description) return true;

  info.insertBefore(link, description);
  return true;
}

  function setIcon(btn, isDark) {
    const sun = btn.querySelector(".icon-sun");
    const moon = btn.querySelector(".icon-moon");
    if (!sun || !moon) return;

    // When currently dark, show sun (action: go light). When light, show moon (action: go dark).
    sun.style.display = isDark ? "inline-flex" : "none";
    moon.style.display = isDark ? "none" : "inline-flex";

    btn.title = isDark ? "Switch to light mode" : "Switch to dark mode";
    btn.setAttribute("aria-label", btn.title);
  }

  function apply(theme, btn) {
    const darkCss = document.getElementById("swagger-dark-css");
    const isDark = theme === "dark";

    document.documentElement.classList.toggle("docs-dark", isDark);
    document.body.classList.toggle("docs-dark", isDark);

    if (darkCss) darkCss.disabled = !isDark;

    // Let CSS control colors/borders/backgrounds (avoid inline overrides)
    btn.style.color = "";
    btn.style.background = "";
    btn.style.borderColor = "";

    // Always update the icon for the SAME button instance.
    setIcon(btn, isDark);
  }

  function mountIntoHeader(btn) {
    const header = document.querySelector(".swagger-ui .information-container .info hgroup.main");
    if (!header) return false;

    let slot = header.querySelector(".swagger-ui-toggle-slot");
    if (!slot) {
      slot = document.createElement("div");
      slot.className = "swagger-ui-toggle-slot";
      header.appendChild(slot);
    }

    // If it was mounted elsewhere, move it here.
    if (btn.parentElement !== slot) {
      slot.appendChild(btn);
    }

    return true;
  }

  function init() {
    // Create the single button instance.
    const btn = createButton();

    // Put it in the DOM immediately so SVG/icon rendering is reliable on first load.
    // We'll move it into the Swagger header once Swagger renders.
    btn.style.visibility = "hidden";
    btn.style.pointerEvents = "none";
    document.body.appendChild(btn);

    const saved = localStorage.getItem(storageKey);
    const initial = saved ? saved : (prefersDarkNow() ? "dark" : "light");

    // Apply theme + set icon immediately.
    apply(initial, btn);

    // Mount once Swagger renders.
    let tries = 0;
const iv = setInterval(function () {
  tries += 1;

  const mounted = mountIntoHeader(btn);
  const moved = moveOpenApiLinkAboveDescription();

  if ((mounted && moved) || tries > 60) {
    clearInterval(iv);

    btn.style.visibility = "visible";
    btn.style.pointerEvents = "auto";

    const current = document.documentElement.classList.contains("docs-dark")
      ? "dark"
      : "light";
    apply(current, btn);
  }
}, 100);

    // Follow OS changes only if user never chose explicitly.
    if (!saved && window.matchMedia) {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      const onChange = (e) => apply(e.matches ? "dark" : "light", btn);
      if (mq.addEventListener) mq.addEventListener("change", onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }

    btn.addEventListener("click", function () {
      const current = document.documentElement.classList.contains("docs-dark") ? "dark" : "light";
      const next = current === "dark" ? "light" : "dark";
      localStorage.setItem(storageKey, next);
      apply(next, btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();