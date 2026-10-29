[Русский](README.md) | [**English**](README.en.md)

# Koto — app website

A responsive Russian and English website for the native Koto translator by **Slipcast-Dev**.

- [Website](https://slipcast-dev.github.io/koto-website/) · [English](https://slipcast-dev.github.io/koto-website/en/?lang=en)
- [Website repository](https://github.com/Slipcast-dev/koto-website)
- [App and source code](https://github.com/Slipcast-dev/translator-Koto)
- [Verification and limitations](VERIFICATION.en.md)

## Languages

Russian is served from `index.html`; English from `en/index.html`. A globe language switch replaces the extra download button on the right of the header. The main download button remains in the hero.

Selection priority:
1. An explicit `?lang=ru` or `?lang=en` URL parameter.
2. A manual choice saved in `localStorage` as `koto.language`.
3. The primary browser language (`navigator.language`): `ru` and `ru-*` select Russian; all others select English. Unknown languages fall back to English.

Browsers usually inherit the system language, but a website cannot read OS language settings directly. New visitors use the browser's preferred language. A manual choice takes priority on later visits. If storage is blocked, switching still works through the URL parameter, but the choice cannot persist between independent visits.

A small local script runs in `head` before page content. Redirects preserve query parameters and fragments. With JavaScript disabled, automatic selection is unavailable; both pages and their language links still work. English pages link to English app documentation. The translation preview intentionally retains its English → Russian example with explicit `lang` attributes.

## Architecture

Static HTML/CSS with JavaScript only for language selection; no backend, npm, external fonts, CDN or analytics. The website does not collect text. Only the language choice is stored in the browser. No cookies, API keys or environment variables are required.

The translator interface is a fixed preview. Apple Translation, Qwen, OCR and shortcuts belong to the installed app. Inline SVGs represent text recognition, a local-engine chip, Chrome and a privacy shield with a lock. The original Koto brandmark is preserved.

## Structure

| File | Purpose |
| --- | --- |
| `index.html`, `en/index.html` | Generated pages for GitHub Pages |
| `src/index.template.html` | Shared HTML template |
| `src/locales/ru.json`, `src/locales/en.json` | Text, metadata and accessible labels |
| `product.json` | Version, requirements, shared and English links |
| `assets/styles.css` | Styling and responsive layout |
| `assets/language.js` | Language detection and persistence |
| `assets/koto-brandmark.png` | Brandmark and favicon |
| `scripts/build.py` | Standard-library Python build |
| `tests/` | Build and language-selection regressions |
| `robots.txt`, `sitemap.xml` | Indexing for both pages |
| `screenshots/` | Historical screenshots of the previous Russian site; see its README |
| `VERIFICATION.md`, `VERIFICATION.en.md` | Current verification reports |
| `LICENSE` | MIT, © 2026 Slipcast-Dev |

## Build and checks

Python 3.10+; Node.js 18+ is only needed for JavaScript checks. No third-party dependencies.

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/language.test.cjs
```

The build validates HTTPS links, direct DMG/ZIP URLs, matching translation keys and non-empty strings, and escapes all substitutions. Both localizations are validated before pages are written. Commit sources and generated output together.

For local preview:
```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open the [local site](http://localhost:8765/), [Russian](http://localhost:8765/?lang=ru) or [English](http://localhost:8765/en/?lang=en) page. Stop the server with `Ctrl+C`.

## Product updates and publishing

Verified on 30 October 2026: published prerelease **0.1.0-alpha.14**, extension **Chrome 0.1.4**. Download buttons use the existing DMG and ZIP assets' direct `browser_download_url` values. The Releases link opens the release list. The site does not use `/releases/latest` for alpha builds.

For a new release:
1. Check GitHub Releases assets and the app documentation's requirements.
2. Update `version`, `verified_on`, `links.download`, `links.extension_download` and, if needed, `platform` in `product.json`. `english_links` overrides documentation links for English.
3. Update both locale files when text changes.
4. Run the build and checks; update both documentation languages.
5. Push changes to `main`. GitHub Pages publishes the root of this branch; inspect the result in Actions.

Download URLs are pinned to a release and do not update automatically. For a new domain, change `site_url`, retain its trailing `/`, and rebuild. Pages include canonical and hreflang links; the sitemap includes both pages.

## Product limitations

Apple Silicon, macOS 26+. The alpha is signed ad hoc without Apple Developer ID/notarization: macOS may block launch. App documentation records release checks on macOS 27.2; macOS 26, extended Live use and some external integrations still need acceptance testing. This repository does not establish app functionality.

Before publishing visual changes, check both languages at 360, 390, 768, 1024 and 1440 px, keyboard focus and links. See the [report](VERIFICATION.en.md) for checks actually performed. Preserve the copyright and MIT notice when redistributing.
