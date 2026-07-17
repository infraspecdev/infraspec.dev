---
title: "The Observer Pattern: What It Is and Why It's Actually Useful"
authorIds: ["sreyas"]
date: 2026-07-17
draft: false
featured: true
weight: 1
---

## The Problem

Imagine you're building a system where one object's state change needs to trigger reactions in several other, unrelated parts of your application. Maybe it's a YouTube channel that needs to notify every subscriber the moment a new video goes live. Maybe it's a weather station that needs to update a phone app, a website widget, and a digital billboard the instant the temperature changes. Maybe it's a stock ticker that needs to push price updates to a dozen different dashboards.

The naive solution is to hard-code the reactions directly into the object that changes:

```go
func (c *Channel) UploadVideo(v Video) {
    c.videos = append(c.videos, v)
    notifySubscriberA(v)
    notifySubscriberB(v)
    notifyAnalyticsService(v)
    // ...and so on, forever
}
```

This works until it doesn't. Every time you add a new thing that needs to know about uploads, you have to go back and modify `UploadVideo`. The channel object becomes tightly coupled to every consumer of its events, and the code turns into a maintenance headache. Worse, the channel now has to know implementation details about subscribers, dashboards, and analytics services — concerns that have nothing to do with what a channel actually does.

What we want instead is a way for the channel to say "something happened" without caring who's listening or what they do about it.

## What Is the Observer Pattern?

The Observer Pattern is a behavioral design pattern that defines a one-to-many relationship between objects: when one object (the **subject**) changes state, all its dependents (the **observers**) are notified automatically, without the subject needing to know anything about them beyond a shared interface.

It's the same idea behind pub-sub systems, event emitters, and reactive programming — just distilled into its simplest object-oriented form.

## Why It's Needed

The Observer Pattern solves a specific coupling problem: it lets you add or remove reactions to an event without touching the code that produces the event. The subject only needs to know that its observers implement a common interface. It doesn't care whether that observer sends an email, updates a UI, or writes to a log.

This gives you:

- **Loose coupling** — the subject and observers can evolve independently.
- **Open/closed compliance** — you can add new observers without modifying the subject.
- **Dynamic relationships** — observers can subscribe and unsubscribe at runtime.

## Core Components

Every implementation of the Observer Pattern, regardless of language, is built from the same pieces:

- **Subject (Observable)** — the object being watched. It maintains a list of observers and notifies them of changes.
- **Observer** — a common interface that all observers implement, exposing one or more notify methods (sometimes a single generic `Update()`, sometimes one method per event type).
- **Concrete Observers** — the actual implementations that react to notifications (e.g., an email service, a UI widget, a logging service).
- **Concrete Subject** — the real implementation of the subject, holding state and triggering notifications when that state changes.
- **Event** — the change being communicated — either passed as data to a generic method, or implied by which specific method gets called.
- **Notification Mechanism** — the logic that loops over registered observers and calls the relevant notify method whenever something noteworthy happens.

## Implementing It in Go: A Parking Lot Management System

Go doesn't have classes or inheritance, but that's exactly why the Observer Pattern feels so natural here. All you need is an interface — and a real example makes this concrete faster than an abstract one.

Consider a parking lot with three stakeholders who all care about the same underlying state change — the lot filling up or freeing a space — but who each need to react differently:

- **Owner** — wants to know both when the lot becomes full (to track demand) and when space frees up (to track turnover).
- **Cop** — only cares about the lot becoming full, so incoming vehicles can be redirected elsewhere.
- **Attendant** — only cares about space becoming available, so waiting vehicles can be guided in.

Rather than a single generic `Update()` method, this project modeled the observer contract as a `Stakeholder` interface with one notify method per event type:

```go
package parkinglot

// Stakeholder is the contract every party interested in the
// parking lot's state must satisfy.
type Stakeholder interface {
    NotifyParkingLotFull()
    NotifyParkingLotAvailable()
}
```

Any struct that implements both methods automatically qualifies as a `Stakeholder` — no explicit "implements" declaration needed, because Go's interfaces are satisfied structurally. `Owner`, `Cop`, and `Attendant` each implement it, reacting only where it matters to them:

