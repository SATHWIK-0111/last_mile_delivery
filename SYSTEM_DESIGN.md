# System Design — Last Mile Delivery Tracker

## 1. Architecture

The system is a role-based last-mile delivery platform with Customer, Delivery Agent, and Administrator workflows. React communicates with a FastAPI REST backend through Axios. FastAPI routes handle authentication, orders, agents, and administration, while business rules are centralized in service modules. SQLAlchemy provides data access and Alembic manages migrations.

The main flow is:

```text
Customer / Agent / Admin
          |
          v
     React Frontend
          |
          v
     FastAPI REST API
          |
          v
 Business Service Layer
          |
          v
 SQLAlchemy Models
          |
          v
      Database
```

JWT bearer authentication identifies users, and role checks protect customer, agent, and administrator operations.

## 2. Rate Calculation Engine

The rate engine calculates the delivery charge before an order is created. The calculation validates `order_type` as `B2B` or `B2C`, validates `payment_type` as `PREPAID` or `COD`, and requires positive package dimensions and actual weight.

### Volumetric Weight

Package volume is converted into volumetric weight using a divisor of `5000`:

```text
Volumetric Weight (kg)
= Length (cm) × Breadth (cm) × Height (cm)
  -----------------------------------------
                    5000
```

### Billable Weight

The system compares actual weight with volumetric weight and uses the larger value:

```text
Billable Weight
= max(Actual Weight, Volumetric Weight)
```

This ensures that both heavy packages and bulky lightweight packages are priced appropriately.

### Zone Type

The pickup and drop addresses are passed through zone detection. If both addresses resolve to the same zone, the shipment is `INTRA`; otherwise it is `INTER`:

```text
Zone Type =
    INTRA  if Pickup Zone ID = Drop Zone ID
    INTER  otherwise
```

The rate card is then selected using:

```text
Rate Card = (Order Type, Zone Type)
```

For example, the system can use separate configured rate cards for `B2B/INTRA`, `B2B/INTER`, `B2C/INTRA`, and `B2C/INTER`.

### Base Charge

The configured rate card contains a weight limit, base rate, and optional additional rate.

For packages within the weight limit:

```text
Base Charge = Base Rate
```

For packages above the weight limit:

```text
Extra Weight
= Billable Weight − Weight Limit

Base Charge
= Base Rate + (Extra Weight × Additional Rate)
```

### COD Charge

For prepaid orders:

```text
COD Charge = 0
```

For COD orders, the system retrieves the configured COD charge for the order type:

```text
COD Charge = Configured COD Charge
```

### Final Charge

The final delivery charge is:

```text
Total Charge
= Base Charge + COD Charge
```

The backend returns zones, zone type, actual/volumetric/billable weight, rate-card ID, base charge, COD charge, and total.

The calculation is kept in the backend rate-engine service rather than the frontend, providing one consistent source of truth for charges.

## 3. Zone Detection

Zones are represented as database entities with associated zone-area information. The rate engine loads the configured areas once and reuses them when detecting the pickup and drop zones.

The pickup and drop addresses are passed to the zone-detection service. Their zone IDs determine intra-zone versus inter-zone pricing.

Zone information is also important for assignment: an agent is considered for automatic assignment when the agent belongs to the pickup zone and has valid current location data. This keeps assignment geographically relevant.

## 4. Auto-Assignment and Agent Availability

Automatic assignment is handled by the assignment service. For a rescheduled order requiring reassignment, the system verifies the order state and pickup coordinates. It then searches for agents in the pickup zone whose availability is `AVAILABLE` and whose current latitude and longitude are present.

The system calculates distance to each eligible agent, selects the nearest, assigns the order, changes availability to `BUSY`, and records an assignment event.

Agent availability is explicitly modelled as `AVAILABLE`, `BUSY`, or `OFFLINE`. Delivery completion or failure releases the assigned agent back to `AVAILABLE`.

## 5. Order Lifecycle and Tracking

Order status transitions are controlled by a centralized status service. The supported lifecycle is:

```text
CREATED → ASSIGNED → PICKED_UP → IN_TRANSIT
→ OUT_FOR_DELIVERY → DELIVERED
                             |
                             └→ FAILED
                                   |
                                   └→ RESCHEDULED → ASSIGNED
```

Invalid transitions are rejected by the backend. Every status change creates a tracking-history event containing the status, actor information, timestamp, and remarks. The current order status is separate from its historical event records, preserving the delivery timeline rather than overwriting it.

## 6. Failed Delivery Handling

A delivery can be marked `FAILED` only when it is `OUT_FOR_DELIVERY`. The agent must provide a failure reason. The backend updates the order status, releases the assigned agent, creates a tracking-history event, and creates a customer notification.

A failed order can subsequently be rescheduled by the customer. Rescheduling changes the order to `RESCHEDULED` and triggers automatic reassignment to an eligible nearby agent. This provides a recovery path while retaining the original failure event in tracking history.

## 7. Database and API Design

The database is modelled around users, agents, orders, assignments, zones, rate cards, COD charges, notifications, tracking history, and reschedule requests. Foreign-key relationships connect operational records, while tracking and notification records preserve historical events.

The API is organized by responsibility (`/auth`, `/orders`, `/agent`, and `/admin`) and delegates operations to reusable services, separating validation, business rules, persistence, and presentation.
