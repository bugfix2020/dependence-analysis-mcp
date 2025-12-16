from __future__ import annotations

from pathlib import Path

from dependence_analysis_mcp.scanner import scan_directory


def test_unused_import_ignored_when_only_in_comment_and_string(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    (src / "a.ts").write_text(
        """
import { foo } from './b'

// foo is mentioned in a comment
const s = "foo in a string";

export const x = 1
""".strip(),
        encoding="utf-8",
    )

    (src / "b.ts").write_text(
        """
export const foo = 123
""".strip(),
        encoding="utf-8",
    )

    r = scan_directory(str(tmp_path), roots=None, include_extensions=None)

    assert any(u.file.endswith("a.ts") and u.importSource == "./b" for u in r.unusedImports)
    assert not any(f.path.endswith("b.ts") for f in r.referencedFiles)


def test_used_import_counts_as_reference(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    (src / "a.ts").write_text(
        """
import { foo } from './b'

export const y = foo + 1
""".strip(),
        encoding="utf-8",
    )

    (src / "b.ts").write_text(
        """
export const foo = 123
""".strip(),
        encoding="utf-8",
    )

    r = scan_directory(str(tmp_path), roots=None, include_extensions=None)

    assert not any(u.file.endswith("a.ts") and u.importSource == "./b" for u in r.unusedImports)
    b = next(f for f in r.referencedFiles if f.path.endswith("b.ts"))
    assert b.importCount == 1


def test_ast_counts_property_access_as_usage(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    (src / "a.ts").write_text(
        """
import foo from './b'

export const z = foo.bar
""".strip(),
        encoding="utf-8",
    )

    (src / "b.ts").write_text(
        """
export default { bar: 1 }
""".strip(),
        encoding="utf-8",
    )

    r = scan_directory(str(tmp_path), roots=None, include_extensions=None)
    assert not any(u.file.endswith("a.ts") and u.importSource == "./b" for u in r.unusedImports)
    assert any(f.path.endswith("b.ts") for f in r.referencedFiles)
