# Deployment Guide

## Version Control Workflow

This project follows GitHub Flow:
- `main` is always deployable
- New work happens on feature branches (e.g. `feature/*`, `fix/*`)
- Changes are merged into `main` via reviewed Pull Requests

## Branch Naming Convention

- `feature/description` — new functionality
- `fix/description` — bug fixes
- `hotfix/description` — urgent production fixes

## Merge Strategy

Pull Requests are merged using squash and merge to keep `main`'s history clean and readable.
