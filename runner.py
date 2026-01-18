import sys
import json
import packages_parser


def load_entries(file_path: str):
    """
    1) TXT: new line — google package id
    2) JSON: [
         {"google":"com.x", "apple":"123"},
         {"apple":"284882215"},
         {"google":"com.y"}
       ]
       or JSON: ["com.x", "com.y"]
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        return []

    is_json = file_path.lower().endswith(".json") or raw[:1] in ("[", "{")
    if is_json:
        data = json.loads(raw)

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            if all(isinstance(x, str) for x in data):
                return [{"google": x.strip(), "apple": ""} for x in data if x.strip()]

            if all(isinstance(x, dict) for x in data):
                entries = []
                for x in data:
                    entries.append({
                        "google": (x.get("google") or x.get("package") or x.get("android") or "").strip(),
                        "apple": str(x.get("apple") or x.get("trackId") or x.get("ios") or "").strip(),
                    })
                return entries

        raise ValueError("Unsupported JSON format. Expected list[str] or list[dict].")

    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)

    return [{"google": x, "apple": ""} for x in lines]


def main():
    if len(sys.argv) != 2:
        print("Usage: python runner.py <packages.txt|apps_list.json>")
        sys.exit(1)

    file_path = sys.argv[1]
    entries = load_entries(file_path)

    if not entries:
        print("No entries found.")
        return

    if hasattr(packages_parser, "parse_entries"):
        packages_parser.parse_entries(entries)
        return

    if hasattr(packages_parser, "parse_packages"):
        packages = [e["google"] for e in entries if e.get("google")]
        packages_parser.parse_packages(packages)
        return

    raise RuntimeError("packages_parser has neither parse_entries nor parse_packages.")


if __name__ == "__main__":
    main()
