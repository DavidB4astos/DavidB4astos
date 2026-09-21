"""Render public GitHub metrics without credentials or private repository access."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

USER = "DavidB4astos"


def get(path):
    request = Request(
        f"https://api.github.com/{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "public-profile-stats"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


profile = get(f"users/{USER}")
repos = []
page = 1
while True:
    batch = get(f"users/{USER}/repos?type=owner&per_page=100&page={page}")
    repos.extend(repo for repo in batch if not repo["private"])
    if len(batch) < 100:
        break
    page += 1
originals = [repo for repo in repos if not repo["fork"]]
metrics = [
    ("Public repositories", len(repos)),
    ("Stars earned", sum(repo["stargazers_count"] for repo in originals)),
    ("Forks of original projects", sum(repo["forks_count"] for repo in originals)),
    ("Followers", profile["followers"]),
]
rows = "\n".join(
    f'<text x="25" y="{78 + i * 30}" fill="#c9d1d9">{label}</text>'
    f'<text x="420" y="{78 + i * 30}" text-anchor="end" fill="#f0f6fc">{value}</text>'
    for i, (label, value) in enumerate(metrics)
)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="195" viewBox="0 0 450 195" role="img" aria-labelledby="title">
<title id="title">David Bastos — public GitHub statistics</title>
<rect x="0.5" y="0.5" width="449" height="194" rx="6" fill="#0d1117" stroke="#30363d"/>
<g font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14">
<text x="25" y="36" fill="#ef4444" font-size="20" font-weight="600">GitHub Stats</text>
{rows}
</g></svg>
'''
Path("assets").mkdir(exist_ok=True)
Path("assets/stats.svg").write_text(svg, encoding="utf-8")
