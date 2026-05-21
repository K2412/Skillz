# Laravel Best Practices

Best practices for Laravel, prioritized by impact. Each rule teaches what to do and why. For exact API syntax, verify with `search-docs`.

## Consistency First

Before applying any rule, check what the application already does. Laravel offers multiple valid approaches — the best choice is the one the codebase already uses, even if another pattern would be theoretically better. Inconsistency is worse than a suboptimal pattern.

Check sibling files, related controllers, models, or tests for established patterns. If one exists, follow it — don't introduce a second way. These rules are defaults for when no pattern exists yet, not overrides.

## Quick Reference

### 1. Database Performance → `rules/db-performance.md`

- Eager load with `with()` to prevent N+1 queries
- Enable `Model::preventLazyLoading()` in development
- Select only needed columns, avoid `SELECT *`
- `chunk()` / `chunkById()` for large datasets
- Index columns used in `WHERE`, `ORDER BY`, `JOIN`
- `withCount()` instead of loading relations to count
- `cursor()` for memory-efficient read-only iteration
- Never query in Blade templates

### 2. Advanced Query Patterns → `rules/advanced-queries.md`

- `addSelect()` subqueries over eager-loading entire has-many for a single value
- Dynamic relationships via subquery FK + `belongsTo`
- Conditional aggregates (`CASE WHEN` in `selectRaw`) over multiple count queries
- `setRelation()` to prevent circular N+1 queries
- `whereIn` + `pluck()` over `whereHas` for better index usage
- Two simple queries can beat one complex query
- Compound indexes matching `orderBy` column order
- Correlated subqueries in `orderBy` for has-many sorting (avoid joins)

### 3. Security → `rules/security.md`

- Define `$fillable` or `$guarded` on every model, authorize every action via policies or gates
- No raw SQL with user input — use Eloquent or query builder
- `{{ }}` for output escaping, `@csrf` on all POST/PUT/DELETE forms, `throttle` on auth and API routes
- Validate MIME type, extension, and size for file uploads
- Never commit `.env`, use `config()` for secrets, `encrypted` cast for sensitive DB fields

### 4. Caching → `rules/caching.md`

- `Cache::remember()` over manual get/put
- `Cache::flexible()` for stale-while-revalidate on high-traffic data
- `Cache::memo()` to avoid redundant cache hits within a request
- Cache tags to invalidate related groups
- `Cache::add()` for atomic conditional writes
- `once()` to memoize per-request or per-object lifetime
- `Cache::lock()` / `lockForUpdate()` for race conditions
- Failover cache stores in production

### 5. Eloquent Patterns → `rules/eloquent.md`

- Correct relationship types with return type hints
- Local scopes for reusable query constraints
- Global scopes sparingly — document their existence
- Attribute casts in the `casts()` method
- Cast date columns, use Carbon instances in templates
- `whereBelongsTo($model)` for cleaner queries
- Never hardcode table names — use `(new Model)->getTable()` or Eloquent queries

### 6. Validation & Forms → `rules/validation.md`

- Form Request classes, not inline validation
- Array notation `['required', 'email']` for new code; follow existing convention
- `$request->validated()` only — never `$request->all()`
- `Rule::when()` for conditional validation
- `after()` instead of `withValidator()`

### 7. Configuration → `rules/config.md`

- `env()` only inside config files
- `App::environment()` or `app()->isProduction()`
- Config, lang files, and constants over hardcoded text

### 8. Testing Patterns → `rules/testing.md`

- `LazilyRefreshDatabase` over `RefreshDatabase` for speed
- `assertModelExists()` over raw `assertDatabaseHas()`
- Factory states and sequences over manual overrides
- Use fakes (`Event::fake()`, `Exceptions::fake()`, etc.) — but always after factory setup, not before
- `recycle()` to share relationship instances across factories

### 9. Queue & Job Patterns → `rules/queue-jobs.md`

- `retry_after` must exceed job `timeout`; use exponential backoff `[1, 5, 10]`
- `ShouldBeUnique` to prevent duplicates; `ShouldBeUniqueUntilProcessing` for early lock release
- Always implement `failed()`; with `retryUntil()`, set `$tries = 0`
- `RateLimited` middleware for external API calls; `Bus::batch()` for related jobs
- Horizon for complex multi-queue scenarios

### 10. Routing & Controllers → `rules/routing.md`

- Implicit route model binding
- Scoped bindings for nested resources
- `Route::resource()` or `apiResource()`
- Methods under 10 lines — extract to actions/services
- Type-hint Form Requests for auto-validation

### 11. HTTP Client → `rules/http-client.md`

- Explicit `timeout` and `connectTimeout` on every request
- `retry()` with exponential backoff for external APIs
- Check response status or use `throw()`
- `Http::pool()` for concurrent independent requests
- `Http::fake()` and `preventStrayRequests()` in tests

### 12. Events, Notifications & Mail → `rules/events-notifications.md`, `rules/mail.md`

- Event discovery over manual registration; `event:cache` in production
- `ShouldDispatchAfterCommit` / `afterCommit()` inside transactions
- Queue notifications and mailables with `ShouldQueue`
- On-demand notifications for non-user recipients
- `HasLocalePreference` on notifiable models
- `assertQueued()` not `assertSent()` for queued mailables
- Markdown mailables for transactional emails

### 13. Error Handling → `rules/error-handling.md`

- `report()`/`render()` on exception classes or in `bootstrap/app.php` — follow existing pattern
- `ShouldntReport` for exceptions that should never log
- Throttle high-volume exceptions to protect log sinks
- `dontReportDuplicates()` for multi-catch scenarios
- Force JSON rendering for API routes
- Structured context via `context()` on exception classes

### 14. Task Scheduling → `rules/scheduling.md`

- `withoutOverlapping()` on variable-duration tasks
- `onOneServer()` on multi-server deployments
- `runInBackground()` for concurrent long tasks
- `environments()` to restrict to appropriate environments
- `takeUntilTimeout()` for time-bounded processing
- Schedule groups for shared configuration

### 15. Architecture → `rules/architecture.md`

- Single-purpose Action classes; dependency injection over `app()` helper
- Prefer official Laravel packages and follow conventions, don't override defaults
- Default to `ORDER BY id DESC` or `created_at DESC`; `mb_*` for UTF-8 safety
- `defer()` for post-response work; `Context` for request-scoped data; `Concurrency::run()` for parallel execution

### 16. Migrations → `rules/migrations.md`

- Generate migrations with `php artisan make:migration`
- `constrained()` for foreign keys
- Never modify migrations that have run in production
- Add indexes in the migration, not as an afterthought
- Mirror column defaults in model `$attributes`
- Reversible `down()` by default; forward-fix migrations for intentionally irreversible changes
- One concern per migration — never mix DDL and DML

### 17. Collections → `rules/collections.md`

- Higher-order messages for simple collection operations
- `cursor()` vs. `lazy()` — choose based on relationship needs
- `lazyById()` when updating records while iterating
- `toQuery()` for bulk operations on collections

### 18. Blade & Views → `rules/blade-views.md`

- `$attributes->merge()` in component templates
- Blade components over `@include`; `@pushOnce` for per-component scripts
- View Composers for shared view data
- `@aware` for deeply nested component props

### 19. Conventions & Style → `rules/style.md`

