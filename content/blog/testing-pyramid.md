---
title: "Testing Pyramid: Unit, Integration, and Where We Mix Up"
authorIds: ["hemant"]
date: 2026-07-17
draft: false
featured: true
weight: 1
---

A class depends on another class, and that dependency gets hardwired in as a concrete type instead of something more flexible like an interface. You write tests, they pass, coverage looks reasonable. Nothing is broken.

Then a new requirement arrives that needs the first class to work with a different kind of dependency. That is when you find out the tests you already had could not actually tell you whether the first class was correct on its own. They only ever proved that the two classes happened to work together.

This happens more often than it should, and it comes from using the wrong kind of test for the job. To see exactly how it happens, and how to fix it, let's walk through a concrete case: a parking system we built.

## What we had

`ParkingLot` could park and unpark cars directly. That was the whole system.

```go
type ParkingLot struct{}

func (p *ParkingLot) Park(car Car) error {
    // park the car
    return nil
}
```

Then the question came: can the `Attendant` handle parking? So the attendant took over that responsibility. It held a reference to the `ParkingLot` and called into it to park a car.

```go
type Attendant struct {
    lot *ParkingLot
}

func (a *Attendant) Park(car Car) error {
    return a.lot.Park(car)
}
```

Then a new requirement: the attendant should support multiple strategies for finding a lot and parking on it. So the attendant took on a bit more work. It picks a strategy, the strategy locates a lot, and the lot does the actual parking.

```go
type Attendant struct {
    lot      *ParkingLot
    strategy Strategy
}

func (a *Attendant) Park(car Car) error {
    a.lot = a.strategy.FindLot()
    return a.lot.Park(car)
}
```

At each step we wrote tests. At each step they passed. The design was growing and the test suite kept up. But something was quietly off.

## Then the requirement changed

The next requirement was:

> "The attendant should work with any type of parking lot: underground, multistory, valet, or any future variant."

This requirement did not actually need to touch the attendant at all. The attendant's job was only to find a lot and hand the car to it. It never needed to know whether that lot was underground, multistory, or valet. But `ParkingLot` was hardwired into the attendant as a concrete type, so supporting a new kind of lot meant changing the attendant anyway.

The requirement itself was perfectly reasonable. What it exposed was a design problem that had been sitting there since the first iteration, and a test suite that had never caught it.

## What the tests could not do

We went back to the attendant tests expecting them to cover this. That is when the real problem surfaced. The tests were never really testing the attendant on its own. They were testing the attendant and the parking lot together, as one combined unit, and once we looked closely, that combination had been quietly hiding several problems all along.

**Failures pointed to the wrong place.** The attendant tests used a real `ParkingLot`. When a bug lived in `ParkingLot`, the attendant tests failed too. We would go look at the attendant, find nothing wrong, and waste time before realizing the bug was somewhere else entirely.

**Edge cases needed real setup.** To test what the attendant does when a lot is full, we had to fill a real `ParkingLot` by parking cars until it hit capacity. That meant the attendant test now depended on knowing the lot's capacity. Change that number, and the attendant test broke, even though the attendant itself had not changed.

**Some states could not be created at all.** How should the attendant behave when a lot goes offline, or enters maintenance? The real `ParkingLot` has no such state to begin with, so those paths inside the attendant simply could not be tested.



## What kind of test were we actually writing

The intent was to write unit tests for the attendant. What we actually wrote was something in between, part unit test and part integration test, without noticing it. The mistake was not really in the code. It was that we did not have a clear enough idea of what makes something a unit test versus an integration test, so the two got mixed together without us noticing.

<img src="/images/blog/testing-pyramid/pyramid.png" alt="Testing Pyramid" />

Tests differ by how many real components they let run, and that difference decides which question they can actually answer.

**Unit tests** replaces every dependency of the class under test with something fully controlled, a fake, a stub, a mock. Nothing real runs except the one piece of logic being tested. Because every input is controlled, you can put the system into any state you want on demand: a full lot, an offline lot, a lot that returns an error. And because nothing else is running at the same time, a failure can only mean one thing, the logic under test is wrong.

