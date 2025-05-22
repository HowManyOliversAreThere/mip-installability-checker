import subprocess

list_file = "input.txt"
idx = 0
with open(list_file, "r") as input_fil, open("output.txt", "w") as result_fil:
    result_fil.write("package_url,mip_installability\n")
    for line in input_fil:
        if not line:
            continue

        idx += 1
        line = line.strip()
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

        success = (
            not timed_out
            and result.returncode == 0
            and result.stdout.decode("utf-8").strip().lower().endswith("done")
        )
        print(f"{idx}: {command_arg} -> {'✅' if success else '❌'}")
        result_fil.write(f"{line},{'✅' if success else '❌'}\n")

print(f"Processed {idx} packages.")