- Follow Laravel naming conventions for all entities
- Prefer Laravel helpers (`Str`, `Arr`, `Number`, `Uri`, `Str::of()`, `$request->string()`) over raw PHP functions
- No JS/CSS in Blade, no HTML in PHP classes
- Code should be readable; comments only for config files

## How to Apply

Always use a sub-agent to read rule files and explore this skill's content.

1. Identify the file type and select relevant sections (e.g., migration → §16, controller → §1, §3, §5, §6, §10)
2. Check sibling files for existing patterns — follow those first per Consistency First
3. Verify API syntax with `search-docs` for the installed Laravel version

## Expanded Rule Details


### advanced-queries

# Advanced Query Patterns

## Use `addSelect()` Subqueries for Single Values from Has-Many

Instead of eager-loading an entire has-many relationship for a single value (like the latest timestamp), use a correlated subquery via `addSelect()`. This pulls the value directly in the main SQL query — zero extra queries.

```php
public function scopeWithLastLoginAt($query): void
{
    $query->addSelect([
        'last_login_at' => Login::select('created_at')
            ->whereColumn('user_id', 'users.id')
            ->latest()
            ->take(1),
    ])->withCasts(['last_login_at' => 'datetime']);
}
```

## Create Dynamic Relationships via Subquery FK

Extend the `addSelect()` pattern to fetch a foreign key via subquery, then define a `belongsTo` relationship on that virtual attribute. This provides a fully-hydrated related model without loading the entire collection.

```php
public function lastLogin(): BelongsTo
{
    return $this->belongsTo(Login::class);
}

public function scopeWithLastLogin($query): void
{
    $query->addSelect([
        'last_login_id' => Login::select('id')
            ->whereColumn('user_id', 'users.id')
            ->latest()
            ->take(1),
    ])->with('lastLogin');
}
```

## Use Conditional Aggregates Instead of Multiple Count Queries

Replace N separate `count()` queries with a single query using `CASE WHEN` inside `selectRaw()`. Use `toBase()` to skip model hydration when you only need scalar values.

```php
$statuses = Feature::toBase()
    ->selectRaw("count(case when status = 'Requested' then 1 end) as requested")
    ->selectRaw("count(case when status = 'Planned' then 1 end) as planned")
    ->selectRaw("count(case when status = 'Completed' then 1 end) as completed")
    ->first();
```

## Use `setRelation()` to Prevent Circular N+1

When a parent model is eager-loaded with its children, and the view also needs `$child->parent`, use `setRelation()` to inject the already-loaded parent rather than letting Eloquent fire N additional queries.

```php
$feature->load('comments.user');
$feature->comments->each->setRelation('feature', $feature);
```

## Prefer `whereIn` + Subquery Over `whereHas`

`whereHas()` emits a correlated `EXISTS` subquery that re-executes per row. Using `whereIn()` with a `select('id')` subquery lets the database use an index lookup instead, without loading data into PHP memory.

Incorrect (correlated EXISTS re-executes per row):

```php
$query->whereHas('company', fn ($q) => $q->where('name', 'like', $term));
```

Correct (index-friendly subquery, no PHP memory overhead):

```php
$query->whereIn('company_id', Company::where('name', 'like', $term)->select('id'));
```

## Sometimes Two Simple Queries Beat One Complex Query

Running a small, targeted secondary query and passing its results via `whereIn` is often faster than a single complex correlated subquery or join. The additional round-trip is worthwhile when the secondary query is highly selective and uses its own index.

## Use Compound Indexes Matching `orderBy` Column Order

When ordering by multiple columns, create a single compound index in the same column order as the `ORDER BY` clause. Individual single-column indexes cannot combine for multi-column sorts — the database will filesort without a compound index.

```php
// Migration
$table->index(['last_name', 'first_name']);

// Query — column order must match the index
User::query()->orderBy('last_name')->orderBy('first_name')->paginate();
```

## Use Correlated Subqueries for Has-Many Ordering

When sorting by a value from a has-many relationship, avoid joins (they duplicate rows). Use a correlated subquery inside `orderBy()` instead, paired with an `addSelect` scope for eager loading.

```php
public function scopeOrderByLastLogin($query): void
{
    $query->orderByDesc(Login::select('created_at')
        ->whereColumn('user_id', 'users.id')
        ->latest()
        ->take(1)
    );
}
```

### architecture

# Architecture Best Practices

## Single-Purpose Action Classes

Extract discrete business operations into invokable Action classes.

```php
class CreateOrderAction
{
    public function __construct(private InventoryService $inventory) {}

    public function execute(array $data): Order
    {
        $order = Order::create($data);
        $this->inventory->reserve($order);

        return $order;
    }
}
```

## Use Dependency Injection

Always use constructor injection. Avoid `app()` or `resolve()` inside classes.

Incorrect:
```php
class OrderController extends Controller
{
    public function store(StoreOrderRequest $request)
    {
        $service = app(OrderService::class);

        return $service->create($request->validated());
    }
}
```

Correct:
```php
class OrderController extends Controller
{
    public function __construct(private OrderService $service) {}

    public function store(StoreOrderRequest $request)
    {
        return $this->service->create($request->validated());
    }
}
```

## Code to Interfaces

Depend on contracts at system boundaries (payment gateways, notification channels, external APIs) for testability and swappability.

Incorrect (concrete dependency):
```php
class OrderService
{
    public function __construct(private StripeGateway $gateway) {}
}
```

Correct (interface dependency):
```php
interface PaymentGateway
{
    public function charge(int $amount, string $customerId): PaymentResult;
}

class OrderService
{
    public function __construct(private PaymentGateway $gateway) {}
}
```

Bind in a service provider:

```php
$this->app->bind(PaymentGateway::class, StripeGateway::class);
```

## Default Sort by Descending

When no explicit order is specified, sort by `id` or `created_at` descending. Without an explicit `ORDER BY`, row order is undefined.

Incorrect:
```php
$posts = Post::paginate();
```

Correct:
```php
$posts = Post::latest()->paginate();
```

## Use Atomic Locks for Race Conditions

Prevent race conditions with `Cache::lock()` or `lockForUpdate()`.

```php
Cache::lock('order-processing-'.$order->id, 10)->block(5, function () use ($order) {
    $order->process();
});

// Or at query level
$product = Product::where('id', $id)->lockForUpdate()->first();
```

## Use `mb_*` String Functions

When no Laravel helper exists, prefer `mb_strlen`, `mb_strtolower`, etc. for UTF-8 safety. Standard PHP string functions count bytes, not characters.

Incorrect:
```php
strlen('José');          // 5 (bytes, not characters)
strtolower('MÜNCHEN');  // 'mÜnchen' — fails on multibyte
```

Correct:
```php
mb_strlen('José');             // 4 (characters)
mb_strtolower('MÜNCHEN');     // 'münchen'

// Prefer Laravel's Str helpers when available
Str::length('José');          // 4
Str::lower('MÜNCHEN');        // 'münchen'
```

## Use `defer()` for Post-Response Work

For lightweight tasks that don't need to survive a crash (logging, analytics, cleanup), use `defer()` instead of dispatching a job. The callback runs after the HTTP response is sent — no queue overhead.

Incorrect (job overhead for trivial work):
```php
dispatch(new LogPageView($page));
```

Correct (runs after response, same process):
```php
defer(fn () => PageView::create(['page_id' => $page->id, 'user_id' => auth()->id()]));
```

