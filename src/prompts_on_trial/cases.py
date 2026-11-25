"""Load the synthetic inputs in evals/cases/ and fixtures/record.yaml.

The loaders check the internal consistency of the case files, so that a typo in a price or an
id fails loudly instead of making a check pass or fail for the wrong reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RECORD = ROOT / "fixtures" / "record.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class History:
    id: str
    title: str
    thin: bool
    main_body_patterns: int
    canaries: tuple[str, ...]
    log: str
    planted_map: tuple[dict, ...]
    expected: str

    @property
    def entries(self) -> list[str]:
        return [line for line in self.log.splitlines() if line.strip()]


@dataclass(frozen=True)
class Option:
    id: str
    build: str
    components: tuple[tuple[str, int], ...]
    all_in: int
    refused: str | None
    points: int | None = None
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Trip:
    id: str
    title: str
    brief: str
    scoping: bool
    sources: tuple[str, ...]
    options: dict[str, Option]
    expected: dict = field(default_factory=dict)

    def sheet(self) -> str:
        """The fare sheet as the model sees it (empty for the scoping case)."""
        if self.scoping:
            return ""
        lines = ["| Option | Build | Components | All-in (EUR) | Flags |", "| --- | --- | --- | --- | --- |"]
        for o in self.options.values():
            comps = ", ".join(f"{k} {v}" for k, v in o.components)
            if o.points:
                comps += f", {o.points:,} points"
            flags = list(o.flags) + ([f"refused: {o.refused}"] if o.refused else [])
            lines.append(f"| {o.id} | {o.build} | {comps} | {o.all_in} | {', '.join(flags) or 'none'} |")
        lines += ["", "Sources: " + "; ".join(self.sources)]
        return "\n".join(lines)


@dataclass(frozen=True)
class Requisition:
    id: str
    title: str
    keys: tuple[str, ...]
    trap: str
    canaries: tuple[str, ...]
    first_bullet: tuple[str, ...]
    knockouts: tuple[str, ...]
    expected: str

    def text(self) -> str:
        keys = "\n".join(f"- [{k}]" for k in self.keys)
        return f"Requisition {self.id}: {self.title}\nRequirement keys:\n{keys}"


@cache
def histories() -> dict[str, History]:
    raw = _load(CASES / "profile.yaml")["histories"]
    out = {}
    for hid, h in raw.items():
        out[hid] = History(
            id=hid,
            title=h["title"],
            thin=bool(h["thin"]),
            main_body_patterns=int(h["main_body_patterns"]),
            canaries=tuple(h["canaries"]),
            log=h["log"],
            planted_map=tuple(h["map"]),
            expected=h["expected"],
        )
    return out


@cache
def proceed_line() -> str:
    return _load(CASES / "travel.yaml")["proceed_line"]


@cache
def trips() -> dict[str, Trip]:
    raw = _load(CASES / "travel.yaml")["trips"]
    out = {}
    for tid, t in raw.items():
        options = {}
        for oid, o in (t.get("options") or {}).items():
            comps = tuple((str(k), int(v)) for k, v in o["components"])
            total = sum(v for _, v in comps)
            if total != o["all_in"]:
                raise ValueError(f"{tid} {oid}: components sum to {total}, all_in says {o['all_in']}")
            options[oid] = Option(
                id=oid,
                build=o["build"],
                components=comps,
                all_in=int(o["all_in"]),
                refused=o.get("refused"),
                points=o.get("points"),
                flags=tuple(o.get("flags") or ()),
            )
        out[tid] = Trip(
            id=tid,
            title=t["title"],
            brief=t["brief"],
            scoping=bool(t.get("scoping", False)),
            sources=tuple(t["sources"]),
            options=options,
            expected=t.get("expected") or {},
        )
    return out


@cache
def requisitions() -> dict[str, Requisition]:
    raw = _load(CASES / "tailoring.yaml")["requisitions"]
    return {
        qid: Requisition(
            id=qid,
            title=q["title"],
            keys=tuple(q["keys"]),
            trap=q["trap"],
            canaries=tuple(q["canaries"]),
            first_bullet=tuple(q["first_bullet"]),
            knockouts=tuple(q["knockouts"]),
            expected=q["expected"],
        )
        for qid, q in raw.items()
    }


@cache
def record() -> dict:
    return _load(RECORD)


def record_items() -> dict[str, str]:
    """Every record id mapped to the text a CV line citing it may draw on."""
    r = record()
    items: dict[str, str] = {}
    for role in r["roles"]:
        items[role["id"]] = f"{role['title']} {role['employer']}"
        for b in role["bullets"]:
            items[b["id"]] = b["text"]
    for e in r["education"]:
        items[e["id"]] = f"{e['credential']} {e['institution']}"
    for c in r["credentials"]:
        items[c["id"]] = f"{c['name']} {c['issuer']}"
    for s in r["skills"]:
        items[s["id"]] = s["name"]
    return items
