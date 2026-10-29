/* Выбираем язык до отрисовки страницы. Сам текст уже находится в HTML. */
(() => {
  "use strict";
  const current = document.documentElement.lang;
  const url = new URL(window.location.href);
  const explicit = url.searchParams.get("lang");
  const valid = (value) => value === "ru" || value === "en";
  let saved = null;

  // Приватный режим и запрет хранилища не должны мешать навигации.
  try {
    saved = window.localStorage.getItem("koto.language");
    if (valid(explicit)) {
      window.localStorage.setItem("koto.language", explicit);
    }
  } catch {
    // При недоступном хранилище выбор передаётся параметром URL.
  }

  const preferred = navigator.language || navigator.languages?.[0] || "en";
  const detected = /^ru(?:-|$)/i.test(preferred) ? "ru" : "en";
  const language = valid(explicit) ? explicit : valid(saved) ? saved : detected;
  if (language === current) return;

  const target = new URL(language === "en" ? "en/" : "../", url);
  target.search = url.search;
  target.searchParams.set("lang", language);
  target.hash = url.hash;
  window.location.replace(target.href);
})();
