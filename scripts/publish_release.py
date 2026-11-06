"""Publish the tools inventory and assets from the current Git commit."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def gh(*args):
    subprocess.run(["gh", *args], cwd=ROOT, check=True)


def package_tools(catalog, output):
    for tool in catalog["tools"]:
        if tool["package"] == "existing-release":
            continue
        destination = output / tool["asset"]
        if tool["package"] == "file":
            shutil.copyfile(ROOT / tool["entry"], destination)
        else:
            directory = ROOT / tool["directory"]
            with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
                for source in sorted(directory.rglob("*")):
                    if source.is_file():
                        archive.write(source, source.relative_to(directory.parent))


def copy_existing_assets(catalog, output):
    for asset in catalog["existing_release_assets"]:
        destination = output / asset["name"]
        request = Request(asset["url"], headers={"User-Agent": "lol-tools-release"})
        with urlopen(request, timeout=120) as response, destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        if digest != asset["sha256"]:
            raise ValueError(f"Release asset checksum mismatch: {asset['name']}")


def release_notes(catalog, tag, commit, repository):
    release_url = f"https://github.com/{repository}/releases/download/{tag}"
    lines = [
        "# 小程序合集",
        "",
        f"与主库提交 [{commit[:7]}](https://github.com/{repository}/tree/{commit}) 对应，共 **{len(catalog['tools'])} 个工具**。",
        "",
        "| 工具 | 主库入口与说明 | 下载 |",
        "| --- | --- | --- |",
    ]
    for tool in catalog["tools"]:
        directory = f"https://github.com/{repository}/tree/{commit}/{tool['directory']}"
        asset_url = f"{release_url}/{quote(tool['asset'], safe='')}"
        download = f"[{tool['kind']}]({asset_url})"
        if tool["id"] == "filename-cleaner":
            download += f" · [原 Windows 成品]({release_url}/Remove.special.file.name.zip)"
        lines.append(f"| {tool['name']} | [目录与用法]({directory}) | {download} |")
    lines.extend([
        "",
        f"[完整主库源码包]({release_url}/lol-tools-source.zip)",
        "",
        "Python 工具的独立 ZIP 包含源码、说明及对应依赖列表；HTML 工具下载后用浏览器打开。",
        "图片转 PDF＋Word、图片转 PDF、简单锁屏当前只有成品，主库保存对应说明与下载入口。",
        "4 份历史成品附件经过 SHA-256 核对后原样复制；文件名清理同时提供当前源码和原 Windows 成品。",
        "各附件的 SHA-256 见 SHA256SUMS.txt。历史 Release 继续保留。",
    ])
    return "\n".join(lines) + "\n"


def main():
    import os

    catalog = json.loads((ROOT / "tools.json").read_text())
    repository = os.environ["GH_REPO"]
    commit = git("rev-parse", "HEAD")
    date = datetime.fromisoformat(git("show", "-s", "--format=%cI", "HEAD"))
    date = date.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    tag = f"tools-{date.replace('-', '')}-{commit[:7]}"
    existing = subprocess.run(
        ["gh", "release", "view", tag, "--json", "isDraft"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if existing.returncode == 0 and not json.loads(existing.stdout)["isDraft"]:
        print(f"Matching release already published: {tag}")
        return

    with tempfile.TemporaryDirectory(prefix="lol-release-") as temporary:
        output = Path(temporary)
        package_tools(catalog, output)
        copy_existing_assets(catalog, output)
        subprocess.run([
            "git", "archive", "--format=zip", "--prefix=lol-tools/",
            f"--output={output / 'lol-tools-source.zip'}", commit,
        ], cwd=ROOT, check=True)
        sums = []
        for asset in sorted(output.iterdir()):
            sums.append(f"{hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}")
        (output / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n")
        notes = output / "release-notes.md"
        notes.write_text(release_notes(catalog, tag, commit, repository))
        if existing.returncode != 0:
            gh("release", "create", tag, "--target", commit, "--draft",
               "--title", f"小程序合集 · {date}", "--notes-file", str(notes))
        assets = [str(path) for path in sorted(output.iterdir()) if path != notes]
        gh("release", "upload", tag, *assets, "--clobber")
        gh("release", "edit", tag, "--notes-file", str(notes), "--draft=false", "--latest")
        print(f"Published https://github.com/{repository}/releases/tag/{tag}")


if __name__ == "__main__":
    main()
