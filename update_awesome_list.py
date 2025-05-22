import os
from pathlib import Path
import re
import subprocess
import tempfile

from dotenv import load_dotenv
import requests

from mip_installability_checker import checker

load_dotenv()
gh_token = os.environ.get("GITHUB_TOKEN")

awesome_list_url = "https://raw.githubusercontent.com/mcauser/awesome-micropython/refs/heads/master/readme.md"
badge_url = "https://img.shields.io/badge/mip-%E2%9C%93-green?style=flat-square"
badge_link_dest = "https://docs.micropython.org/en/latest/reference/packages.html#installing-packages-with-mip"
repo_regex = re.compile(r"]\((https://git(hu|la)b\.com/[^/]+/[^/]+/?)\) - ")
original_repo = "https://github.com/mcauser/awesome-micropython"
original_branch_name = "master"
fork_repo = "https://github.com/HowManyOliversAreThere/awesome-micropython"
fork_repo_slugs = fork_repo.replace("https://github.com/", "")
fork_branch_name = "update-mip-badges"


def get_awesome_list():
    response = requests.get(awesome_list_url)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch awesome list: {response.status_code} ({response.text})"
        )

    return response.text


def update_awesome_list(output_file="awesome_list.md", pr=False):
    awesome_list = get_awesome_list()
    matches = repo_regex.findall(awesome_list)
    print(f"Found {len(matches)} repositories in the awesome list.")

    slugs = [match[0] for match in matches]
    results = [k for k, v in checker.check_installability_many(slugs).items() if v]
    print(len(results), "newly installable packages")

    for url in results:
        awesome_list = awesome_list.replace(
            f"{url}) - ",
            f"{url}) - <a href='{badge_link_dest}'>![]({badge_url})</a> - ",
        )

    with open(output_file, "w") as output_fil:
        output_fil.write(awesome_list)

    print(f"Updated awesome list saved to {output_file}.")

    if pr:
        # Use gh CLI for all git and PR operations
        with tempfile.TemporaryDirectory() as tmpdir:
            if not gh_token:
                raise RuntimeError(
                    "GITHUB_TOKEN environment variable is not set. "
                    "Please set it to your GitHub token."
                )

            print(f"Cloning repository to {tmpdir}...")
            subprocess.run(["gh", "repo", "clone", original_repo, tmpdir], check=True)

            cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                subprocess.run(["gh", "auth", "setup-git"], check=True)

                # Make sure we're on the original branch
                subprocess.run(["git", "checkout", original_branch_name], check=True)

                # Create and switch to a new branch
                subprocess.run(["git", "checkout", "-b", fork_branch_name], check=True)

                # Copy the updated file to the repo
                source_path = Path(cwd) / output_file
                target_path = Path(tmpdir) / "readme.md"
                with open(source_path, "r") as src, open(target_path, "w") as dst:
                    dst.write(src.read())

                # Add and commit the changes
                subprocess.run(["git", "add", "readme.md"], check=True)
                newline = "\n"
                commit_message = (
                    f"Add MIP installability badges to {len(results)}"
                    f" package{'s' if len(results) > 1 else ''}\n\n"
                    f"{newline.join(['- ' + url for url in results])}"
                )
                subprocess.run(["git", "commit", "-m", commit_message], check=True)

                # Fork the repo if not already forked (gh handles this gracefully)
                subprocess.run(["gh", "repo", "fork", "--remote"], check=True)

                # Push the branch to the fork
                subprocess.run(
                    ["git", "push", "-f", "--set-upstream", "origin", fork_branch_name],
                    check=True,
                )

                try:
                    # Create a pull request using gh
                    pr_title = "Add MIP installability badges"
                    pr_body = (
                        "This PR adds MIP-installability badges (indicating which"
                        " packages can be installed with MIP) to"
                        f" {len(results)} packages.\n\n"
                        "Packages:\n\n"
                        f"{newline.join(['- ' + url for url in results])}\n\n"
                        "🤖 This PR was created by the MIP Installability Checker"
                    )
                    subprocess.run(
                        [
                            "gh",
                            "pr",
                            "create",
                            "--title",
                            pr_title,
                            "--body",
                            pr_body,
                            "--base",
                            original_branch_name,
                            "--repo",
                            original_repo.replace("https://github.com/", ""),
                        ],
                        check=True,
                    )
                except subprocess.CalledProcessError as err:
                    print(f"Failed to create PR: {err}\nIt likely already exists.")

            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    update_awesome_list(pr=True)
