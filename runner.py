import sys
import packages_parser


def read_packages_from_file(file_path):
    with open(file_path, 'r') as file:
        packages = [line.strip() for line in file.readlines()]
    return packages


def main():
    if len(sys.argv) != 2:
        print("Usage: python runner.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    packages = read_packages_from_file(file_path)
    packages_parser.parse_packages(packages)


if __name__ == "__main__":
    main()