Use jobs when the work must survive process crashes or needs retry logic. Use `defer()` for fire-and-forget work.

## Use `Context` for Request-Scoped Data

The `Context` facade passes data through the entire request lifecycle — middleware, controllers, jobs, logs — without passing arguments manually.

```php
// In middleware
Context::add('tenant_id', $request->header('X-Tenant-ID'));

// Anywhere later — controllers, jobs, log context
$tenantId = Context::get('tenant_id');
```

Context data automatically propagates to queued jobs and is included in log entries. Use `Context::addHidden()` for sensitive data that should be available in queued jobs but excluded from log context. If data must not leave the current process, do not store it in `Context`.

## Use `Concurrency::run()` for Parallel Execution

Run independent operations in parallel using child processes — no async libraries needed.

```php
use Illuminate\Support\Facades\Concurrency;

[$users, $orders] = Concurrency::run([
    fn () => User::count(),
    fn () => Order::where('status', 'pending')->count(),
]);
```

Each closure runs in a separate process with full Laravel access. Use for independent database queries, API calls, or computations that would otherwise run sequentially.

## Convention Over Configuration

Follow Laravel conventions. Don't override defaults unnecessarily.

Incorrect:
```php
class Customer extends Model
{
    protected $table = 'Customer';
    protected $primaryKey = 'customer_id';

    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class, 'role_customer', 'customer_id', 'role_id');
    }
}
```

Correct:
```php
class Customer extends Model
{
    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class);
    }
}
```

### blade-views

# Blade & Views Best Practices

## Use `$attributes->merge()` in Component Templates

Hardcoding classes prevents consumers from adding their own. `merge()` combines class attributes cleanly.

```blade
<div {{ $attributes->merge(['class' => 'alert alert-'.$type]) }}>
    {{ $message }}
</div>
```

## Use `@pushOnce` for Per-Component Scripts

If a component renders inside a `@foreach`, `@push` inserts the script N times. `@pushOnce` guarantees it's included exactly once.

## Prefer Blade Components Over `@include`

`@include` shares all parent variables implicitly (hidden coupling). Components have explicit props, attribute bags, and slots.

## Use View Composers for Shared View Data

If every controller rendering a sidebar must pass `$categories`, that's duplicated code. A View Composer centralizes it.

## Use Blade Fragments for Partial Re-Renders (htmx/Turbo)

A single view can return either the full page or just a fragment, keeping routing clean.

```php
return view('dashboard', compact('users'))
    ->fragmentIf($request->hasHeader('HX-Request'), 'user-list');
```

## Use `@aware` for Deeply Nested Component Props

Avoids re-passing parent props through every level of nested components.

### caching

# Caching Best Practices

## Use `Cache::remember()` Instead of Manual Get/Put

Cleaner cache-aside pattern that removes boilerplate. use `Cache::lock()` for race conditions.

Incorrect:
```php
$val = Cache::get('stats');
if (! $val) {
    $val = $this->computeStats();
    Cache::put('stats', $val, 60);
}
```

Correct:
```php
$val = Cache::remember('stats', 60, fn () => $this->computeStats());
```

## Use `Cache::flexible()` for Stale-While-Revalidate

On high-traffic keys, one user always gets a slow response when the cache expires. `flexible()` serves slightly stale data while refreshing in the background.

Incorrect: `Cache::remember('users', 300, fn () => User::all());`

Correct: `Cache::flexible('users', [300, 600], fn () => User::all());` — fresh for 5 min, stale-but-served up to 10 min, refreshes via deferred function.

## Use `Cache::memo()` to Avoid Redundant Hits Within a Request

If the same cache key is read multiple times per request (e.g., a service called from multiple places), `memo()` stores the resolved value in memory.

`Cache::memo()->get('settings');` — 5 calls = 1 Redis round-trip instead of 5.

## Use Cache Tags to Invalidate Related Groups

Without tags, invalidating a group of entries requires tracking every key. Tags let you flush atomically. Only works with `redis`, `memcached`, `dynamodb` — not `file` or `database`.

```php
Cache::tags(['user-1'])->flush();
```

## Use `Cache::add()` for Atomic Conditional Writes

`add()` only writes if the key does not exist — atomic, no race condition between checking and writing.

Incorrect: `if (! Cache::has('lock')) { Cache::put('lock', true, 10); }`

Correct: `Cache::add('lock', true, 10);`

## Use `once()` for Per-Request Memoization

`once()` memoizes a function's return value for the lifetime of the object (or request for closures). Unlike `Cache::memo()`, it doesn't hit the cache store at all — pure in-memory.

```php
public function roles(): Collection
{
    return once(fn () => $this->loadRoles());
}
```

Multiple calls return the cached result without re-executing. Use `once()` for expensive computations called multiple times per request. Use `Cache::memo()` when you also want cross-request caching.

## Configure Failover Cache Stores in Production

If Redis goes down, the app falls back to a secondary store automatically.

```php
'failover' => ['driver' => 'failover', 'stores' => ['redis', 'database']],
```

### collections

# Collection Best Practices

## Use Higher-Order Messages for Simple Operations

Incorrect:
```php
$users->each(function (User $user) {
    $user->markAsVip();
});
```

Correct: `$users->each->markAsVip();`

Works with `each`, `map`, `sum`, `filter`, `reject`, `contains`, etc.

## Choose `cursor()` vs. `lazy()` Correctly

- `cursor()` — one model in memory, but cannot eager-load relationships (N+1 risk).
- `lazy()` — chunked pagination returning a flat LazyCollection, supports eager loading.

Incorrect: `User::with('roles')->cursor()` — eager loading silently ignored.

Correct: `User::with('roles')->lazy()` for relationship access; `User::cursor()` for attribute-only work.

## Use `lazyById()` When Updating Records While Iterating

`lazy()` uses offset pagination — updating records during iteration can skip or double-process. `lazyById()` uses `id > last_id`, safe against mutation.

## Use `toQuery()` for Bulk Operations on Collections

Avoids manual `whereIn` construction.

Incorrect: `User::whereIn('id', $users->pluck('id'))->update([...]);`

Correct: `$users->toQuery()->update([...]);`

## Use `#[CollectedBy]` for Custom Collection Classes

More declarative than overriding `newCollection()`.

```php
#[CollectedBy(UserCollection::class)]
class User extends Model {}
```

### config

# Configuration Best Practices

## `env()` Only in Config Files

Direct `env()` calls may return `null` when config is cached.

Incorrect:
```php
$key = env('API_KEY');
```

Correct:
```php
// config/services.php
'key' => env('API_KEY'),

// Application code
$key = config('services.key');
```

## Use Encrypted Env or External Secrets

Never store production secrets in plain `.env` files in version control.

Incorrect:
```bash

# .env committed to repo or shared in Slack

STRIPE_SECRET=sk_live_abc123
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI
```

Correct:
```bash
php artisan env:encrypt --env=production --readable
php artisan env:decrypt --env=production
```

For cloud deployments, prefer the platform's native secret store (AWS Secrets Manager, Vault, etc.) and inject at runtime.

## Use `App::environment()` for Environment Checks

Incorrect:
```php
if (env('APP_ENV') === 'production') {
```

Correct:
```php
if (app()->isProduction()) {
// or
if (App::environment('production')) {
```

## Use Constants and Language Files

Use class constants instead of hardcoded magic strings for model states, types, and statuses.

