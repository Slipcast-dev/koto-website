"""Сборка статической страницы из шаблона и единой конфигурации продукта."""

import json
from pathlib import Path
import re
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    """Проверить конфигурацию и записать готовые файлы для GitHub Pages.

    Значения экранируются для HTML. Неизвестные маркеры и некорректные
    ссылки прерывают сборку, чтобы не публиковать повреждённую страницу.
    JavaScript и сетевые запросы посетителю для просмотра не нужны.
    """
    from html import escape

    config = json.loads((ROOT / "product.json").read_text(encoding="utf-8"))
    values = {key: str(value) for key, value in config.items() if key != "links"}
    values.update({f"links.{key}": value for key, value in config["links"].items()})
    for key, value in values.items():
        if key.startswith("links.") or key == "site_url":
            url = urlparse(value)
            if url.scheme != "https" or not url.netloc:
                raise ValueError(f"Некорректный HTTPS-адрес: {key}")

    def substitute(match: re.Match[str]) -> str:
        """Подставить только известное значение с безопасным экранированием."""
        return escape(values[match.group(1)], quote=True)

    template = (ROOT / "src/index.template.html").read_text(encoding="utf-8")
    page = re.sub(r"\{\{([a-z_.]+)\}\}", substitute, template)
    if "{{" in page:
        raise ValueError("В шаблоне остались неподставленные значения")
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    origin = config["site_url"]
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {origin}sitemap.xml\n", encoding="utf-8"
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{escape(origin)}</loc></url>\n</urlset>\n",
        encoding="utf-8",
    )
    print("Готово: index.html, robots.txt, sitemap.xml")


if __name__ == "__main__":
    try:
        build()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Ошибка сборки: {error}") from error
