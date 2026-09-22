#!/usr/bin/env python3
"""按 mapping.tsv 重排 rime-cangjie 仓颉码表键位。

用法:
    python3 remap_cangjie.py            # 试运行（dry-run），只显示将发生的改动
    python3 remap_cangjie.py --write    # 实际修改 rime-cangjie/ 并生成 build/
    python3 remap_cangjie.py --force    # 即使 rime-cangjie/ 有未提交改动也强行运行（危险）

处理对象（rime-cangjie/ 目录）:
    *.dict.yaml    码表文件：置换所有「仅由 [a-z'] 组成且含字母」的列（code、stem）
    *.schema.yaml  方案文件：置换 xlit|abc|字根| 行中的字根显示串

完成后将 rime-cangjie/ 全部内容（不含 .git）复制到 build/，然后还原
rime-cangjie/ 的改动，使其保持干净（结果只保留在 build/ 中）。

幂等性说明:
    本脚本直接原地修改 rime-cangjie/。置换做两次会叠加，因此运行前要求
    rime-cangjie/ 的 git 工作区干净；若上次 --write 后还原失败，请先:
        git -C rime-cangjie restore .
    或使用 --force 跳过检查。

mapping.tsv: 两列（字根 -> 目标键位），# 开头为注释，未列出的字根保持默认键位。
"""

import shutil
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent / "rime-cangjie"
BUILD = Path(__file__).resolve().parent / "build"
MAPPING = Path(__file__).resolve().parent / "mapping.tsv"

# 默认布局: 键位 -> 字根（z=符）
DEFAULT_KEYS = "abcdefghijklmnopqrstuvwxyz"
DEFAULT_RADICALS = "日月金木水火土竹戈十大中一弓人心手口尸廿山女田難卜符"

CODE_CHARS = set(DEFAULT_KEYS) | {"'"}