```php
// Incorrect
return $this->type === 'normal';

// Correct
return $this->type === self::TYPE_NORMAL;
```

If the application already uses language files for localization, use `__()` for user-facing strings too. Do not introduce language files purely for English-only apps — simple string literals are fine there.

```php
// Only when lang files already exist in the project
return back()->with('message', __('app.article_added'));
```

### db-performance

# Database Performance Best Practices

## Always Eager Load Relationships

Lazy loading causes N+1 query problems — one query per loop iteration. Always use `with()` to load relationships upfront.

Incorrect (N+1 — executes 1 + N queries):
```php
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name;
}
```

Correct (2 queries total):
```php
$posts = Post::with('author')->get();
foreach ($posts as $post) {
    echo $post->author->name;
}
```

Constrain eager loads to select only needed columns (always include the foreign key):

```php
$users = User::with(['posts' => function ($query) {
    $query->select('id', 'user_id', 'title')
          ->where('published', true)
          ->latest()
          ->limit(10);
}])->get();
```

## Prevent Lazy Loading in Development

Enable this in `AppServiceProvider::boot()` to catch N+1 issues during development.

```php
public function boot(): void
{
    Model::preventLazyLoading(! app()->isProduction());
}
```

Throws `LazyLoadingViolationException` when a relationship is accessed without being eager-loaded.

## Select Only Needed Columns

Avoid `SELECT *` — especially when tables have large text or JSON columns.

Incorrect:
```php
$posts = Post::with('author')->get();
```

Correct:
```php
$posts = Post::select('id', 'title', 'user_id', 'created_at')
    ->with(['author:id,name,avatar'])
    ->get();
```

When selecting columns on eager-loaded relationships, always include the foreign key column or the relationship won't match.

## Chunk Large Datasets

Never load thousands of records at once. Use chunking for batch processing.

Incorrect:
```php
$users = User::all();
foreach ($users as $user) {
    $user->notify(new WeeklyDigest);
}
```

Correct:
```php
User::where('subscribed', true)->chunk(200, function ($users) {
    foreach ($users as $user) {
        $user->notify(new WeeklyDigest);
    }
});
```

Use `chunkById()` when modifying records during iteration — standard `chunk()` uses OFFSET which shifts when rows change:

```php
User::where('active', false)->chunkById(200, function ($users) {
    $users->each->delete();
});
```

## Add Database Indexes

Index columns that appear in `WHERE`, `ORDER BY`, `JOIN`, and `GROUP BY` clauses.

Incorrect:
```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status');
    $table->timestamps();
});
```

Correct:
```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->index()->constrained();
    $table->string('status')->index();
    $table->timestamps();
    $table->index(['status', 'created_at']);
});
```

Add composite indexes for common query patterns (e.g., `WHERE status = ? ORDER BY created_at`).

## Use `withCount()` for Counting Relations

Never load entire collections just to count them.

Incorrect:
```php
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->comments->count();
}
```

Correct:
```php
$posts = Post::withCount('comments')->get();
foreach ($posts as $post) {
    echo $post->comments_count;
}
```

Conditional counting:

```php
$posts = Post::withCount([
    'comments',
    'comments as approved_comments_count' => function ($query) {
        $query->where('approved', true);
    },
])->get();
```

## Use `cursor()` for Memory-Efficient Iteration

For read-only iteration over large result sets, `cursor()` loads one record at a time via a PHP generator.

Incorrect:
```php
$users = User::where('active', true)->get();
```

Correct:
```php
foreach (User::where('active', true)->cursor() as $user) {
    ProcessUser::dispatch($user->id);
}
```

Use `cursor()` for read-only iteration. Use `chunk()` / `chunkById()` when modifying records.

## No Queries in Blade Templates

Never execute queries in Blade templates. Pass data from controllers.

Incorrect:
```blade
@foreach (User::all() as $user)
    {{ $user->profile->name }}
@endforeach
```

Correct:
```php
// Controller
$users = User::with('profile')->get();
return view('users.index', compact('users'));
```

```blade
@foreach ($users as $user)
    {{ $user->profile->name }}
@endforeach
```

### eloquent

# Eloquent Best Practices

## Use Correct Relationship Types

Use `hasMany`, `belongsTo`, `morphMany`, etc. with proper return type hints.

```php
public function comments(): HasMany
{
    return $this->hasMany(Comment::class);
}

public function author(): BelongsTo
{
    return $this->belongsTo(User::class, 'user_id');
}
```

## Use Local Scopes for Reusable Queries

Extract reusable query constraints into local scopes to avoid duplication.

Incorrect:
```php
$active = User::where('verified', true)->whereNotNull('activated_at')->get();
$articles = Article::whereHas('user', function ($q) {
    $q->where('verified', true)->whereNotNull('activated_at');
})->get();
```

Correct:
```php
public function scopeActive(Builder $query): Builder
{
    return $query->where('verified', true)->whereNotNull('activated_at');
}

// Usage
$active = User::active()->get();
$articles = Article::whereHas('user', fn ($q) => $q->active())->get();
```

## Apply Global Scopes Sparingly

Global scopes silently modify every query on the model, making debugging difficult. Prefer local scopes and reserve global scopes for truly universal constraints like soft deletes or multi-tenancy.

Incorrect (global scope for a conditional filter):
```php
class PublishedScope implements Scope
{
    public function apply(Builder $builder, Model $model): void
    {
        $builder->where('published', true);
    }
}
// Now admin panels, reports, and background jobs all silently skip drafts
```

Correct (local scope you opt into):
```php
public function scopePublished(Builder $query): Builder
{
    return $query->where('published', true);
}

Post::published()->paginate(); // Explicit
Post::paginate(); // Admin sees all
```

## Define Attribute Casts

Use the `casts()` method (or `$casts` property following project convention) for automatic type conversion.

```php
protected function casts(): array
{
    return [
        'is_active' => 'boolean',
        'metadata' => 'array',
        'total' => 'decimal:2',
    ];
}
```

## Cast Date Columns Properly

Always cast date columns. Use Carbon instances in templates instead of formatting strings manually.

Incorrect:
```blade
{{ Carbon::createFromFormat('Y-d-m H-i', $order->ordered_at)->toDateString() }}
```

Correct:
```php
protected function casts(): array
{
    return [
        'ordered_at' => 'datetime',
    ];
}
```

```blade
{{ $order->ordered_at->toDateString() }}
{{ $order->ordered_at->format('m-d') }}
```

## Use `whereBelongsTo()` for Relationship Queries

Cleaner than manually specifying foreign keys.

Incorrect:
```php
Post::where('user_id', $user->id)->get();
```

Correct:
```php
Post::whereBelongsTo($user)->get();
Post::whereBelongsTo($user, 'author')->get();
```

## Avoid Hardcoded Table Names in Queries

Never use string literals for table names in raw queries, joins, or subqueries. Hardcoded table names make it impossible to find all places a model is used and break refactoring (e.g., renaming a table requires hunting through every raw string).

Incorrect:
```php
DB::table('users')->where('active', true)->get();

$query->join('companies', 'companies.id', '=', 'users.company_id');

DB::select('SELECT * FROM orders WHERE status = ?', ['pending']);
```

Correct — reference the model's table:
```php
DB::table((new User)->getTable())->where('active', true)->get();

// Even better — use Eloquent or the query builder instead of raw SQL
User::where('active', true)->get();
Order::where('status', 'pending')->get();
```

