from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pytest


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class TestCaseGroup:
    name: str
    description: str
    targets: tuple[str, ...]


CASE_GROUPS = {
    "domain": TestCaseGroup(
        name="domain",
        description="Modelos, inventário, banco e regras centrais de tabuleiro.",
        targets=(
            "tests/test_domain_models.py",
            "tests/test_core_systems.py",
        ),
    ),
    "cards": TestCaseGroup(
        name="cards",
        description="Cartas de desenvolvimento e progressão de turnos.",
        targets=(
            "tests/test_development_cards.py",
            "tests/test_progress_cards.py",
        ),
    ),
    "ui": TestCaseGroup(
        name="ui",
        description="Componentes visuais, diálogos e HUD.",
        targets=(
            "tests/test_components_behavior.py",
            "tests/test_ui_dialogs.py",
        ),
    ),
    "runtime": TestCaseGroup(
        name="runtime",
        description="Cenas principais, fluxo do jogo e integração de runtime.",
        targets=(
            "tests/test_scenes_and_runtime.py",
            "tests/test_ui_dialogs.py",
        ),
    ),
    "system": TestCaseGroup(
        name="system",
        description="Testes de sistema de ponta a ponta e recuperação.",
        targets=(
            "tests/test_system_full_game.py",
        ),
    ),
    "all": TestCaseGroup(
        name="all",
        description="Suíte completa do projeto.",
        targets=("tests",),
    ),
}


class TestDriver:
    def __init__(self, groups: dict[str, TestCaseGroup] | None = None):
        self.groups = groups or CASE_GROUPS

    def list_groups(self) -> list[str]:
        return [f"{group.name}: {group.description}" for group in self.groups.values()]

    def resolve_targets(self, selected_groups: Iterable[str] | None = None) -> list[str]:
        group_names = list(selected_groups or ("all",))
        resolved: list[str] = []
        seen = set()

        for name in group_names:
            if name not in self.groups:
                raise KeyError(f"Grupo de testes desconhecido: {name}")
            for target in self.groups[name].targets:
                if target in seen:
                    continue
                seen.add(target)
                resolved.append(target)

        return resolved

    def run(self, selected_groups: Iterable[str] | None = None, pytest_args: list[str] | None = None) -> int:
        args = list(pytest_args or [])
        args.extend(self.resolve_targets(selected_groups))
        return pytest.main(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Driver de testes por grupos de casos.")
    parser.add_argument(
        "-g",
        "--group",
        action="append",
        choices=sorted(CASE_GROUPS.keys()),
        help="Grupo de testes a executar. Pode ser usado mais de uma vez.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista os grupos disponíveis e encerra.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, pytest_args = parser.parse_known_args(argv)

    driver = TestDriver()

    if args.list:
        for line in driver.list_groups():
            print(line)
        return 0

    return driver.run(args.group, pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())
