from mip_installability_checker import checker

list_file = "input.txt"


def parse_input_file():
    # Read all lines at the start
    with open(list_file, "r") as input_fil:
        lines = [line.strip() for line in input_fil if line.strip()]

    results = checker.check_installability_many(lines, verbose=True)

    with open("output.txt", "w") as result_fil:
        result_fil.write("package_url,mip_installability\n")
        for line, status in results.items():
            result_fil.write(f"{line},{'✅' if status else '❌'}\n")

    print(f"Processed {len(lines)} packages.")


if __name__ == "__main__":
    parse_input_file()