**Integration tests** lets two or more real classes run together. It answers a narrower, different question: do these pieces connect and behave correctly when combined? Because a real dependency is involved, you are limited to whatever states that dependency can actually get into. A full lot has to be filled for real. An offline lot might not be reachable at all. And when it fails, the failure could be coming from either side.

**End to End tests** runs the whole system the way a user would touch it. It gives the highest confidence that the real thing works, at the cost of being the slowest to run and the hardest to debug, since a failure could be coming from anywhere in the chain.

Combined together, they form a pyramid. That shape is not just a rule of thumb about proportions, it follows directly from what each layer can and cannot do. Unit tests are cheap and precise, so you want as much logic covered there as possible: many of them, at the base. Integration tests are more expensive and answer a coarser question, so you only need enough to confirm the seams actually connect: fewer of them, in the middle. End to end tests are the most expensive and the least specific about why something failed, so they are kept for the paths that matter most to a user: fewest, at the top.

Put as questions, each layer is asking something different:

- Unit: is this piece of logic correct, given inputs I control?
- Integration: do these real classes work together correctly?
- End to end: does the system, as a whole, do what the user needs?

The attendant test we had did not cleanly answer any one of these. It exercised a real `ParkingLot` to test the `Attendant`'s logic, so it was answering the integration question while we believed we were asking the unit question. That mismatch is exactly why the four problems above, wrong failures, hard to reach edge cases, untestable states, and invisible decisions, stayed hidden until a new requirement forced us to look closely.

## Fixing the test by fixing the seam

The attendant test cannot become a real unit test until the attendant stops depending on a concrete type. So we ask a simpler question first: what does the attendant actually need from a lot? Not the whole `ParkingLot` struct, only the ability to park a car and get back an error if that fails. That is a small, single behavior, and it can be named as an interface.

```go
type Lot interface {
    Park(car Car) error
}

type Attendant struct {
    lot Lot
}
```

The attendant now depends on that behavior instead of a specific struct. `ParkingLot` satisfies this interface without any changes to it. Any future lot type will too. The attendant does not know, and does not need to know, what is actually behind the interface.

With that in place, the attendant's unit tests can use a version of `Lot` built purely for testing, one where we control exactly what it does and what it returns:

```go
type fakeLot struct {
    full  bool
    calls []Car
}

func (f *fakeLot) Park(car Car) error {
    f.calls = append(f.calls, car)
    if f.full {
        return errors.New("lot is full")
    }
    return nil
}
```

Now each problem from before has a direct answer.

- A bug in `ParkingLot` now fails parking lot tests, not attendant tests.
- Testing the full lot case means setting `full: true` on the fake, no real capacity involved.
- Testing error handling means returning an error from the fake, no real failure needed.
- And checking call order means inspecting `calls`.

The integration test still exists, but it lives at the right layer and tests the right question: do the real `Attendant` and real `ParkingLot` work together? That is worth one test, not the main coverage for both types.

## What each layer now gives us

With the separation in place, each kind of test does its actual job.

The attendant unit tests cover every logical path through the attendant with no dependency on any real lot. They run fast and fail for one reason: something is wrong in the attendant.

The parking lot unit tests cover the lot's own logic in isolation. Same guarantee, different scope.

The integration test covers the connection. It confirms that a real attendant working with a real lot produces the correct outcome. It does not need to cover every edge case, because those are already covered at the unit level.

When the multistory lot requirement arrives, we implement `Lot` and pass it in. No attendant code changes. No attendant tests change.

## The takeaway

This was not just about parking lots. The same pattern could show up in any codebase: a class depends on another class, that dependency gets hardwired in as a concrete type instead of an interface, and nobody notices because the tests still pass.

The fix: find the one behavior the dependent class actually needs, turn it into an interface, and let unit tests use a fake version of it. Keep one real combination as an integration test, just to prove the two sides actually connect.

The habit worth keeping is simpler than the fix. Before trusting a green test, ask what it is actually testing. If the answer involves more than one real class, it is probably not a unit test, no matter what folder it lives in. A test that passes because two things happened to work together is not the same as a test that passes because the logic underneath is correct. Learning to tell those two apart, before a requirement forces the question, is what keeps a test suite honest.
