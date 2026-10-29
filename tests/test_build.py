"""Регрессии локализации, HTML и прямых ссылок без записи на диск."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch
from html.parser import HTMLParser

from scripts import build as builder


class MemoryPath:
    """Минимальная файловая система для проверки реальной функции сборки."""

    def __init__(self, files: dict[str, str], name: str = "") -> None:
        self.files = files
        self.name = name

    def __truediv__(self, name: str) -> "MemoryPath":
        return MemoryPath(self.files, f"{self.name}/{name}".lstrip("/"))

    @property
    def parent(self) -> "MemoryPath":
        return MemoryPath(self.files, self.name.rpartition("/")[0])

    def mkdir(self, **kwargs: bool) -> None:
        pass

    def read_text(self, encoding: str) -> str:
        return self.files[self.name]

    def write_text(self, value: str, encoding: str) -> None:
        self.files[self.name] = value


class Elements(HTMLParser):
    """Собрать элементы для проверки семантики, а не форматирования HTML."""

    def __init__(self, page: str) -> None:
        super().__init__()
        self.items: list[tuple[str, dict[str, str]]] = []
        self.feed(page)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        self.items.append((tag, dict(attrs)))


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = (
            "product.json", "src/index.template.html",
            "src/locales/ru.json", "src/locales/en.json",
        )
        self.files = {p: (root / p).read_text(encoding="utf-8") for p in paths}

    def build(self) -> None:
        with patch.object(builder, "ROOT", MemoryPath(self.files)):
            builder.build()

    def test_pages_links_icons_and_metadata(self) -> None:
        self.build()
        config = json.loads(self.files["product.json"])
        for lang, path, prefix in (
            ("ru", "index.html", ""), ("en", "en/index.html", "../")
        ):
            with self.subTest(lang=lang):
                page = self.files[path]
                elements = Elements(page).items
                self.assertNotIn("{{", page)
                self.assertIn(("html", {"lang": lang}), elements)
                anchors = [a for tag, a in elements if tag == "a"]
                hrefs = [a["href"] for a in anchors]
                self.assertEqual(hrefs.count(config["links"]["download"]), 1)
                self.assertEqual(hrefs.count(config["links"]["extension_download"]), 1)
                self.assertEqual(hrefs.count(config["links"]["releases"]), 1)
                switches = [a for a in anchors if a.get("class") == "language-switch"]
                self.assertEqual(len(switches), 1)
                self.assertIn("?lang=", switches[0]["href"])
                self.assertNotIn('class="btn small"', page)
                self.assertEqual(sum(tag == "svg" for tag, _ in elements), 5)
                self.assertIn(prefix + "assets/language.js", page)
                self.assertIn(prefix + "assets/styles.css", page)
                self.assertIn('hreflang="ru"', page)
                self.assertIn('hreflang="en"', page)
        self.assertIn("INSTALLATION.en.md", self.files["en/index.html"])
        self.assertIn("en/</loc>", self.files["sitemap.xml"])

    def test_translation_key_mismatch_rejected_before_output(self) -> None:
        locale = json.loads(self.files["src/locales/en.json"])
        del locale["title"]
        self.files["src/locales/en.json"] = json.dumps(locale)
        with self.assertRaises(ValueError):
            self.build()
        self.assertNotIn("index.html", self.files)

    def test_download_page_is_not_an_installer(self) -> None:
        config = json.loads(self.files["product.json"])
        config["links"]["download"] = config["links"]["releases"]
        self.files["product.json"] = json.dumps(config)
        with self.assertRaises(ValueError):
            self.build()

    def test_translations_are_escaped(self) -> None:
        locale = json.loads(self.files["src/locales/en.json"])
        locale["headline"] = '<img src=x onerror="bad()">'
        self.files["src/locales/en.json"] = json.dumps(locale)
        self.build()
        self.assertIn("&lt;img", self.files["en/index.html"])
        self.assertNotIn('<img src=x', self.files["en/index.html"])

    def test_empty_translation_rejected(self) -> None:
        locale = json.loads(self.files["src/locales/en.json"])
        locale["title"] = ""
        self.files["src/locales/en.json"] = json.dumps(locale)
        with self.assertRaises(ValueError):
            self.build()


if __name__ == "__main__":
    unittest.main()