Prefer Eloquent queries and relationships over `DB::table()` whenever possible — they already reference the model's table. When `DB::table()` or raw joins are unavoidable, always use `(new Model)->getTable()` to keep the reference traceable.

**Exception — migrations:** In migrations, hardcoded table names via `DB::table('settings')` are acceptable and preferred. Models change over time but migrations are frozen snapshots — referencing a model that is later renamed or deleted would break the migration.

### error-handling

# Error Handling Best Practices

## Exception Reporting and Rendering

There are two valid approaches — choose one and apply it consistently across the project.

**Co-location on the exception class** — keeps behavior alongside the exception definition, easier to find:

```php
class InvalidOrderException extends Exception
{
    public function report(): void { /* custom reporting */ }

    public function render(Request $request): Response
    {
        return response()->view('errors.invalid-order', status: 422);
    }
}
```

**Centralized in `bootstrap/app.php`** — all exception handling in one place, easier to see the full picture:

```php
->withExceptions(function (Exceptions $exceptions) {
    $exceptions->report(function (InvalidOrderException $e) { /* ... */ });
    $exceptions->render(function (InvalidOrderException $e, Request $request) {
        return response()->view('errors.invalid-order', status: 422);
    });
})
```

Check the existing codebase and follow whichever pattern is already established.

## Use `ShouldntReport` for Exceptions That Should Never Log

More discoverable than listing classes in `dontReport()`.

```php
class PodcastProcessingException extends Exception implements ShouldntReport {}
```

## Throttle High-Volume Exceptions

A single failing integration can flood error tracking. Use `throttle()` to rate-limit per exception type.

## Enable `dontReportDuplicates()`

Prevents the same exception instance from being logged multiple times when `report($e)` is called in multiple catch blocks.

## Force JSON Error Rendering for API Routes

Laravel auto-detects `Accept: application/json` but API clients may not set it. Explicitly declare JSON rendering for API routes.

```php
$exceptions->shouldRenderJsonWhen(function (Request $request, Throwable $e) {
    return $request->is('api/*') || $request->expectsJson();
});
```

## Add Context to Exception Classes

Attach structured data to exceptions at the source via a `context()` method — Laravel includes it automatically in the log entry.

```php
class InvalidOrderException extends Exception
{
    public function context(): array
    {
        return ['order_id' => $this->orderId];
    }
}
```

### events-notifications

# Events & Notifications Best Practices

## Rely on Event Discovery

Laravel auto-discovers listeners by reading `handle(EventType $event)` type-hints. No manual registration needed in `AppServiceProvider`.

## Run `event:cache` in Production Deploy

Event discovery scans the filesystem per-request in dev. Cache it in production: `php artisan optimize` or `php artisan event:cache`.

## Use `ShouldDispatchAfterCommit` Inside Transactions

Without it, a queued listener may process before the DB transaction commits, reading data that doesn't exist yet.

```php
class OrderShipped implements ShouldDispatchAfterCommit {}
```

## Always Queue Notifications

Notifications often hit external APIs (email, SMS, Slack). Without `ShouldQueue`, they block the HTTP response.

```php
class InvoicePaid extends Notification implements ShouldQueue
{
    use Queueable;
}
```

## Use `afterCommit()` on Notifications in Transactions

Same race condition as events — call `afterCommit()` to delay dispatch until the transaction commits.

```php
$user->notify((new InvoicePaid($invoice))->afterCommit());
```

## Route Notification Channels to Dedicated Queues

Mail and database notifications have different priorities. Use `viaQueues()` to route them to separate queues.

## Use On-Demand Notifications for Non-User Recipients

Avoid creating dummy models to send notifications to arbitrary addresses.

```php
Notification::route('mail', 'admin@example.com')->notify(new SystemAlert());
```

## Implement `HasLocalePreference` on Notifiable Models

Laravel automatically uses the user's preferred locale for all notifications and mailables — no per-call `locale()` needed.

### http-client

# HTTP Client Best Practices

## Always Set Explicit Timeouts

The default timeout is 30 seconds — too long for most API calls. Always set explicit `timeout` and `connectTimeout` to fail fast.

Incorrect:
```php
$response = Http::get('https://api.example.com/users');
```

Correct:
```php
$response = Http::timeout(5)
    ->connectTimeout(3)
    ->get('https://api.example.com/users');
```

For service-specific clients, define timeouts in a macro:

```php
Http::macro('github', function () {
    return Http::baseUrl('https://api.github.com')
        ->timeout(10)
        ->connectTimeout(3)
        ->withToken(config('services.github.token'));
});

$response = Http::github()->get('/repos/laravel/framework');
```

## Use Retry with Backoff for External APIs

External APIs have transient failures. Use `retry()` with increasing delays.

Incorrect:
```php
$response = Http::post('https://api.stripe.com/v1/charges', $data);

if ($response->failed()) {
    throw new PaymentFailedException('Charge failed');
}
```

Correct:
```php
$response = Http::retry([100, 500, 1000])
    ->timeout(10)
    ->post('https://api.stripe.com/v1/charges', $data);
```

Only retry on specific errors:

```php
$response = Http::retry(3, 100, function (Throwable $exception, PendingRequest $request) {
    return $exception instanceof ConnectionException
        || ($exception instanceof RequestException && $exception->response->serverError());
})->post('https://api.example.com/data');
```

## Handle Errors Explicitly

The HTTP Client does not throw on 4xx/5xx by default. Always check status or use `throw()`.

Incorrect:
```php
$response = Http::get('https://api.example.com/users/1');
$user = $response->json(); // Could be an error body
```

Correct:
```php
$response = Http::timeout(5)
    ->get('https://api.example.com/users/1')
    ->throw();

$user = $response->json();
```

For graceful degradation:

```php
$response = Http::get('https://api.example.com/users/1');

if ($response->successful()) {
    return $response->json();
}

if ($response->notFound()) {
    return null;
}

$response->throw();
```

## Use Request Pooling for Concurrent Requests

When making multiple independent API calls, use `Http::pool()` instead of sequential calls.

Incorrect:
```php
$users = Http::get('https://api.example.com/users')->json();
$posts = Http::get('https://api.example.com/posts')->json();
$comments = Http::get('https://api.example.com/comments')->json();
```

Correct:
```php
use Illuminate\Http\Client\Pool;

$responses = Http::pool(fn (Pool $pool) => [
    $pool->as('users')->get('https://api.example.com/users'),
    $pool->as('posts')->get('https://api.example.com/posts'),
    $pool->as('comments')->get('https://api.example.com/comments'),
]);

$users = $responses['users']->json();
$posts = $responses['posts']->json();
```

## Fake HTTP Calls in Tests

Never make real HTTP requests in tests. Use `Http::fake()` and `preventStrayRequests()`.

Incorrect:
```php
it('syncs user from API', function () {
    $service = new UserSyncService;
    $service->sync(1); // Hits the real API
});
```

Correct:
```php
it('syncs user from API', function () {
    Http::preventStrayRequests();

    Http::fake([
        'api.example.com/users/1' => Http::response([
            'name' => 'John Doe',
            'email' => 'john@example.com',
        ]),
    ]);

    $service = new UserSyncService;
    $service->sync(1);

    Http::assertSent(function (Request $request) {
        return $request->url() === 'https://api.example.com/users/1';
    });
});
```

