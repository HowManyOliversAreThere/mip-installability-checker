import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

list_file = "input.txt"


def check_installability(idx, line):
    command_arg = line.replace("https://github.com/", "github:").replace(
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
        print(f"Timeout for {idx}: {command_arg}")
        timed_out = True
        result = None

    success = (
        not timed_out
        and result is not None
        and result.returncode == 0
        and result.stdout.decode("utf-8").strip().lower().endswith("done")
    )
    print(f"{idx}: {command_arg} -> {'✅' if success else '❌'}")
    return (line, "✅" if success else "❌")


# Read all lines at the start
with open(list_file, "r") as input_fil:
    lines = [line.strip() for line in input_fil if line.strip()]

results = []
with ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(check_installability, idx + 1, line): (idx, line)
        for idx, line in enumerate(lines)
    }
    for future in as_completed(futures):
        results.append(future.result())

# Preserve original order
results.sort(key=lambda x: lines.index(x[0]))

with open("output.txt", "w") as result_fil:
    result_fil.write("package_url,mip_installability\n")
    for line, status in results:
        result_fil.write(f"{line},{status}\n")

print(f"Processed {len(lines)} packages.")