def load_mapping() -> dict[str, str]:
    """返回 字根 -> 键位 的覆盖映射。"""
    overrides: dict[str, str] = {}
    for lineno, raw in enumerate(MAPPING.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            sys.exit(f"mapping.tsv 第 {lineno} 行格式错误（应为两列）: {raw!r}")
        radical, key = parts[0], parts[1].lower()
        if radical not in DEFAULT_RADICALS:
            sys.exit(f"mapping.tsv 第 {lineno} 行: 未知的字根 {radical!r}")
        if key not in DEFAULT_KEYS:
            sys.exit(f"mapping.tsv 第 {lineno} 行: 无效的键位 {key!r}（只能 a-z）")
        if radical in overrides:
            sys.exit(f"mapping.tsv 第 {lineno} 行: 字根 {radical!r} 重复定义")
        overrides[radical] = key
    return overrides


def build_maps(overrides: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """返回 (key_to_rad, rad_to_key)，并校验是一一映射。"""
    rad_to_key = {r: k for r, k in zip(DEFAULT_RADICALS, DEFAULT_KEYS)}
    rad_to_key.update(overrides)
    keys = list(rad_to_key.values())
    if len(keys) != len(set(keys)):
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        sys.exit(f"多个字根被分配到同一键位: {dupes}，请保证一一映射")
    key_to_rad = {k: r for r, k in rad_to_key.items()}
    return key_to_rad, rad_to_key


def ensure_clean_repo(force: bool) -> None:
    """rime-cangjie 必须是干净的 git 工作区，防止重复置换叠加。"""
    import subprocess

    # 子模块中 .git 是文件（指向父仓库 .git/modules/...），普通仓库中是目录
    if not (DIR / ".git").exists():
        if not force:
            sys.exit(f"{DIR} 不是 git 仓库，无法保证幂等；确认无误可用 --force")
        return
    r = subprocess.run(
        ["git", "-C", str(DIR), "status", "--porcelain", "--", "."],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.exit(f"git status 失败: {r.stderr.strip()}")
    if r.stdout.strip() and not force:
        sys.exit(
            f"{DIR} 有未提交的改动，可能已被置换过一次。请先还原:\n"
            f"    git -C {DIR} restore .\n"
            f"或加 --force 强行运行（危险）。"
        )


def remap_code(code: str, letter_map: dict[str, str]) -> str:
    return "".join(letter_map.get(c, c) for c in code)


def is_code_field(field: str) -> bool:
    return bool(field) and set(field) <= CODE_CHARS and any(c.islower() for c in field)


def remap_dict_file(
    path: Path, letter_map: dict[str, str], write: bool
) -> list[tuple[str, str, str]]:
    """原地置换一个 dict.yaml 中所有编码列。返回抽样对照 (汉字, 旧码, 新码)。"""
    raw = path.read_bytes().decode("utf-8")
    lines = raw.split("\n")  # 保留行尾 \r
    out, samples, in_body = [], [], False
    for line in lines:
        if not in_body:
            in_body = line.rstrip("\r") == "..."
            out.append(line)
            continue
        stripped = line.rstrip("\r")
        if stripped:
            fields = stripped.split("\t")
            changed = False
            for i, f in enumerate(fields):
                if is_code_field(f):
                    new_code = remap_code(f, letter_map)
                    if len(samples) < 8 and len(f) <= 3:
                        samples.append((fields[0], f, new_code))
                    if new_code != f:
                        fields[i] = new_code
                        changed = True
            if changed:
                line = "\t".join(fields) + ("\r" if line != stripped else "")
        out.append(line)
    new_raw = "\n".join(out)
    if write and new_raw != raw:
        path.write_bytes(new_raw.encode("utf-8"))
        print(f"已写入 {path}")
    return samples


XLIT_RE_DUMMY = None  # xlit 处理见下


def remap_pattern(pattern: str, letter_map: dict[str, str]) -> str:
    """置换正则模式中的字面字母（仅限不含字符类的简单模式，如 ^z.*$）。"""
    if "[" in pattern or "A-Z" in pattern:
        return pattern  # 含字符类（如 [A-Za-z]），不做置换
    return "".join(letter_map.get(c, c) if c.islower() else c for c in pattern)


def remap_xlit_file(
    path: Path, key_to_rad: dict[str, str], letter_map: dict[str, str], write: bool
) -> None:
    """原地置换 schema yaml 中 xlit|src|dst| 行的字根显示串，
    以及 disable_user_dict_for_patterns 中的按键模式。"""
    import re

    xlit_re = re.compile(r"xlit\|([^|]*)\|([^|]*)\|")
    text = path.read_text(encoding="utf-8")
    changed = 0

    def repl(m: re.Match) -> str:
        nonlocal changed
        src, dst = m.group(1), m.group(2)
        # 尾部的 ～ / ~ 不是字根，单独保留
        suffix = ""
        core = dst
        while core and core[-1] in "～~":
            suffix = core[-1] + suffix
            core = core[:-1]
        new_dst = (
            "".join(key_to_rad[c.lower()] if c.lower() in key_to_rad else c for c in src)[
                : len(core)
            ]
            + suffix
        )
        if new_dst != dst:
            changed += 1
        return f"xlit|{src}|{new_dst}|"

    new_lines = []
    in_patterns_block = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("disable_user_dict_for_patterns:"):
            in_patterns_block = True
        elif in_patterns_block:
            if stripped.startswith("-"):
                m = re.match(r"(\s*-\s*\"?)([^\"]+)(\"?\s*(?:#.*)?(?:\r?\n)?)$", line)
                if m:
                    new_pat = remap_pattern(m.group(2), letter_map)
                    if new_pat != m.group(2):
                        changed += 1
                        new_line = line[: m.start(2)] + new_pat + line[m.end(2) :]
                        print(f"{path.name}:\n  - {line.strip()}\n  + {new_line.strip()}")
                    line = line[: m.start(2)] + new_pat + line[m.end(2) :]
            else:
                in_patterns_block = False  # 块结束
        if "xlit|" in line and not stripped.startswith("#"):
            line = xlit_re.sub(repl, line)
        new_lines.append(line)
    new_text = "".join(new_lines)
    # 展示新旧对照
    old_lines = [
        ln for ln in text.splitlines() if "xlit|" in ln and not ln.lstrip().startswith("#")
    ]
    new_lines2 = [
        ln for ln in new_text.splitlines() if "xlit|" in ln and not ln.lstrip().startswith("#")
    ]
    for o, nw in zip(old_lines, new_lines2):
        if o != nw:
            print(f"{path.name}:\n  - {o.strip()}\n  + {nw.strip()}")
    if changed == 0:
        print(f"警告: {path.name} 中未找到需要更新的 xlit 行")
    if write and new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"已写入 {path}")


def reset_submodule() -> None:
    """还原 rime-cangjie/ 中的改动，只保留 build/ 里的置换结果。"""
    import subprocess

    r = subprocess.run(
        ["git", "-C", str(DIR), "restore", "."],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.exit(f"git restore 失败: {r.stderr.strip()}")
    print(f"已还原 {DIR} 到干净状态")


def copy_to_build() -> None:
    """清空并重建 build/，复制 rime-cangjie 全部内容（不含 .git）。"""
    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(
        DIR,
        BUILD,
        ignore=shutil.ignore_patterns(".git"),
    )
    n = sum(1 for p in BUILD.rglob("*") if p.is_file())
    print(f"已复制 {n} 个文件到 {BUILD}")


def main() -> None:
    write = "--write" in sys.argv
    force = "--force" in sys.argv
    if not DIR.is_dir():
        sys.exit(f"找不到目录 {DIR}")
    ensure_clean_repo(force)

    overrides = load_mapping()
    key_to_rad, rad_to_key = build_maps(overrides)
    # 旧字母 l 代表字根 DEFAULT_RADICALS[i]，该字根的新键位是 rad_to_key[r]
    letter_map = {ol: rad_to_key[r] for ol, r in zip(DEFAULT_KEYS, DEFAULT_RADICALS)}
    changed = {f"{ol}->{m}" for ol, m in letter_map.items() if ol != m}
    if not changed:
        print("映射为空（全部保持默认），输出将与原始码表一致。")
    else:
        print(f"键位变化（{len(changed)} 个）: {' '.join(sorted(changed))}")

    dict_files = sorted(DIR.glob("*.dict.yaml"))
    if not dict_files:
        sys.exit(f"{DIR} 下没有找到 *.dict.yaml")
    samples: list[tuple[str, str, str]] = []
    for f in dict_files:
        samples += remap_dict_file(f, letter_map, write)

    print("编码抽样:")
    for ch, old, new in samples:
        mark = " " if old != new else "*"
        print(f"  {mark} {ch}: {old} -> {new}")

    for f in sorted(DIR.glob("*.schema.yaml")):
        remap_xlit_file(f, key_to_rad, letter_map, write)

    if write:
        copy_to_build()
        reset_submodule()
        print("\n完成。若键位有变，请重新部署 fcitx5。")
    else:
        print("\n以上为试运行结果。确认无误后加 --write 参数实际写入并生成 build/。")


if __name__ == "__main__":
    main()
