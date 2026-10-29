[Русский](VERIFICATION.md) | [**English**](VERIFICATION.en.md)

# Website verification

Updated: 30 October 2026.

## Verified sources

The website tree and sources, app release list, README.en.md, INSTALLATION.en.md and PRIVACY.en.md were read through GitHub API. Published alpha.14, its DMG and Chrome 0.1.4 ZIP, and the presence of English installation, models and privacy documentation were confirmed. The original Koto brandmark is preserved. Checksums and app functionality were not tested in this task.

## Checks performed

- The actual build function ran against an in-memory filesystem, without cloning the repository or writing its files to the computer.
- Five Python tests: both pages and metadata/resources/SVG/direct links; rejection of mismatched translation keys; rejection of a release page used as an installer URL; translation escaping; rejection of empty translations.
- JavaScript ran in isolated Node.js contexts: Russian and regional variants, other languages, missing language, saved preference, explicit URL parameter, invalid values, blocked localStorage, redirects in both directions, and preserved query parameters and fragments.
- Russian and English HTML, robots.txt and sitemap.xml were generated. GitHub Releases metadata confirmed the installer and ZIP assets.
- The main download button remains; the header contains the language switch and GitHub link. Feature and privacy placeholders were replaced with inline SVGs.

Tests are in `tests/test_build.py` and `tests/language.test.cjs`; commands are in README. Local execution used sources supplied in memory; normal checkout execution and browser acceptance are separate checks.

## Verification limits

The new version has not undergone visual acceptance in a real browser, click-to-download testing or app launch testing. No claim is made about overflow at all viewport sizes, browser console output or actual OS language settings. JavaScript tests use a simulated browser environment in Node.js.

For visual acceptance, check ru/en at 360, 390, 768, 1024 and 1440 px; switching with Russian and non-Russian primary browser languages, disabled JavaScript, blocked storage, keyboard focus, images and real downloads.

## Historical material

PNGs in `screenshots/` show the previous Russian site from 28 October 2026. They do not show the current language switch or SVGs and are not evidence of acceptance for the new interface. See `screenshots/README.md`.
