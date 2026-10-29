"""Сборка русской и английской страниц из общего шаблона."""

from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("ru", "en")


def require_https(value: str, key: str) -> None:
    """Отклонить некорректные публичные ссылки до записи файлов."""
    if not isinstance(value, str):
        raise ValueError(f"Ожидается строка: {key}")
    url = urlparse(value)
    if url.scheme != "https" or not url.netloc:
        raise ValueError(f"Некорректный HTTPS-адрес: {key}")


def build() -> None:
    """Проверить обе локализации и затем записать готовые файлы.

    Переводы содержат только текст: разметка принадлежит общему шаблону.
    Все подстановки экранируются. Обе страницы проверяются до первой записи,
    чтобы ошибка английского перевода не оставила частично обновлённый сайт.
    """
    config = json.loads((ROOT / "product.json").read_text(encoding="utf-8"))
    origin = config["site_url"]
    require_https(origin, "site_url")
    if not origin.endswith("/"):
        raise ValueError("site_url должен заканчиваться на /")
    for group in ("links", "english_links"):
        for key, value in config[group].items():
            require_https(value, f"{group}.{key}")
    for key, suffix in (("download", ".dmg"), ("extension_download", ".zip")):
        url = urlparse(config["links"][key])
        if "/releases/download/" not in url.path or not url.path.endswith(suffix):
            raise ValueError(f"Нужна прямая ссылка на файл: links.{key}")

    template = (ROOT / "src/index.template.html").read_text(encoding="utf-8")
    locales = {
        lang: json.loads(
            (ROOT / f"src/locales/{lang}.json").read_text(encoding="utf-8")
        )
        for lang in LANGUAGES
    }
    if locales["ru"].keys() != locales["en"].keys():
        raise ValueError("Наборы ключей ru и en должны совпадать")
    pages = {}
    for lang in LANGUAGES:
        translations = locales[lang]
        if any(not isinstance(v, str) or not v.strip() for v in translations.values()):
            raise ValueError(f"Пустой или некорректный перевод: {lang}")
        links = dict(config["links"])
        if lang == "en":
            links.update(config["english_links"])
        values = {
            key: str(config[key])
            for key in ("version", "platform", "copyright_year", "site_url")
        }
        values.update({f"links.{key}": value for key, value in links.items()})
        values.update({f"t.{key}": value for key, value in translations.items()})
        values.update({
            "language": lang,
            "other_language": "en" if lang == "ru" else "ru",
            "asset_prefix": "" if lang == "ru" else "../",
            "page_url": origin if lang == "ru" else origin + "en/",
            "switch_url": "en/?lang=en" if lang == "ru" else "../?lang=ru",
        })

        def substitute(match: re.Match[str]) -> str:
            """Не допускать HTML из конфигурации и файлов перевода."""
            return escape(values[match.group(1)], quote=True)

        page = re.sub(r"\{\{([a-z_.]+)\}\}", substitute, template)
        if "{{" in page:
            raise ValueError(f"Неподставленные значения: {lang}")
        pages["index.html" if lang == "ru" else "en/index.html"] = page

    for path, page in pages.items():
        output = ROOT / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(page, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {origin}sitemap.xml\n",
        encoding="utf-8",
    )
    entries = "".join(
        f"  <url><loc>{escape(origin + suffix)}</loc></url>\n"
        for suffix in ("", "en/")
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries + "</urlset>\n",
        encoding="utf-8",
    )
    print("Готово: index.html, en/index.html, robots.txt, sitemap.xml")


if __name__ == "__main__":
    try:
        build()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Ошибка сборки: {error}") from error
