/* Проверка выбора языка в изолированном браузерном контексте Node.js. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../assets/language.js"), "utf8");

function run({ current = "ru", preferred = "en-US", languages = [], saved = null,
  query = "", blocked = false, hash = "" } = {}) {
  let redirect = null;
  let stored = saved;
  const window = {
    location: {
      href: "https://example.com/koto/" + (current === "en" ? "en/" : "") + query + hash,
      replace(value) { redirect = value; },
    },
    localStorage: {
      getItem() { if (blocked) throw Error("Blocked"); return stored; },
      setItem(key, value) { if (blocked) throw Error("Blocked"); stored = value; },
    },
  };
  vm.runInNewContext(source, {
    URL, window, document: { documentElement: { lang: current } },
    navigator: { language: preferred, languages },
  });
  return { redirect, stored };
}

assert.equal(run({ preferred: "ru-RU" }).redirect, null);
assert.equal(run({ preferred: "RU" }).redirect, null);
for (const preferred of ["en-US", "de-DE", "fr", "ja", "be", "uk", "russian", ""]) {
  assert.equal(run({ preferred }).redirect, "https://example.com/koto/en/?lang=en");
}
assert.equal(run({ current: "en", preferred: "ru" }).redirect, "https://example.com/koto/?lang=ru");
assert.equal(run({ current: "en", preferred: "en-GB" }).redirect, null);
assert.equal(run({ preferred: "ru", saved: "en" }).redirect, "https://example.com/koto/en/?lang=en");
assert.equal(run({ preferred: "de", saved: "ru" }).redirect, null);
assert.equal(run({ preferred: "ru", saved: "invalid" }).redirect, null);
assert.equal(run({ preferred: "ru", query: "?lang=en" }).stored, "en");
assert.equal(run({ preferred: "en", saved: "en", query: "?lang=ru" }).redirect, null);
assert.equal(run({ preferred: "ru", query: "?lang=de" }).redirect, null);
assert.equal(run({ preferred: "de", blocked: true }).redirect, "https://example.com/koto/en/?lang=en");
assert.equal(run({ preferred: "en", query: "?lang=ru", blocked: true }).redirect, null);
assert.equal(run({ preferred: "en", query: "?ref=share", hash: "#privacy" }).redirect,
  "https://example.com/koto/en/?ref=share&lang=en#privacy");
assert.equal(run({ preferred: "", languages: ["ru-RU"] }).redirect, null);
assert.equal(run({ current: "en", preferred: "ru", query: "?lang=en" }).redirect, null);
console.log("PASS: language detection, switching, persistence, blocked storage and redirect paths");
