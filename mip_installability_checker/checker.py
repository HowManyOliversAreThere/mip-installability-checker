import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


def check_installability(slug: str):
    command_arg = slug.replace("https://github.com/", "github:").replace(
        "https://gitlab.com/", "gitlab:"
    )
    timed_out = False
    try:
        result = subprocess.run(
            ["micropython", "-m", "mip", "install", command_arg],
            capture_output=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print(f"Timeout for {slug}")
        timed_out = True
        result = None

    success = (
        not timed_out
        and result is not None
        and result.returncode == 0
        and result.stdout.decode("utf-8").strip().lower().endswith("done")
    )
    print(f"{slug}: {'✅' if success else '❌'}")
    return (slug, success)


def check_installability_many(package_slugs: List[str]):
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(check_installability, slug): (idx, slug)
            for idx, slug in enumerate(package_slugs)
        }
        for future in as_completed(futures):
            result = future.result()
            results[result[0]] = result[1]

    return results
