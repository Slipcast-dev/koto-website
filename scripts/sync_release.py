"""Обновить product.json по последнему выпуску приложения; без токенов, только публичный API GitHub."""

from datetime import date
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RELEASES = "https://api.github.com/repos/Slipcast-dev/translator-Koto/releases?per_page=20"


def latest_release() -> dict:
    """Первый непубликованный-как-черновик выпуск: API отдаёт их от новых к старым."""
    request = urllib.request.Request(RELEASES, headers={"Accept": "application/vnd.github+json", "User-Agent": "koto-website-sync"})
    with urllib.request.urlopen(request, timeout=30) as response:
        releases = json.load(response)
    for release in releases:
        if not release.get("draft"):
            return release
    raise RuntimeError("Нет опубликованных выпусков")


def main() -> None:
    release = latest_release()
    tag = release["tag_name"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[A-Za-z]+\.\d+)?", tag):
        raise RuntimeError(f"Неожиданный тег: {tag}")
    assets = {asset["name"]: asset["browser_download_url"] for asset in release["assets"]}
    dmg = next((url for name, url in assets.items() if name.endswith(".dmg") and "arm64" in name), None)
    zip_url = next((url for name, url in assets.items() if name.startswith("Koto-Chrome-") and name.endswith(".zip")), None)
    if not dmg or not zip_url:
        raise RuntimeError("В выпуске нет DMG или ZIP расширения")
    path = ROOT / "product.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps(config, ensure_ascii=False, sort_keys=True)
    config["version"] = tag[1:]
    config["links"]["download"] = dmg
    config["links"]["extension_download"] = zip_url
    if json.dumps(config, ensure_ascii=False, sort_keys=True) != before:
        config["verified_on"] = date.today().isoformat()
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("updated", tag)
    else:
        print("up to date", tag)


if __name__ == "__main__":
    main()