Test failure scenarios too:

```php
Http::fake([
    'api.example.com/*' => Http::failedConnection(),
]);
```

### mail

# Mail Best Practices

## Implement `ShouldQueue` on the Mailable Class

Makes queueing the default regardless of how the mailable is dispatched. No need to remember `Mail::queue()` at every call site — `Mail::send()` also queues it.

## Use `afterCommit()` on Mailables Inside Transactions

A queued mailable dispatched inside a transaction may process before the commit. Use `$this->afterCommit()` in the constructor.

## Use `assertQueued()` Not `assertSent()` for Queued Mailables

`Mail::assertSent()` only catches synchronous mail. Queued mailables fail `assertSent` with a "Did you mean to use assertQueued()?" hint.

Incorrect: `Mail::assertSent(OrderShipped::class);` when mailable implements `ShouldQueue`.

Correct: `Mail::assertQueued(OrderShipped::class);`

## Use Markdown Mailables for Transactional Emails

Markdown mailables auto-generate both HTML and plain-text versions, use responsive components, and allow global style customization. Generate with `--markdown` flag.

## Separate Content Tests from Sending Tests

Content tests: instantiate the mailable directly, call `assertSeeInHtml()`.
Sending tests: use `Mail::fake()` and `assertSent()`/`assertQueued()`.
Don't mix them — it conflates concerns and makes tests brittle.

### migrations

# Migration Best Practices

## Generate Migrations with Artisan

Always use `php artisan make:migration` for consistent naming and timestamps.

Incorrect (manually created file):
```php
// database/migrations/posts_migration.php  ← wrong naming, no timestamp
```

Correct (Artisan-generated):
```bash
php artisan make:migration create_posts_table
php artisan make:migration add_slug_to_posts_table
```

## Use `constrained()` for Foreign Keys

Automatic naming and referential integrity.

```php
$table->foreignId('user_id')->constrained()->cascadeOnDelete();

// Non-standard names
$table->foreignId('author_id')->constrained('users');
```

## Never Modify Deployed Migrations

Once a migration has run in production, treat it as immutable. Create a new migration to change the table.

Incorrect (editing a deployed migration):
```php
// 2024_01_01_create_posts_table.php — already in production
$table->string('slug')->unique(); // ← added after deployment
```

Correct (new migration to alter):
```php
// 2024_03_15_add_slug_to_posts_table.php
Schema::table('posts', function (Blueprint $table) {
    $table->string('slug')->unique()->after('title');
});
```

## Add Indexes in the Migration

Add indexes when creating the table, not as an afterthought. Columns used in `WHERE`, `ORDER BY`, and `JOIN` clauses need indexes.

Incorrect:
```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status');
    $table->timestamps();
});
```

Correct:
```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->index();
    $table->string('status')->index();
    $table->timestamp('shipped_at')->nullable()->index();
    $table->timestamps();
});
```

## Mirror Defaults in Model `$attributes`

When a column has a database default, mirror it in the model so new instances have correct values before saving.

```php
// Migration
$table->string('status')->default('pending');

// Model
protected $attributes = [
    'status' => 'pending',
];
```

## Write Reversible `down()` Methods by Default

Implement `down()` for schema changes that can be safely reversed so `migrate:rollback` works in CI and failed deployments.

```php
public function down(): void
{
    Schema::table('posts', function (Blueprint $table) {
        $table->dropColumn('slug');
    });
}
```

For intentionally irreversible migrations (e.g., destructive data backfills), leave a clear comment and require a forward fix migration instead of pretending rollback is supported.

## Keep Migrations Focused

One concern per migration. Never mix DDL (schema changes) and DML (data manipulation).

Incorrect (partial failure creates unrecoverable state):
```php
public function up(): void
{
    Schema::create('settings', function (Blueprint $table) { ... });
    DB::table('settings')->insert(['key' => 'version', 'value' => '1.0']);
}
```

Correct (separate migrations):
```php
// Migration 1: create_settings_table
Schema::create('settings', function (Blueprint $table) { ... });

// Migration 2: seed_default_settings
DB::table('settings')->insert(['key' => 'version', 'value' => '1.0']);
```

### queue-jobs

# Queue & Job Best Practices

## Set `retry_after` Greater Than `timeout`

If `retry_after` is shorter than the job's `timeout`, the queue worker re-dispatches the job while it's still running, causing duplicate execution.

Incorrect (`retry_after` ≤ `timeout`):
```php
class ProcessReport implements ShouldQueue
{
    public $timeout = 120;
}

// config/queue.php — retry_after: 90 ← job retried while still running!
```

Correct (`retry_after` > `timeout`):
```php
class ProcessReport implements ShouldQueue
{
    public $timeout = 120;
}

// config/queue.php — retry_after: 180 ← safely longer than any job timeout
```

## Use Exponential Backoff

Use progressively longer delays between retries to avoid hammering failing services.

Incorrect (fixed retry interval):
```php
class SyncWithStripe implements ShouldQueue
{
    public $tries = 3;
    // Default: retries immediately, overwhelming the API
}
```

Correct (exponential backoff):
```php
class SyncWithStripe implements ShouldQueue
{
    public $tries = 3;
    public $backoff = [1, 5, 10];
}
```

## Implement `ShouldBeUnique`

Prevent duplicate job processing.

```php
class GenerateInvoice implements ShouldQueue, ShouldBeUnique
{
    public function uniqueId(): string
    {
        return $this->order->id;
    }

    public $uniqueFor = 3600;
}
```

## Always Implement `failed()`

Handle errors explicitly — don't rely on silent failure.

```php
public function failed(?Throwable $exception): void
{
    $this->podcast->update(['status' => 'failed']);
    Log::error('Processing failed', ['id' => $this->podcast->id, 'error' => $exception->getMessage()]);
}
```

## Rate Limit External API Calls in Jobs

Use `RateLimited` middleware to throttle jobs calling third-party APIs.

```php
public function middleware(): array
{
    return [new RateLimited('external-api')];
}
```

## Batch Related Jobs

Use `Bus::batch()` when jobs should succeed or fail together.

```php
Bus::batch([
    new ImportCsvChunk($chunk1),
    new ImportCsvChunk($chunk2),
])
->then(fn (Batch $batch) => Notification::send($user, new ImportComplete))
->catch(fn (Batch $batch, Throwable $e) => Log::error('Batch failed'))
->dispatch();
```

## `retryUntil()` Needs `$tries = 0`

When using time-based retry limits, set `$tries = 0` to avoid premature failure.

```php
public $tries = 0;

public function retryUntil(): \DateTimeInterface
{
    return now()->addHours(4);
}
```

## Use `ShouldBeUniqueUntilProcessing` for Early Lock Release

`ShouldBeUnique` holds the lock until the job completes. `ShouldBeUniqueUntilProcessing` releases it when processing starts, allowing new instances to queue.

```php
class UpdateSearchIndex implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    // Lock releases when processing begins, not when it finishes
}
```

## Use Horizon for Complex Queue Scenarios

Use Laravel Horizon when you need monitoring, auto-scaling, failure tracking, or multiple queues with different priorities.

```php
// config/horizon.php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'connection' => 'redis',
            'queue' => ['high', 'default', 'low'],
            'balance' => 'auto',
            'minProcesses' => 1,
            'maxProcesses' => 10,
            'tries' => 3,
        ],
    ],
],
```

