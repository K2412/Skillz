# Grey-box Testing

Grey-box tests sit at internal seams — they test behaviour through a real interface, but they know enough about the internals to choose the right boundary to test at.

## Why Grey-box Tests Matter for AI Agents

An AI agent making changes needs fast, precise feedback. End-to-end tests are too slow and too broad. Unit tests that test implementation details break on refactors. Grey-box tests hit the sweet spot:

- Fast (no HTTP, no full bootstrap)
- Precise (target the changed behaviour)
- Stable (test through the public interface of a module, not its internals)

## The Seam Concept

A **seam** is a place where you can alter behaviour without editing the code in that place. The best seams are:

- Constructor injection points (pass a fake dependency)
- Interface boundaries (swap implementations)
- Module entry points (call the public API directly)

## What Good Seam Tests Look Like

```php
// Grey-box test: tests the Order service through its public API,
// with a fake payment gateway injected at the seam
class OrderServiceTest extends TestCase {
    public function test_order_is_placed_when_payment_succeeds(): void {
        $gateway = new FakePaymentGateway(shouldSucceed: true);
        $service = new OrderService($gateway, new InMemoryOrderRepository());

        $order = $service->place(Cart::withItems([Item::create('SKU-1', 2)]));

        $this->assertTrue($order->isConfirmed());
        $this->assertCount(1, $gateway->capturedCharges());
    }
}
```

## Interface-First Testing

Design your interfaces for testability before writing implementation:

1. Define the interface/contract at the seam
2. Write the test against that interface with a fake/stub
3. Implement the real class to satisfy the interface
4. The test now covers both the fake and the real (via integration test)

## Common Seams to Look For

| Seam type | Example |
|---|---|
| External service | Payment gateway, email sender, SMS provider |
| Persistence | Repository interface (in-memory fake for tests) |
| Clock/time | `ClockInterface` injected (controllable in tests) |
| File system | `FilesystemInterface` (in-memory for tests) |
| Queue | Fake queue that collects dispatched jobs |
| Event bus | Fake event collector |

## Anti-patterns to Flag

- Tests that hit real HTTP endpoints for every assertion
- Tests that read/write real database rows without transactions or truncation
- Tests that sleep or use `time()` directly
- Tests that call `new ConcreteClass()` instead of using an interface
