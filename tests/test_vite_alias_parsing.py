from __future__ import annotations

from pathlib import Path

from dependence_analysis_mcp.resolve import load_vite_aliases


def test_load_vite_aliases_object_string(tmp_path: Path) -> None:
    (tmp_path / "vite.config.ts").write_text(
        """
import { defineConfig } from 'vite'

export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '~': 'src'
    }
  }
})
""".strip(),
        encoding="utf-8",
    )

    rules, warnings = load_vite_aliases(tmp_path)
    assert warnings == []
    mapping = {r.find: r.replacement for r in rules}
    assert "@" in mapping
    assert Path(mapping["@"]).name == "src"


def test_load_vite_aliases_array_path_resolve(tmp_path: Path) -> None:
    (tmp_path / "vite.config.ts").write_text(
        """
import path from 'path'

export default {
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(__dirname, 'src') },
    ]
  }
}
""".strip(),
        encoding="utf-8",
    )

    rules, warnings = load_vite_aliases(tmp_path)
    assert warnings == []
    assert any(r.find == "@" and Path(r.replacement).name == "src" for r in rules)


def test_load_vite_aliases_url_pathname(tmp_path: Path) -> None:
    (tmp_path / "vite.config.ts").write_text(
        """
export default {
  resolve: {
    alias: [
      { find: '@', replacement: new URL('./src', import.meta.url).pathname },
    ]
  }
}
""".strip(),
        encoding="utf-8",
    )

    rules, warnings = load_vite_aliases(tmp_path)
    assert warnings == []
    assert any(r.find == "@" and Path(r.replacement).name == "src" for r in rules)


def test_load_vite_aliases_file_url_to_path(tmp_path: Path) -> None:
    (tmp_path / "vite.config.ts").write_text(
        """
import { fileURLToPath, URL } from 'node:url'

export default {
  resolve: {
    alias: [
      { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
    ]
  }
}
""".strip(),
        encoding="utf-8",
    )

    rules, warnings = load_vite_aliases(tmp_path)
    assert warnings == []
    assert any(r.find == "@" and Path(r.replacement).name == "src" for r in rules)


def test_load_vite_aliases_import_meta_dirname(tmp_path: Path) -> None:
    (tmp_path / "vite.config.ts").write_text(
        """
import path from 'node:path'

export default {
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(import.meta.dirname, 'src') },
    ]
  }
}
""".strip(),
        encoding="utf-8",
    )

    rules, warnings = load_vite_aliases(tmp_path)
    assert warnings == []
    assert any(r.find == "@" and Path(r.replacement).name == "src" for r in rules)