### routing

# Routing & Controllers Best Practices

## Use Implicit Route Model Binding

Let Laravel resolve models automatically from route parameters.

Incorrect:
```php
public function show(int $id)
{
    $post = Post::findOrFail($id);
}
```

Correct:
```php
public function show(Post $post)
{
    return view('posts.show', ['post' => $post]);
}
```

## Use Scoped Bindings for Nested Resources

Enforce parent-child relationships automatically.

```php
Route::get('/users/{user}/posts/{post}', function (User $user, Post $post) {
    // $post is automatically scoped to $user
})->scopeBindings();
```

## Use Resource Controllers

Use `Route::resource()` or `apiResource()` for RESTful endpoints.

```php
Route::resource('posts', PostController::class);
// In routes/api.php — the /api prefix is applied automatically
Route::apiResource('posts', Api\PostController::class);
```

## Keep Controllers Thin

Aim for under 10 lines per method. Extract business logic to action or service classes.

Incorrect:
```php
public function store(Request $request)
{
    $validated = $request->validate([...]);
    if ($request->hasFile('image')) {
        $request->file('image')->move(public_path('images'));
    }
    $post = Post::create($validated);
    $post->tags()->sync($validated['tags']);
    event(new PostCreated($post));
    return redirect()->route('posts.show', $post);
}
```

Correct:
```php
public function store(StorePostRequest $request, CreatePostAction $create)
{
    $post = $create->execute($request->validated());

    return redirect()->route('posts.show', $post);
}
```

## Type-Hint Form Requests

Type-hinting Form Requests triggers automatic validation and authorization before the method executes.

Incorrect:
```php
public function store(Request $request): RedirectResponse
{
    $validated = $request->validate([
        'title' => ['required', 'max:255'],
        'body' => ['required'],
    ]);

    Post::create($validated);

    return redirect()->route('posts.index');
}
```

Correct:
```php
public function store(StorePostRequest $request): RedirectResponse
{
    Post::create($request->validated());

    return redirect()->route('posts.index');
}
```

### scheduling

# Task Scheduling Best Practices

## Use `withoutOverlapping()` on Variable-Duration Tasks

Without it, a long-running task spawns a second instance on the next tick, causing double-processing or resource exhaustion.

## Use `onOneServer()` on Multi-Server Deployments

Without it, every server runs the same task simultaneously. Requires a shared cache driver (Redis, database, Memcached).

## Use `runInBackground()` for Concurrent Long Tasks

By default, tasks at the same tick run sequentially. A slow first task delays all subsequent ones. `runInBackground()` runs them as separate processes.

## Use `environments()` to Restrict Tasks

Prevent accidental execution of production-only tasks (billing, reporting) on staging.

```php
Schedule::command('billing:charge')->monthly()->environments(['production']);
```

## Use `takeUntilTimeout()` for Time-Bounded Processing

A task running every 15 minutes that processes an unbounded cursor can overlap with the next run. Bound execution time.

## Use Schedule Groups for Shared Configuration

Avoid repeating `->onOneServer()->timezone('America/New_York')` across many tasks.

```php
Schedule::daily()
    ->onOneServer()
    ->timezone('America/New_York')
    ->group(function () {
        Schedule::command('emails:send --force');
        Schedule::command('emails:prune');
    });
```

### security

# Security Best Practices

## Mass Assignment Protection

Every model must define `$fillable` (whitelist) or `$guarded` (blacklist).

Incorrect:
```php
class User extends Model
{
    protected $guarded = []; // All fields are mass assignable
}
```

Correct:
```php
class User extends Model
{
    protected $fillable = [
        'name',
        'email',
        'password',
    ];
}
```

Never use `$guarded = []` on models that accept user input.

## Authorize Every Action

Use policies or gates in controllers. Never skip authorization.

Incorrect:
```php
public function update(UpdatePostRequest $request, Post $post)
{
    $post->update($request->validated());
}
```

Correct:
```php
public function update(UpdatePostRequest $request, Post $post)
{
    Gate::authorize('update', $post);

    $post->update($request->validated());
}
```

Or via Form Request:

```php
public function authorize(): bool
{
    return $this->user()->can('update', $this->route('post'));
}
```

## Prevent SQL Injection

Always use parameter binding. Never interpolate user input into queries.

Incorrect:
```php
DB::select("SELECT * FROM users WHERE name = '{$request->name}'");
```

Correct:
```php
User::where('name', $request->name)->get();

// Raw expressions with bindings
User::whereRaw('LOWER(name) = ?', [strtolower($request->name)])->get();
```

## Escape Output to Prevent XSS

Use `{{ }}` for HTML escaping. Only use `{!! !!}` for trusted, pre-sanitized content.

Incorrect:
```blade
{!! $user->bio !!}
```

Correct:
```blade
{{ $user->bio }}
```

## CSRF Protection

Include `@csrf` in all POST/PUT/DELETE Blade forms. In Inertia apps, the `@csrf` directive is automatically applied.

Incorrect:
```blade
<form method="POST" action="/posts">
    <input type="text" name="title">
</form>
```

Correct:
```blade
<form method="POST" action="/posts">
    @csrf
    <input type="text" name="title">
</form>
```

## Rate Limit Auth and API Routes

Apply `throttle` middleware to authentication and API routes.

```php
RateLimiter::for('login', function (Request $request) {
    return Limit::perMinute(5)->by($request->ip());
});

Route::post('/login', LoginController::class)->middleware('throttle:login');
```

## Validate File Uploads

Validate extension, MIME type, and size. The `mimes` rule checks extensions; use `mimetypes` for actual MIME type validation. Never trust client-provided filenames.

```php
public function rules(): array
{
    return [
        'avatar' => ['required', 'image', 'mimes:jpg,jpeg,png,webp', 'max:2048'],
    ];
}
```

Store with generated filenames:

```php
$path = $request->file('avatar')->store('avatars', 'public');
```

## Keep Secrets Out of Code

Never commit `.env`. Access secrets via `config()` only.

Incorrect:
```php
$key = env('API_KEY');
```

Correct:
```php
// config/services.php
'api_key' => env('API_KEY'),

// In application code
$key = config('services.api_key');
```

## Audit Dependencies

Run `composer audit` periodically to check for known vulnerabilities in dependencies. Automate this in CI to catch issues before deployment.

```bash
composer audit
```

## Encrypt Sensitive Database Fields

Use `encrypted` cast for API keys/tokens and mark the attribute as `hidden`.

Incorrect:
```php
class Integration extends Model
{
    protected function casts(): array
    {
        return [
            'api_key' => 'string',
        ];
    }
}
```

Correct:
```php
class Integration extends Model
{
    protected $hidden = ['api_key', 'api_secret'];

    protected function casts(): array
    {
        return [
            'api_key' => 'encrypted',
            'api_secret' => 'encrypted',
        ];
    }
}
```

### style

# Conventions & Style

## Follow Laravel Naming Conventions

