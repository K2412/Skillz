# Deep Modules

A deep module has a **simple interface** and a **complex implementation**. The complexity is hidden — callers don't need to know how it works, only what it does.

## The Depth Metric

```
depth = complexity_hidden / interface_complexity
```

A module with 2 public methods and 500 lines of logic is deep.
A module with 20 public methods and 50 lines of logic is shallow.

## Signs of a Shallow Module

- Pass-through methods: `function getUser($id) { return $this->repo->find($id); }`
- Getters/setters for every field
- Public methods that expose implementation steps ("fetchFromCache", "hydrateFromRow")
- Callers must call methods in a specific order to get correct state
- Internal data structures leak into the public API

## Signs of a Deep Module

- Single, clear entry point per capability
- Implementation can change without callers noticing
- Error handling contained internally
- Business logic not visible from method signature

## How to Deepen a Shallow Module

1. **Combine related methods** — if callers always call A then B, merge them.
2. **Hide the sequence** — if callers must follow a protocol, encode it internally.
3. **Pull error handling in** — don't make callers handle implementation errors.
4. **Move decisions down** — if every caller makes the same conditional, move it inside.

## Example: Shallow → Deep (PHP)

```php
// Shallow — caller must know implementation
class UserRepository {
    public function fetchFromDatabase(int $id): array { ... }
    public function hydrateUser(array $row): User { ... }
    public function cacheUser(User $user): void { ... }
}
// Caller: $row = $repo->fetchFromDatabase($id); $user = $repo->hydrateUser($row); $repo->cacheUser($user);

// Deep — implementation hidden
class UserRepository {
    public function find(int $id): ?User { ... }  // cache + fetch + hydrate internally
}
```

## When Not to Go Deeper

- The module is a pure data container (DTO/value object) — thin is correct
- The module is an adapter to an external API — mirror the external API shape
- Multiple callers need different subsets of behaviour — splitting is correct
