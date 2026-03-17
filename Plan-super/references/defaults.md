# Super Plan — Stack Defaults

When the user doesn't specify a tech stack, apply these defaults unless overridden.

## Backend

| Concern | Default |
|---|---|
| Framework | Laravel (latest stable) |
| PHP version | 8.3+ |
| HTTP client | Saloon |
| Queue | Laravel Queue (Redis driver) |
| Auth | Laravel Sanctum |
| Static analysis | PHPStan level 8 + Larastan |
| Code style | Laravel Pint |
| Testing | Pest |

## Frontend

| Concern | Default |
|---|---|
| Framework | Inertia.js + Svelte 5 |
| Build tool | Vite |
| Styling | Tailwind CSS v4 |
| State | Svelte 5 runes ($state, $derived, $effect) |
| Forms | Inertia useForm |
| HTTP | Inertia router (not fetch) |

## Infrastructure

| Concern | Default |
|---|---|
| CI | GitHub Actions |
| Containerisation | Docker Compose (local), no Kubernetes |
| Deployment | Laravel Forge or Ploi |
| Database | MySQL 8 (primary), Redis (cache/queue) |
| Object storage | S3-compatible (Cloudflare R2) |

## Code Patterns

| Pattern | Default |
|---|---|
| Business logic | Single-action classes (`execute()` method) |
| External APIs | Saloon connectors + requests |
| Data transfer | Laravel Data (Spatie) DTOs |
| Events | Laravel Events + Listeners (queued) |
| Scheduled work | Laravel Scheduler |

## Overriding Defaults

State overrides at the top of your plan:

```
Stack overrides:
- Backend: Node.js + Express (not Laravel)
- Database: PostgreSQL (not MySQL)
```

Unspecified concerns fall back to defaults above.
