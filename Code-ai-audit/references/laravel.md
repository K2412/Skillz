# Laravel-Specific AI-Friendliness Guidance

Laravel projects have common patterns that either help or hurt AI navigability. This guide covers what to look for and how to improve.

## Domain Module Structure

**Problem**: Flat `app/` with `Models/`, `Controllers/`, `Services/` directories couples unrelated code.

**Better**: Domain-separated modules.

```
app/
├── Billing/
│   ├── Actions/
│   ├── Data/
│   ├── Models/
│   └── Contracts/
├── Inventory/
│   ├── Actions/
│   └── Models/
└── Shared/
    └── Contracts/
```

An agent looking at billing logic can stay inside `app/Billing/` — it doesn't need to understand the whole app.

## Actions Pattern

Single-responsibility action classes are deep modules with a minimal interface:

```php
// Good: one action, one method, clear name
class ChargeCustomerAction {
    public function execute(Customer $customer, Money $amount): Charge { ... }
}
```

Flag: Service classes with 10+ public methods. Recommend splitting into actions.

## Pipelines

Laravel's `Pipeline` facade creates explicit, navigable processing chains:

```php
// Each step is findable, testable in isolation
$result = Pipeline::send($order)
    ->through([ValidateInventory::class, ApplyDiscounts::class, ChargePayment::class])
    ->thenReturn();
```

Flag: Long service methods with multiple steps. Recommend extracting to a pipeline.

## Repository Pattern

Flag: Eloquent models directly in controllers or service classes. Recommend:
- Repository interface in `Contracts/`
- Eloquent implementation in `Infrastructure/`
- Fake in-memory implementation for tests

## Event Sourcing / Domain Events

Events make side effects explicit and testable:

```php
// Side effects declared, not hidden
$order->place();
// → OrderPlaced event dispatched
// → Listeners: SendConfirmationEmail, UpdateInventory, ChargePayment
```

Flag: Service classes that call other services directly (hidden coupling). Recommend events.

## Key Laravel Files to Check

| File | What to look for |
|---|---|
| `app/Providers/AppServiceProvider.php` | Interface bindings, seam points |
| `routes/` | Number of routes; resource vs. manual routing |
| `app/Http/Controllers/` | Fat controllers (business logic in controllers) |
| `database/factories/` | Good factories = testable models |
| `tests/` | Unit vs. Feature ratio |
| `phpstan.neon` / `rector.php` | Static analysis configured? |
| `deptrac.yaml` | Layer boundary enforcement? |