| What | Convention | Good | Bad |
|------|-----------|------|-----|
| Controller | singular | `ArticleController` | `ArticlesController` |
| Model | singular | `User` | `Users` |
| Table | plural, snake_case | `article_comments` | `articleComments` |
| Pivot table | singular alphabetical | `article_user` | `user_article` |
| Column | snake_case, no model name | `meta_title` | `article_meta_title` |
| Foreign key | singular model + `_id` | `article_id` | `articles_id` |
| Route | plural | `articles/1` | `article/1` |
| Route name | snake_case with dots | `users.show_active` | `users.show-active` |
| Method | camelCase | `getAll` | `get_all` |
| Variable | camelCase | `$articlesWithAuthor` | `$articles_with_author` |
| Collection | descriptive, plural | `$activeUsers` | `$data` |
| Object | descriptive, singular | `$activeUser` | `$users` |
| View | kebab-case | `show-filtered.blade.php` | `showFiltered.blade.php` |
| Config | snake_case | `google_calendar.php` | `googleCalendar.php` |
| Enum | singular | `UserType` | `UserTypes` |

## Prefer Shorter Readable Syntax

| Verbose | Shorter |
|---------|---------|
| `Session::get('cart')` | `session('cart')` |
| `$request->session()->get('cart')` | `session('cart')` |
| `$request->input('name')` | `$request->name` |
| `return Redirect::back()` | `return back()` |
| `Carbon::now()` | `now()` |
| `App::make('Class')` | `app('Class')` |
| `->where('column', '=', 1)` | `->where('column', 1)` |
| `->orderBy('created_at', 'desc')` | `->latest()` |
| `->orderBy('created_at', 'asc')` | `->oldest()` |
| `->first()->name` | `->value('name')` |

## Use Laravel String & Array Helpers

Laravel provides `Str`, `Arr`, `Number`, and `Uri` helper classes that are more readable, chainable, and UTF-8 safe than raw PHP functions. Always prefer them.

Strings — use `Str` and fluent `Str::of()` over raw PHP:
```php
// Incorrect
$slug = strtolower(str_replace(' ', '-', $title));
$short = substr($text, 0, 100) . '...';
$class = substr(strrchr('App\Models\User', '\'), 1);

// Correct
$slug = Str::slug($title);
$short = Str::limit($text, 100);
$class = class_basename('App\Models\User');
```

Fluent strings — chain operations for complex transformations:
```php
// Incorrect
$result = strtolower(trim(str_replace('_', '-', $input)));

// Correct
$result = Str::of($input)->trim()->replace('_', '-')->lower();
```

Key `Str` methods to prefer: `Str::slug()`, `Str::limit()`, `Str::contains()`, `Str::before()`, `Str::after()`, `Str::between()`, `Str::camel()`, `Str::snake()`, `Str::kebab()`, `Str::headline()`, `Str::squish()`, `Str::mask()`, `Str::uuid()`, `Str::ulid()`, `Str::random()`, `Str::is()`.

Arrays — use `Arr` over raw PHP:
```php
// Incorrect
$name = isset($array['user']['name']) ? $array['user']['name'] : 'default';

// Correct
$name = Arr::get($array, 'user.name', 'default');
```

Key `Arr` methods: `Arr::get()`, `Arr::has()`, `Arr::only()`, `Arr::except()`, `Arr::first()`, `Arr::flatten()`, `Arr::pluck()`, `Arr::where()`, `Arr::wrap()`.

Numbers — use `Number` for display formatting:
```php
Number::format(1000000);          // "1,000,000"
Number::currency(1500, 'USD');    // "$1,500.00"
Number::abbreviate(1000000);      // "1M"
Number::fileSize(1024 * 1024);    // "1 MB"
Number::percentage(75.5);         // "75.5%"
```

URIs — use `Uri` for URL manipulation:
```php
$uri = Uri::of('https://example.com/search')
    ->withQuery(['q' => 'laravel', 'page' => 1]);
```

Use `$request->string('name')` to get a fluent `Stringable` directly from request input for immediate chaining.

Use `search-docs` for the full list of available methods — these helpers are extensive.

## No Inline JS/CSS in Blade

Do not put JS or CSS in Blade templates. Do not put HTML in PHP classes.

Incorrect:
```blade
let article = `{{ json_encode($article) }}`;
```

Correct:
```blade
<button class="js-fav-article" data-article='@json($article)'>{{ $article->name }}</button>
```

Pass data to JS via data attributes or use a dedicated PHP-to-JS package.

## No Unnecessary Comments

Code should be readable on its own. Use descriptive method and variable names instead of comments. The only exception is config files, where descriptive comments are expected.

Incorrect:
```php
// Check if there are any joins
if (count((array) $builder->getQuery()->joins) > 0)
```

Correct:
```php
if ($this->hasJoins())
```

### testing

# Testing Best Practices

## Use `LazilyRefreshDatabase` Over `RefreshDatabase`

`RefreshDatabase` migrates once per process and wraps each test in a rolled-back transaction. `LazilyRefreshDatabase` skips even that first migration if the schema is already up to date.

## Use Model Assertions Over Raw Database Assertions

Incorrect: `$this->assertDatabaseHas('users', ['id' => $user->id]);`

Correct: `$this->assertModelExists($user);`

More expressive, type-safe, and fails with clearer messages.

## Use Factory States and Sequences

Named states make tests self-documenting. Sequences eliminate repetitive setup.

Incorrect: `User::factory()->create(['email_verified_at' => null]);`

Correct: `User::factory()->unverified()->create();`

## Use `Exceptions::fake()` to Assert Exception Reporting

Instead of `withoutExceptionHandling()`, use `Exceptions::fake()` to assert the correct exception was reported while the request completes normally.

## Call `Event::fake()` After Factory Setup

Model factories rely on model events (e.g., `creating` to generate UUIDs). Calling `Event::fake()` before factory calls silences those events, producing broken models.

Incorrect: `Event::fake(); $user = User::factory()->create();`

Correct: `$user = User::factory()->create(); Event::fake();`

## Use `recycle()` to Share Relationship Instances Across Factories

Without `recycle()`, nested factories create separate instances of the same conceptual entity.

```php
Ticket::factory()
    ->recycle(Airline::factory()->create())
    ->create();
```

### validation

# Validation & Forms Best Practices

## Use Form Request Classes

Extract validation from controllers into dedicated Form Request classes.

Incorrect:
```php
public function store(Request $request)
{
    $request->validate([
        'title' => 'required|max:255',
        'body' => 'required',
    ]);
}
```

Correct:
```php
public function store(StorePostRequest $request)
{
    Post::create($request->validated());
}
```

## Array vs. String Notation for Rules

Array syntax is more readable and composes cleanly with `Rule::` objects. Prefer it in new code, but check existing Form Requests first and match whatever notation the project already uses.

```php
// Preferred for new code
'email' => ['required', 'email', Rule::unique('users')],

// Follow existing convention if the project uses string notation
'email' => 'required|email|unique:users',
```

## Always Use `validated()`

Get only validated data. Never use `$request->all()` for mass operations.

Incorrect:
```php
Post::create($request->all());
```

Correct:
```php
Post::create($request->validated());
```

## Use `Rule::when()` for Conditional Validation

```php
'company_name' => [
    Rule::when($this->account_type === 'business', ['required', 'string', 'max:255']),
],
```

## Use the `after()` Method for Custom Validation

Use `after()` instead of `withValidator()` for custom validation logic that depends on multiple fields.

```php
public function after(): array
{
    return [
        function (Validator $validator) {
            if ($this->quantity > Product::find($this->product_id)?->stock) {
                $validator->errors()->add('quantity', 'Not enough stock.');
            }
        },
    ];
}
```
