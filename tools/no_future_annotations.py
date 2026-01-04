import ast
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    bad_files: list[str] = []
    for raw in argv[1:]:
        path = Path(raw)
        if path.suffix != ".py":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(content, filename=str(path))
        except SyntaxError:
            # Fall back to a strict line match for unparsable files.
            for line in content.splitlines():
                if line.strip() == "from __future__ import annotations":
                    bad_files.append(str(path))
                    break
            continue

        for node in tree.body:
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "__future__"
                and any(alias.name == "annotations" for alias in node.names)
            ):
                bad_files.append(str(path))
                break

    if not bad_files:
        return 0

    sys.stderr.write("Disallowed future import found. Remove `from __future__ import annotations` from:\n")
    for f in bad_files:
        sys.stderr.write(f" - {f}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
