# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 5.0 POS (Point of Sale) and inventory management system for a Brazilian retail/food-service business ("Adega Gonzaguinha"). Monolithic server-rendered app — no separate frontend framework. UI is all in Portuguese (pt-BR).

## Common Commands

```bash
# Local development setup
python -m venv .venv --clear
source .venv/bin/activate
pip install -r requirements.txt
python contrib/envGen.py        # generates .env with SECRET_KEY + DB placeholders
python manage.py migrate
python manage.py runserver

# Docker development (from infra/)
cd infra && docker compose up   # PostgreSQL 16.8 + Django on port 8000

# Formatting
black .                         # black 24.4.2 (in requirements.txt)

# Management commands
python manage.py update_nivelEstoque    # recalculate stock level flags
python manage.py update_product_stock   # reset all stock to 1000, min to 1
python manage.py fix_tab_statuses       # correct Tab statuses from item data

# Production build (Vercel)
bash build.sh                   # validates env, installs deps, migrates, collectstatic
```

No automated test suite exists yet — all `tests.py` files are Django defaults.

## Architecture

Five Django apps under a `setup/` project config:

- **`core/`** — Landing page, public menu, news/changelog. Contains `TimeStampedModel` abstract base class.
- **`produto/`** — Product & category CRUD, search/filter with pagination (50/page), bulk edit via AJAX, Excel import/export, admin actions. Has `NavigationHistoryMiddleware` for breadcrumbs.
- **`pdv/`** — Point of Sale checkout. Session-based cart (`pdv_itens`, `pdv_subtotal` in `request.session`). On purchase: creates records, decrements stock, calls `caixa.services.registrar_venda_caixa()`. Requires `@caixa_aberto_required`.
- **`comandas/`** — Restaurant-style order tabs. Status flow: VAZIA → ATIVA → FECHADA. Django signals on `TabItem` auto-update tab subtotal/status. Two-step close: first close empties items back to VAZIA, second close moves to FECHADA.
- **`caixa/`** — Cash register sessions. Only one open session at a time. Business logic lives in `services.py` (service layer pattern). Custom `@caixa_aberto_required` decorator in `decorators.py`. Custom `SessaoCaixaManager`.

## Key Patterns

- **Service layer**: `caixa/services.py` separates business logic from views — follow this pattern for new complex logic.
- **Django signals**: `comandas/models.py` uses `post_save`/`post_delete` on `TabItem` to auto-update tab aggregates.
- **Session-based state**: PDV cart lives entirely in `request.session` (no server-side cart model).
- **Environment config**: `python-decouple` reads from `.env`; production uses `setup.staging` settings module.
- **Frontend**: TailwindCSS via CDN (no build step), Font Awesome CDN, vanilla JS inline in `base.html`. No Node.js pipeline.

## Deployment

- **Vercel** (primary): `vercel.json` → Python 3.11 runtime, WSGI at `setup/wsgi.py`, `setup.staging` settings, NeonDB PostgreSQL via `DATABASE_URL`.
- **Railway**: `railway.json` → Nixpacks builder.
- **Docker**: `infra/` has production (`Dockerfile` + gunicorn) and dev (`Dockerfile.dev` + runserver) images with `compose.yaml`.
- **Production settings**: `setup/staging.py` enforces SSL, HSTS, secure cookies, WhiteNoise compressed statics.

## Commit Convention

Prefixes: `Add:`, `Update:`, `Fix:`, `Doc:`, `Style:`, `Refactor:`, `Test:`
