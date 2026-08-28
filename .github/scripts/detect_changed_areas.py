#!/usr/bin/env python3
"""Detect CI areas changed by a pull request or push event."""

from __future__ import annotations

import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    from github_api import GitHubApiError, next_link, request_json
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from github_api import GitHubApiError, next_link, request_json

FILTERS = {
    "frontend": [
        "frontend/**",
        "Makefile",
        ".github/workflows/ci.yml",
    ],
    "backend": [
        ".github/scripts/**",
        "app/**",
        "tests/**",
        "config/**",
        "scripts/**",
        "pyproject.toml",
        "uv.lock",
        "Makefile",
        "docs/reference/settings.md",
        ".env.example",
    ],
    "helm": [
        "deploy/helm/**",
        "Makefile",
    ],
    "docker": [
        "Dockerfile",
        "Dockerfile.*",
        ".dockerignore",
        "docker-compose*.yml",
        "app/**",
        "config/**",
        "frontend/**",
        "scripts/**",
        "pyproject.toml",
        "uv.lock",
    ],
    "migrations": [
        "app/db/alembic/**",
        "pyproject.toml",
        "uv.lock",
    ],
}


def _event() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("GITHUB_EVENT_PATH is required")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def _pull_request_files(event: dict[str, Any]) -> list[str]:
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        raise SystemExit("pull_request event payload is required")
    files_url = pull_request.get("url")
    if not isinstance(files_url, str) or not files_url:
        raise SystemExit("pull_request.url missing from event payload")
    url: str | None = f"{files_url}/files?per_page=100"
    files: list[str] = []
    while url:
        try:
            payload, link = request_json(url)
        except GitHubApiError as exc:
            print(
                f"warning: GitHub PR files request failed after retries; falling back to the full CI suite: {exc}",
                flush=True,
            )
            return [
                "frontend/__github_api_unavailable__",
                "app/__github_api_unavailable__",
                "deploy/helm/__github_api_unavailable__",
                "Dockerfile",
                "app/db/alembic/__github_api_unavailable__",
            ]
        if not isinstance(payload, list):
            raise SystemExit(f"GitHub PR files request returned {type(payload).__name__}, expected list")
        for item in payload:
            if isinstance(item, dict) and isinstance(item.get("filename"), str):
                files.append(item["filename"])
        url = next_link(link)
    return files


def _push_files(event: dict[str, Any]) -> list[str]:
    """Return paths changed by commits included in a push payload."""
    commits = event.get("commits")
    if not isinstance(commits, list):
        raise SystemExit("push.commits missing from event payload")

    files: list[str] = []
    for commit in commits:
        if not isinstance(commit, dict):
            continue
        for key in ("added", "modified", "removed"):
            paths = commit.get(key)
            if isinstance(paths, list):
                files.extend(path for path in paths if isinstance(path, str))
    if files:
        return list(dict.fromkeys(files))

    repository = event.get("repository")
    repository_name = repository.get("full_name") if isinstance(repository, dict) else None
    before = event.get("before")
    after = event.get("after")
    if isinstance(repository_name, str) and isinstance(before, str) and isinstance(after, str):
        try:
            payload, _ = request_json(f"https://api.github.com/repos/{repository_name}/compare/{before}...{after}")
        except GitHubApiError as exc:
            print(
                f"warning: GitHub push comparison failed; falling back to the full CI suite: {exc}",
                flush=True,
            )
        else:
            compared_files = (
                [
                    item["filename"]
                    for item in payload.get("files", [])
                    if isinstance(item, dict) and isinstance(item.get("filename"), str)
                ]
                if isinstance(payload, dict)
                else []
            )
            if compared_files:
                return list(dict.fromkeys(compared_files))

    # GitHub can omit the commit list for oversized or synthetic push events.
    # Keep the safety property that an unknown change runs the complete suite.
    return [
        "frontend/__github_push_files_unavailable__",
        "app/__github_push_files_unavailable__",
        "deploy/helm/__github_push_files_unavailable__",
        "Dockerfile",
        "app/db/alembic/__github_push_files_unavailable__",
    ]


def _changed_files(event: dict[str, Any]) -> list[str]:
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    if event_name == "push" or "commits" in event:
        return _push_files(event)
    return _pull_request_files(event)


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


def main() -> int:
    files = _changed_files(_event())
    outputs = {name: any(_matches(path, patterns) for path in files) for name, patterns in FILTERS.items()}
    output_path = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{name}={'true' if matched else 'false'}" for name, matched in outputs.items()]
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as fh:
            for line in lines:
                print(line, file=fh)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
