import html
import json
import os
import re
import urllib.request

README = "README.md"
START = "<!-- projects:start -->"
END = "<!-- projects:end -->"

QUERY = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes { ... on Repository { name description url } }
    }
  }
}
"""


def fetch_pins(login, token):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["pinnedItems"]["nodes"]


def render_cell(repo):
    if repo is None:
        return '    <td width="50%" valign="top"></td>'
    name = html.escape(repo["name"])
    description = html.escape(repo["description"] or "")
    return (
        '    <td width="50%" valign="top">\n'
        f'      <a href="{repo["url"]}"><b>{name}</b></a><br />\n'
        f"      <sub>{description}</sub>\n"
        "    </td>"
    )


def render_table(repos):
    rows = []
    for i in range(0, len(repos), 2):
        pair = repos[i : i + 2] + [None] * (2 - len(repos[i : i + 2]))
        rows.append("  <tr>\n" + "\n".join(map(render_cell, pair)) + "\n  </tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main():
    repos = fetch_pins(os.environ["GITHUB_LOGIN"], os.environ["GITHUB_TOKEN"])
    with open(README) as file:
        readme = file.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    updated = pattern.sub(lambda _: f"{START}\n{render_table(repos)}\n{END}", readme)
    with open(README, "w") as file:
        file.write(updated)


if __name__ == "__main__":
    main()
