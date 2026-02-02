import requests
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

root = Path(__file__).parent.parent
dest = root / "freqtrade" / "rpc" / "api_server" / "ui" / "installed"
base_url = "https://api.github.com/repos/freqtrade/frequi/releases"
r = requests.get(base_url, timeout=60).json()
tmp = [x for x in r if not x.get("prerelease")]
tmp.sort(key=lambda x: x["created_at"], reverse=True)
latest = tmp[0]
version = latest["name"]
assets = latest.get("assets", [])
if assets:
    url = assets[0]["browser_download_url"]
else:
    assets_url = latest["assets_url"]
    assets = requests.get(assets_url, timeout=60).json()
    url = assets[0]["browser_download_url"]
if dest.is_dir():
    for p in reversed(list(dest.glob("**/*"))):
        if p.name in (".gitkeep", "fallback_file.html", ".uiversion"):
            continue
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            p.rmdir()
dest.mkdir(parents=True, exist_ok=True)
content = requests.get(url, timeout=60).content
with ZipFile(BytesIO(content)) as zf:
    for fn in zf.filelist:
        with zf.open(fn) as x:
            destfile = dest / fn.filename
            if fn.is_dir():
                destfile.mkdir(exist_ok=True)
            else:
                destfile.write_bytes(x.read())
with (dest / ".uiversion").open("w") as f:
    f.write(version)