```go
type Owner struct{}

func (o *Owner) NotifyParkingLotFull() {
    fmt.Println("Owner: lot is full, demand is high")
}

func (o *Owner) NotifyParkingLotAvailable() {
    fmt.Println("Owner: a spot opened up")
}

type Cop struct{}

func (c *Cop) NotifyParkingLotFull() {
    fmt.Println("Cop: redirecting incoming vehicles")
}

func (c *Cop) NotifyParkingLotAvailable() {
    // Cop doesn't need to act on this, but the interface requires the method.
}

type Attendant struct{}

func (a *Attendant) NotifyParkingLotFull() {
    // Attendant doesn't need to act on this, but the interface requires the method.
}

func (a *Attendant) NotifyParkingLotAvailable() {
    fmt.Println("Attendant: guiding waiting vehicles to the open spot")
}
```

The `ParkingLot` struct is the concrete subject. It holds a list of added stakeholders and calls the matching notify method whenever its occupancy crosses a threshold:

```go
type ParkingLot struct {
    stakeholders  []Stakeholder
    totalSpots    int
    occupiedSpots int
}

func (p *ParkingLot) Add(s Stakeholder) {
    p.stakeholders = append(p.stakeholders, s)
}

func (p *ParkingLot) ParkVehicle() {
    p.occupiedSpots++
    if p.occupiedSpots == p.totalSpots {
        p.notifyFull()
    }
}

func (p *ParkingLot) RemoveVehicle() {
    wasFull := p.occupiedSpots == p.totalSpots
    p.occupiedSpots--
    if wasFull {
        p.notifyAvailable()
    }
}

func (p *ParkingLot) notifyFull() {
    for _, s := range p.stakeholders {
        s.NotifyParkingLotFull()
    }
}

func (p *ParkingLot) notifyAvailable() {
    for _, s := range p.stakeholders {
        s.NotifyParkingLotAvailable()
    }
}
```

Wiring it together:

```go
lot := &ParkingLot{totalSpots: 2}
lot.Add(&Owner{})
lot.Add(&Cop{})
lot.Add(&Attendant{})

lot.ParkVehicle()
lot.ParkVehicle()   // triggers NotifyParkingLotFull on all stakeholders
lot.RemoveVehicle() // triggers NotifyParkingLotAvailable on all stakeholders
```

None of these stakeholders know about each other. The `ParkingLot` doesn't know or care that a cop or attendant exists — it just calls the matching notify method on whoever has been added. Adding a fourth stakeholder, say a mobile app showing live availability, means writing one new struct that implements `Stakeholder` and adding it. Nothing about `ParkingLot` changes.

## Advantages and Use Cases

Beyond parking lots, this pattern shows up everywhere:

- **YouTube subscriptions** — a channel notifies every subscriber when a new video is uploaded.
- **Weather stations** — a single sensor reading updates multiple displays (app, website, billboard) simultaneously.
- **Stock market feeds** — a price change gets pushed to every dashboard watching that ticker.
- **News publishing** — a new article triggers an email send, a push notification, and an analytics event, all independently.
- **Chat applications** — a new message gets broadcast to every connected client in a room.

The common thread is always the same: one change, many independent reactions, and no reason for the source of the change to know about any of them.

The main trade-off to be aware of is that notification order isn't usually guaranteed, and if a stakeholder's notify method does something slow or blocking, it can hold up the whole notification chain — something worth considering if you're calling this in a latency-sensitive path, where you might reach for goroutines and channels instead of a synchronous loop.

## Lessons Learned

The parking lot project made the value of this pattern concrete: three stakeholders, three completely different reactions, one shared source of state changes. Building it around a `Stakeholder` interface meant new stakeholders could be added without ever touching `ParkingLot` itself. In a sense, the pattern clubs all the observers together under one contract, so their behavior can be managed — subscribed, notified, swapped out — as a group, even though each one reacts differently underneath.

Go's structural interfaces make this pattern almost free — there's no boilerplate `implements` clause, no base class to inherit from. Any type with `NotifyParkingLotFull()` and `NotifyParkingLotAvailable()` methods just _is_ a `Stakeholder`.

This same interface-driven design pays off in testing. Because `ParkingLot` only depends on the `Stakeholder` interface — not on concrete `Owner`, `Cop`, or `Attendant` types — its dependencies can be supplied from the outside rather than constructed internally. That's dependency injection in practice: `Add()` accepts anything satisfying `Stakeholder`, so a test can hand it a fake stakeholder built purely to record which notify method got called, without needing a real `Owner` or `Cop` at all. Designing structs around small interfaces isn't just about decoupling — it's what makes each piece independently testable in the first place.
