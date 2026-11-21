# Patterns Library

**Purpose**: the design vocabulary for specs. Every design element in a spec's
Technical Specification is stamped with a pattern from this file, or `[NOVEL]`.
Grammar, matching and review rules: `rules/design-spec.md` → "Pattern Stamping".

**Last Updated**: 2026-10-25

**Sources** (pattern names and references only; every "Use when" and "Core mechanism" line is our own wording)

- **AZ**: microservices patterns on Microsoft Azure (61 patterns, grouped by theme), after
  Microsoft's cloud design-pattern catalog:
  https://learn.microsoft.com/en-us/azure/architecture/patterns/

- **EIP**: G. Hohpe and B. Woolf, *Enterprise Integration Patterns*, Addison-Wesley (Pearson), 2004
  (65 patterns; IDs are book page numbers). Index:
  https://www.enterpriseintegrationpatterns.com/patterns/messaging/toc.html

- **GOF**: E. Gamma, R. Helm, R. Johnson and J. Vlissides, *Design Patterns: Elements of Reusable
  Object-Oriented Software*, Addison-Wesley, 1994 (23 patterns).

- **POEAA**: M. Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley, 2002 (51
  patterns). Catalog: https://martinfowler.com/eaaCatalog/

- **DDD**: E. Evans, *Domain-Driven Design Reference*, Domain Language, 2015 (45 entries; IDs are
  its page numbers), licensed CC BY 4.0: https://www.domainlanguage.com/ddd/reference/

- **AGT**: *Agent Patterns Catalog*, https://github.com/agentpatternscatalog/patterns, CC BY 4.0
  (only patterns marked `mature`; restated in our own words, with attribution per record).

- **DDDB**: E. Evans, *Domain-Driven Design*, Addison-Wesley, 2003, ch. 9; and E. Evans and M.
  Fowler, "Specifications".

**Columns**: **ID** is a row label, not a stamp token. **Pattern** and **Aliases** are the names a
stamp may use; aliases are true synonyms only. **Use when** is the problem. **Core mechanism** is
what an element must contain to claim the pattern. **Ref / See also** is never matched.

**Maintenance**: records are append-only: an ID is never reused, a renamed record keeps its old
name as an alias, a retired record names its successor. A project may keep its own copy in
`docs/PatternsLibrary.md` and add a section for patterns promoted from its `[NOVEL]` design
elements.

**Merged across catalogs** (one row, other names as Aliases or Ref): Pipes and Filters,
Publish-Subscribe Channel, Dead Letter Channel, Messaging Bridge, Claim Check, Competing Consumers
and Idempotent Receiver (EIP, on AZ rows); Bounded Context and Anticorruption Layer (DDD, on AZ
rows); Value Object and Repository (POEAA, on DDD rows).

**Not stampable** (a scope choice: they are general building blocks or development practices, not
design decisions): EIP *Message* (p.66), *Message Channel* (p.60), *Message Endpoint* (p.95); DDD
*Continuous Integration* (p.5), *Model-Driven Design* (p.6), *Hands-on Modelers* (p.7), *Refactoring
Toward Deeper Insight* (p.8), *Drawing on Established Formalisms* (p.26), *Conceptual Contours*
(p.27), *Domain Vision Statement* (p.42), *Highlighted Core* (p.43), *Evolving Order* (p.48),
*System Metaphor* (p.49).

---

## AZ — Microservices patterns on Azure

### AZ 01 — Service boundaries & modernization

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-01 | Decompose by Business Capability | | Service or module boundaries should follow what the business does, not technical layers | One unit per business capability, owning that capability's logic and data end to end | see also Bounded Context |
| AZ-02 | Bounded Context | | A model's terms and rules hold only inside an explicit boundary owned by one team or module | An explicit boundary inside which one model and its language are consistent; translation at the edges | DDD p.2; see also Generic Subdomain, Core Domain |
| AZ-03 | Anti-Corruption Layer | Anticorruption Layer | A foreign or legacy model must be translated at the edge so it does not leak into your domain | A dedicated translating layer between your model and the other system; your code never uses the foreign types | DDD p.34; see also Message Translator, Adapter |
| AZ-04 | Strangler Fig | | A legacy system is replaced piece by piece while both run behind one entry point | A routing facade sends each capability to old or new code; capabilities move over one at a time | |
| AZ-05 | Backends for Frontends | BFF | Different client types need differently shaped APIs from the same services | A separate backend per client type, owned with that client, shaping calls to shared services | |

### AZ 02 — API access & service communication

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-06 | Gateway Routing | | Clients should call one endpoint that forwards to many services | One entry point maps request paths or attributes to backend services | often part of an "API gateway"; see also Message Router, Content-Based Router, Message Broker |
| AZ-07 | Gateway Aggregation | | One client request needs data fanned out to several services and merged | A gateway calls several backends for one request and merges their replies | related term: API Composition; see also Aggregator, Scatter-Gather |
| AZ-08 | Gateway Offloading | | Cross-cutting concerns such as TLS, auth or quotas should live once at the edge | Shared concerns are removed from services and implemented once in the gateway | |
| AZ-09 | Synchronous Request-Reply | | A caller needs the answer before it can continue and the callee is fast enough | Caller blocks on a direct call (HTTP/gRPC) bounded by a timeout | see also Request-Reply |
| AZ-10 | Asynchronous Request-Reply | | Work is too slow to wait on, so accept it now and let the caller poll or be told later | Immediate acknowledgement with a status handle; the caller polls it or receives a callback | see also Request-Reply |
| AZ-11 | Service Discovery | | Callers must find service instances whose addresses change | A registry or DNS resolves a logical service name to live instances at call time | |
| AZ-12 | Sidecar | | Helper functionality should run beside a component, isolated but sharing its lifecycle | A separate process or container deployed with each instance, sharing its host and lifecycle | |
| AZ-13 | Ambassador | | Outbound connection concerns (retries, routing, TLS) should be handled by a local proxy | A local out-of-process proxy that the app calls instead of the remote service | see also Proxy |

### AZ 03 — Data ownership & performance

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-14 | Database per Service | | Each service must own its data privately so others cannot couple to its schema | Each service has its own store; other services get data only through its API or events | see also Shared Database |
| AZ-15 | CQRS | Command Query Responsibility Segregation | Reads and writes need different models, shapes or scaling | Separate write model (commands) and read model (queries), possibly in separate stores | |
| AZ-16 | Event Sourcing | | The full history of state changes must be the record, with state derived by replay | An append-only event log is the source of truth; current state is rebuilt by replaying events | see also Domain Event |
| AZ-17 | Materialized View | | Queries need a precomputed shape of data that the source store cannot serve cheaply | A derived read store kept up to date from the source and rebuilt from it when needed | |
| AZ-18 | Transactional Outbox | Outbox | A state change and the event announcing it must commit together, then publish reliably | Event row written in the same local transaction as the change; a relay publishes it afterwards | see also Guaranteed Delivery, Transactional Client |
| AZ-19 | Change Data Capture | CDC | Other components must react to changes already committed in a database | Read the store's commit log or change feed and emit each committed change downstream | related term: Change Feed |
| AZ-20 | Sharding | | One dataset is too big or too busy for a single store and must be split by key | A shard key routes each record to one of several partitions | |
| AZ-21 | Cache-Aside | | Slow reads should be served from a cache filled on demand by the caller | On a miss the caller loads from the store and fills the cache; writes invalidate entries | |
| AZ-22 | Index Table | | Lookups by a secondary attribute need their own structure the main store lacks | A separately maintained table keyed by the secondary attribute, pointing to primary keys | |

### AZ 04 — Messaging & distributed workflows

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-23 | Publisher-Subscriber | Publish-Subscribe Channel, Pub-Sub | One event must reach every interested receiver without the sender knowing them | A topic delivers a copy of each message to every subscription | EIP p.106; see also Observer |
| AZ-24 | Choreography | | Services should react to each other's events with no central coordinator | Each service subscribes to events and emits its own; no component owns the whole flow | see also Saga |
| AZ-25 | Saga | | A business transaction spans services, so each step commits locally and failures are undone by compensation | A sequence of local transactions, each with a compensating action run in reverse on failure | see also Process Manager, Compensating Transaction |
| AZ-26 | Compensating Transaction | | Completed work cannot be rolled back, so a business action must reverse its effect | An explicit undo operation per step, recorded so it can be run after a later failure | |
| AZ-27 | Competing Consumers | | Several workers should share one queue of work to scale and survive failures | Many consumers on one queue; each message is locked to exactly one of them | EIP p.502 |
| AZ-28 | Queue-Based Load Leveling | | Bursts of requests should be buffered so a slower worker processes them at its own pace | A queue between producer and consumer absorbs bursts; the consumer pulls at a steady rate | see also Point-to-Point Channel |
| AZ-29 | Pipes and Filters | | Processing should be a chain of independent stages, each with one job, that can be reordered or reused | Each stage reads input, transforms it and passes output on; stages share no state | EIP p.70; see also Chain of Responsibility |
| AZ-30 | Claim Check | | A payload is too large to send, so store it and pass a reference instead | Store the payload, send a token, and let the receiver fetch the payload by the token | EIP p.346 |
| AZ-31 | Sequential Convoy | | Related messages must be handled in order while unrelated groups proceed in parallel | Messages carry a group key; one consumer at a time processes each group in order | see also Resequencer |
| AZ-32 | Priority Queue | | Urgent work must overtake ordinary work waiting in the same system | Separate queues or priority levels, with consumers serving higher priority first | |
| AZ-33 | Idempotent Consumer | Idempotent Receiver | A message may arrive more than once and must not repeat its business effect | Record processed message IDs atomically with the effect; skip IDs already seen | EIP p.528; an inbox table is one implementation |
| AZ-34 | Dead-Letter Queue | Dead Letter Channel, DLQ | Messages that cannot be processed must be set aside for inspection instead of blocking or vanishing | After N failed attempts, move the message to a separate queue with its failure reason | EIP p.119; see also Invalid Message Channel |
| AZ-35 | Messaging Bridge | | Two messaging systems that cannot talk directly must exchange messages | A component consumes from one system and republishes to the other, mapping channels | EIP p.133 |

### AZ 05 — Resilience & resource protection

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-36 | Retry | | A dependency fails transiently and repeating the call cannot cause harm | Re-attempt only transient errors, with a bounded count and backoff, on idempotent operations | |
| AZ-37 | Circuit Breaker | | Calls to a failing dependency should stop for a while instead of piling up | Count failures; open to fail fast; after a cool-down let trial calls through before closing | |
| AZ-38 | Bulkhead | | One workload or dependency must not be able to exhaust resources shared by others | Separate pools (threads, connections, instances) per workload so exhaustion stays contained | |
| AZ-39 | Timeout | | A call to a dependency must not be allowed to take unbounded time | Every call carries a time limit; on expiry it is abandoned and treated as a failure | related term: Deadline (propagated across hops); see also Message Expiration |
| AZ-40 | Fallback | | When a dependency fails, a reduced answer is better than an error | A defined alternative result (cached, default or partial) returned when the call fails | serves the goal of graceful degradation; see also Special Case |
| AZ-41 | Rate Limiting | | Your outgoing requests must stay within a downstream's capacity or quota | A client-side limiter (e.g. token bucket) paces calls and queues or defers the excess | |
| AZ-42 | Throttling | | Incoming load beyond an agreed level must be slowed or rejected to protect the service | Measure incoming use per client or overall; reject or degrade above a threshold | |
| AZ-43 | Leader Election | | Exactly one of several instances must coordinate shared work at a time | A lease or lock decides one leader; the others take over when the lease expires | |
| AZ-44 | Scheduler Agent Supervisor | | Distributed steps must be scheduled, carried out by agents and supervised for recovery | A scheduler records step state, agents perform steps, a supervisor detects stuck steps and recovers | see also Process Manager |

### AZ 06 — Security & configuration

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-45 | Federated Identity | | User authentication should be delegated to an external identity provider | The app trusts tokens issued by an external identity provider instead of storing credentials | |
| AZ-46 | Workload Identity | | Services must authenticate to each other without credentials stored in code or config | The platform issues the workload an identity and short-lived tokens; no stored secrets | gives secretless access; Azure term: Managed Identity |
| AZ-47 | Gatekeeper | | Requests must be validated by a separate front component before reaching protected backends | A separate front component validates and sanitises every request; backends accept only its traffic | |
| AZ-48 | Valet Key | | A client needs limited, time-bound direct access to one resource without going through your service | Issue a scoped, expiring token granting direct access to one resource | |
| AZ-49 | External Configuration Store | | Settings must change without redeploying and live outside the deployment package | Configuration is read at runtime from a store outside the deployable artifact | |
| AZ-50 | Quarantine | | External content must be validated before anything is allowed to use it | New content lands in an isolated area and is released only after it passes validation | |

### AZ 07 — Deployment, operations & scale

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AZ-51 | Health Endpoint Monitoring | Health Check | External tools must be able to verify that a component is working | An endpoint that runs checks on the component and its dependencies and reports status | see also Control Bus, Smart Proxy |
| AZ-52 | Distributed Tracing | | One request must be followed across several services | A trace ID is propagated on every hop; each hop records timed spans under it | see also Correlation Identifier, Message History |
| AZ-53 | Centralized Log Aggregation | | Logs from many instances must be searched and correlated in one place | Every instance ships structured logs to one store, tagged with correlation fields | |
| AZ-54 | Blue-Green Deployment | | A new version should be fully staged beside the old one, then traffic switched at once | Two full environments; traffic switches atomically and the old one is kept for rollback | |
| AZ-55 | Canary Deployment | Canary Release | A new version should get a small share of traffic first and grow only while healthy | Route a growing share of traffic to the new version, gated on health metrics | |
| AZ-56 | Rolling Deployment | | Instances should be replaced a few at a time while the service stays up | Replace instances in batches, waiting for readiness before each next batch | |
| AZ-57 | Feature Flags | Feature Toggles | Exposure of a feature must be controlled separately from deploying its code | A runtime switch, read per request or session, decides whether the new code path runs | |
| AZ-58 | Deployment Stamps | | Whole copies of the application should be deployed repeatably for scale or isolation | Infrastructure as code deploys identical independent copies; routing assigns users to one | |
| AZ-59 | Geode | | Users in many regions should be served by nearby full copies of the stack | Full stacks in several regions behind global routing, with replicated data | |
| AZ-60 | Compute Resource Consolidation | | Several small workloads should share compute to raise utilization | Co-locate workloads on shared hosts with per-workload resource limits | |
| AZ-61 | Static Content Hosting | | Static files should be served without involving the application servers | Static assets served from storage or a CDN; the app only returns references to them | |

## EIP — Enterprise Integration Patterns

### EIP Ch 2 — Integration styles

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-43 | File Transfer | | Applications exchange data by one writing files that another later reads | Producer writes files in an agreed format and location; consumer reads them on its schedule | |
| EIP-47 | Shared Database | | Applications must see the same data at once and can accept coupling on one schema | Several applications read and write one database schema directly | see also Database per Service |
| EIP-50 | Remote Procedure Invocation | RPC | One application must run behaviour in another and wait for the outcome | A typed remote call interface; the caller blocks for the result | |
| EIP-53 | Messaging | | Applications must exchange data often and asynchronously without tight coupling | Applications exchange packets through a messaging system that stores and forwards them | |

### EIP Ch 3 — Messaging systems

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-78 | Message Router | | A step must pick the next destination for each message without the sender deciding | A component consumes from one channel and forwards each message to one of several outputs | see also Gateway Routing |
| EIP-85 | Message Translator | | Two parties use different data formats and something between them must convert | A filter that maps one message format to another, with no other logic | see also Anti-Corruption Layer, Adapter |

### EIP Ch 4 — Messaging channels

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-103 | Point-to-Point Channel | | Each message must be handled by exactly one receiver | A channel that hands each message to only one of its consumers | see also Queue-Based Load Leveling |
| EIP-111 | Datatype Channel | | Receivers must know what kind of data arrives by which channel it came on | One channel per data type, so the channel identifies the type | |
| EIP-115 | Invalid Message Channel | | Messages a receiver cannot interpret must go somewhere visible instead of being dropped | The receiver moves messages it cannot parse or validate to a dedicated channel | see also Dead-Letter Queue |
| EIP-122 | Guaranteed Delivery | | A message must survive crashes of the messaging system until it is delivered | Messages are persisted at each hop and deleted only after the next hop acknowledges them | see also Transactional Outbox |
| EIP-127 | Channel Adapter | | An application that was not built for messaging must be connected to a channel | An adapter calls the application's own API or data and sends or receives messages for it | |
| EIP-137 | Message Bus | | Many applications must share common channels, formats and commands so any can join or leave | Shared channel infrastructure plus a shared message format and command set | |

### EIP Ch 5 — Message construction

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-145 | Command Message | | A message asks the receiver to perform a specific action | The message names an operation and its arguments for exactly one receiver to execute | see also Command |
| EIP-147 | Document Message | | A message carries data for the receiver to decide what to do with | The message is a data structure with no instruction about what to do with it | |
| EIP-151 | Event Message | | A message announces that something happened, with little or no payload required | The message records a past fact; receivers decide independently how to react | see also Domain Event |
| EIP-154 | Request-Reply | | A sender needs an answer back over messaging, on a separate reply path | A request on one channel and a reply on a separate channel back to the requester | see also Synchronous Request-Reply, Asynchronous Request-Reply |
| EIP-159 | Return Address | | The request itself must say where its reply should be sent | The request carries the reply channel; the replier sends there | |
| EIP-163 | Correlation Identifier | | A reply or follow-up must be matched to the request that caused it | The request carries a unique ID; the reply copies it so the requester can match them | see also Distributed Tracing |
| EIP-170 | Message Sequence | | Data too big for one message is sent as numbered parts and reassembled | Parts carry a sequence ID, position and total count; the receiver reassembles them | |
| EIP-176 | Message Expiration | | A message becomes useless after a time limit and must not be processed late | The message carries an expiry time; it is discarded or rerouted once that has passed | see also Timeout |
| EIP-180 | Format Indicator | | A message format will change, so each message states which version it uses | A version or format field inside the message tells receivers how to parse it | |

### EIP Ch 7 — Message routing

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-230 | Content-Based Router | | The handler for a message depends on values inside it | Inspect fields of each message and route by rules over them | see also Gateway Routing |
| EIP-237 | Message Filter | | A receiver should only get messages that meet a condition, the rest are discarded | A predicate passes matching messages on and drops the rest | |
| EIP-243 | Dynamic Router | | Routing rules change at runtime as destinations register their interests | Destinations announce their criteria on a control channel; the router updates its rules | |
| EIP-249 | Recipient List | | One message must go to a list of recipients worked out per message | Compute the recipient list for each message and send a copy to each | |
| EIP-259 | Splitter | | A message holds several items that must be handled one by one | Break one message into several, one per item, each carrying correlation data | |
| EIP-268 | Aggregator | | Several related messages must be collected and combined before moving on | A stateful component collects correlated messages until a completeness rule fires, then emits one | see also Gateway Aggregation |
| EIP-283 | Resequencer | | Related messages arrive out of order and must be put back in order | Buffer messages and release them in sequence-number order | see also Sequential Convoy |
| EIP-294 | Composed Message Processor | | A composite message is split, each part processed differently, then recombined | Splitter, then a router per part, then an aggregator | |
| EIP-297 | Scatter-Gather | | A request is sent to several parties and their replies are combined into one result | Broadcast or recipient-list the request, then aggregate the replies | see also Gateway Aggregation |
| EIP-301 | Routing Slip | | The steps a message passes through are decided per message and travel with it | The message carries its list of steps; each step does its work and forwards to the next | |
| EIP-312 | Process Manager | | A central component tracks state and decides each next step of a multi-step flow | A stateful coordinator per flow instance receives each step's result and decides the next step | see also Saga, Scheduler Agent Supervisor |
| EIP-322 | Message Broker | | A hub must take routing decisions away from senders and receivers | All messages go through a central hub that holds the routing rules | see also Gateway Routing, Mediator |

### EIP Ch 8 — Message transformation

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-330 | Envelope Wrapper | | Content must be wrapped in headers or encoding the transport demands, then unwrapped | Wrap the payload in a transport envelope at entry and unwrap it at exit | |
| EIP-336 | Content Enricher | | A message lacks data the receiver needs, so a step looks it up and adds it | Use keys in the message to fetch missing data from another source and add it | |
| EIP-342 | Content Filter | | A receiver needs only a few fields, so a step strips the rest | Drop the fields the receiver does not need, often flattening the structure | |
| EIP-352 | Normalizer | | The same kind of data arrives in several formats and must become one | Detect each incoming format and route it to a translator into the common format | |
| EIP-355 | Canonical Data Model | | Many applications exchange data, so each maps to one shared format instead of to each other | One shared format; each application translates only to and from it | |

### EIP Ch 10 — Messaging endpoints

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-468 | Messaging Gateway | | Application code should call a domain-level interface that hides all messaging calls | A class with domain methods that sends and receives messages internally | see also Gateway |
| EIP-477 | Messaging Mapper | | Domain objects and messages must convert to each other while staying independent | A separate mapper converts domain objects to messages and back; neither knows the other | see also Data Mapper |
| EIP-484 | Transactional Client | | Sending or receiving must commit or roll back together with other work | Message send or receive joins the same transaction as the other work | see also Transactional Outbox |
| EIP-494 | Polling Consumer | | The receiver should fetch messages when it is ready rather than being pushed them | The consumer asks the channel for the next message on its own schedule | |
| EIP-498 | Event-Driven Consumer | | The receiver should be called automatically whenever a message arrives | The messaging system invokes a registered handler as each message arrives | |
| EIP-508 | Message Dispatcher | | One endpoint receives messages and hands each to one of several performers | A single receiver hands each message to one of several in-process performers | |
| EIP-515 | Selective Consumer | | A receiver should take only the messages that match its criteria from a shared channel | The consumer receives with a selector over message properties | |
| EIP-522 | Durable Subscriber | | A subscriber must not miss events published while it was disconnected | The messaging system stores messages for a registered subscriber while it is offline | |
| EIP-532 | Service Activator | | The same service must be callable through messaging and through ordinary calls | An adapter receives a message, calls the plain service method and sends any reply | |

### EIP Ch 11 — System management

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| EIP-540 | Control Bus | | A distributed system needs its own channel for management and monitoring commands | A separate channel carrying management commands and status reports to components | see also Health Endpoint Monitoring |
| EIP-545 | Detour | | Messages should be sent through extra steps such as validation or debugging, switched on and off | A switchable router sends messages either directly or through extra steps | |
| EIP-547 | Wire Tap | | Messages must be copied to an observer without disturbing their normal flow | A tap forwards each message unchanged and sends a copy to a second channel | |
| EIP-551 | Message History | | Each message should record the components it passed through for debugging | Each component appends its identity to a history list carried in the message | see also Distributed Tracing |
| EIP-555 | Message Store | | Message data is kept for reporting without slowing the live flow | Copies of messages are written to a separate store for later queries | |
| EIP-558 | Smart Proxy | | Replies to a service that uses return addresses must be tracked or intercepted | A proxy replaces the return address with its own, tracks replies and forwards them on | see also Proxy, Correlation Identifier |
| EIP-569 | Test Message | | A running component must be checked by sending it known inputs and verifying the outputs | Inject marked test messages, verify their results and filter them out of real output | |
| EIP-572 | Channel Purger | | Leftover messages must be cleared from a channel so they do not disturb tests or systems | A utility removes all, or selected, messages from a channel | |

## GOF — Design Patterns (Gang of Four)

### GOF Creational

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| GOF-01 | Abstract Factory | | Families of related objects must be created without naming their concrete classes | An interface with one creation method per product; each concrete factory makes one family | |
| GOF-02 | Builder | | A complex object needs step-by-step construction, possibly in several representations | A builder exposes construction steps; a director or caller runs them, then takes the result | |
| GOF-03 | Factory Method | Virtual Constructor | A class should defer the choice of what to instantiate to its subclasses or callers | A creation method that subclasses or injected callables override to choose the class | see also Factory |
| GOF-04 | Prototype | | New objects should be made by copying a configured example | Objects implement clone; new instances are copies of a registered prototype | |
| GOF-05 | Singleton | | Exactly one instance must exist, with one well-known access point | The class controls its own instantiation and hands out the single instance | see also Registry |

### GOF Structural

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| GOF-06 | Adapter | | An existing class has the wrong interface for the code that must use it | A wrapper implements the expected interface by calling the adaptee | see also Anti-Corruption Layer, Message Translator |
| GOF-07 | Bridge | Handle-Body | An abstraction and its implementation should vary independently | The abstraction holds a reference to an implementor interface; both sides have separate hierarchies | |
| GOF-08 | Composite | | Single objects and groups of them should be treated the same way | Leaves and containers share one interface; containers forward calls to their children | |
| GOF-09 | Decorator | | Behaviour should be added to individual objects without subclassing | A wrapper with the same interface adds behaviour before or after delegating | |
| GOF-10 | Facade | | Callers need one simple entry point to a complicated subsystem | One class with a narrow interface that coordinates the subsystem's classes | see also Gateway, Remote Facade |
| GOF-11 | Flyweight | | Very many small objects must share state to fit in memory | Intrinsic state is shared from a pool; extrinsic state is passed in by the caller | |
| GOF-12 | Proxy | Surrogate | Access to an object must be controlled, deferred or made remote | A stand-in with the same interface that controls access, then delegates to the real object | see also Ambassador, Smart Proxy, Lazy Load |

### GOF Behavioral

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| GOF-13 | Chain of Responsibility | | A request should pass along handlers until one deals with it | Handlers are linked; each handles the request or passes it to the next | see also Pipes and Filters |
| GOF-14 | Command | | A request should be an object that can be queued, logged or undone | An object holds a receiver, an action and its arguments, exposing execute and optionally undo | see also Command Message |
| GOF-15 | Interpreter | | Sentences in a small language must be evaluated | One class per grammar rule; an abstract syntax tree of them evaluates itself | |
| GOF-16 | Iterator | Cursor | A collection's elements must be traversed without exposing its structure | A separate object keeps the traversal position and yields elements one at a time | |
| GOF-17 | Mediator | | Many objects interact and their direct references to each other should be removed | Colleagues talk only to a mediator, which holds the interaction logic | see also Message Broker |
| GOF-18 | Memento | | An object's state must be saved and restored without breaking its encapsulation | The object exports an opaque snapshot that a caretaker stores and hands back to restore | |
| GOF-19 | Observer | | Dependents must be notified automatically when an object changes | The subject keeps a list of observers and calls each of them on change, in process | see also Publisher-Subscriber |
| GOF-20 | State | | An object's behaviour must change with its internal state | Behaviour is delegated to a state object that is swapped on each transition | |
| GOF-21 | Strategy | Policy | One of several interchangeable algorithms must be chosen at runtime | Algorithms implement one interface; the context holds and calls a chosen one | see also Plugin |
| GOF-22 | Template Method | | An algorithm's skeleton is fixed but some steps vary | A base method calls overridable step methods in a fixed order | |
| GOF-23 | Visitor | | New operations over a stable object structure must be added without changing its classes | Elements accept a visitor and call its method for their own type (double dispatch) | |

## POEAA — Patterns of Enterprise Application Architecture

### POEAA Domain logic

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-01 | Transaction Script | | Business logic is simple and best written as one procedure per operation | One procedure per business operation, which reads, decides and writes directly | |
| POEAA-02 | Domain Model | | Business logic is complex enough to need objects that hold both data and behaviour | Domain concepts become classes whose methods enforce the business rules on their own data | see also Entity, Value Object |
| POEAA-03 | Table Module | | Logic is organised around database tables and worked on as record sets | One class per table operating on a whole record set, not on individual rows | |
| POEAA-04 | Service Layer | | Many callers need one boundary that defines the application's operations | A layer of operation methods that coordinates domain logic and transactions for every client | see also Domain Service |

### POEAA Data source

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-05 | Table Data Gateway | | All SQL for one table should live in one place | One object per table exposing find, insert, update and delete for it | |
| POEAA-06 | Row Data Gateway | | Each database row should be accessed through one object without business logic | One object per row with fields and persistence methods only | |
| POEAA-07 | Active Record | | Domain objects map one-to-one to rows and may carry their own persistence | A row object that holds domain logic and also loads and saves itself | |
| POEAA-08 | Data Mapper | | Domain objects and the database schema must stay independent of each other | A separate mapper layer moves data between objects and tables; objects know nothing of SQL | see also Messaging Mapper |

### POEAA Object-relational behaviour

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-09 | Unit of Work | | The changes made during one business operation must be written together and consistently | Track new, changed and deleted objects during the operation and commit them in one batch | |
| POEAA-10 | Identity Map | | The same record must not be loaded into two different objects in one session | A per-session map from key to loaded object, checked before every load | |
| POEAA-11 | Lazy Load | Lazy Loading | Related data is expensive and often not needed, so load it only on first use | A placeholder (proxy, ghost or holder) fetches the real data the first time it is accessed | see also Proxy |

### POEAA Object-relational structure

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-12 | Identity Field | | An in-memory object must remember which database row it came from | The object stores its row's key as a field | |
| POEAA-13 | Foreign Key Mapping | | An object reference must be stored as a relationship between tables | A reference is saved as a foreign key column and resolved on load | |
| POEAA-14 | Association Table Mapping | | A many-to-many relationship must be persisted | A link table of key pairs represents the association | |
| POEAA-15 | Dependent Mapping | | Child objects exist only through their owner and are persisted by it | The owner's mapper also loads and saves its dependents | |
| POEAA-16 | Embedded Value | | A small value object should be stored as columns of its owner's table | The value's fields are flattened into the owner's row | |
| POEAA-17 | Serialized LOB | | A complex object graph should be stored as one serialized field | Serialize the graph to a single text or binary column | |
| POEAA-18 | Single Table Inheritance | | An inheritance hierarchy should live in one table | One table with columns for all subclasses and a type discriminator | |
| POEAA-19 | Class Table Inheritance | | Each class in a hierarchy should have its own table | One table per class, joined on a shared key | |
| POEAA-20 | Concrete Table Inheritance | | Each concrete class should have its own complete table | One full table per concrete class, including inherited fields | |
| POEAA-21 | Inheritance Mappers | | Mapper code for an inheritance hierarchy should not be duplicated | A mapper hierarchy that mirrors the class hierarchy and shares common mapping code | |

### POEAA Metadata mapping

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-22 | Metadata Mapping | | Object-to-table mapping should be described as data rather than written by hand | A declarative mapping description that generic code interprets | |
| POEAA-23 | Query Object | | Queries should be built from objects in domain terms, not hand-written SQL | An object structure describing a query that is translated to SQL | see also Repository |

### POEAA Web presentation

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-24 | Model View Controller | MVC | User interface, input handling and domain data must be separated | Model holds data and logic, view renders it, controller turns input into model calls | |
| POEAA-25 | Page Controller | | Each page or action should have its own input handler | One controller object per page or action | |
| POEAA-26 | Front Controller | | All requests need common handling before being dispatched | One handler receives every request, runs shared steps, then dispatches to commands | |
| POEAA-27 | Template View | | Pages should be authored as markup with placeholders for dynamic data | A template with embedded markers that are filled from data at render time | |
| POEAA-28 | Transform View | | Output should be produced by transforming domain data element by element | A transformation walks the data and emits output for each element | |
| POEAA-29 | Two Step View | | Many pages must share one look that can change in one place | First build a logical screen from data, then render it to output in a second step | |
| POEAA-30 | Application Controller | | Screen flow and navigation logic must be centralised | An object that decides which command and view come next, based on state | |

### POEAA Distribution

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-31 | Remote Facade | | Fine-grained objects must be used across a network without many small calls | A coarse-grained interface over fine-grained objects, so one remote call does a lot of work | see also Facade |
| POEAA-32 | Data Transfer Object | DTO | Data must cross a process boundary in one call | A plain serializable object carrying exactly the fields one call needs | |

### POEAA Offline concurrency

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-33 | Optimistic Offline Lock | | Edits spanning several requests rarely conflict, but conflicts must be detected | Save checks a version number read earlier and fails if it has changed | |
| POEAA-34 | Pessimistic Offline Lock | | Edits spanning several requests conflict often and must be prevented | Acquire an application-level lock at the start of the edit, release it at commit | |
| POEAA-35 | Coarse-Grained Lock | | A group of related objects must be locked as one | One shared lock or version covers the whole group | see also Aggregate |
| POEAA-36 | Implicit Lock | | Developers must not be able to forget to take a lock | Framework code acquires locks automatically around data access | |

### POEAA Session state

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-37 | Client Session State | | Session state is small and the server should stay stateless | State travels with the client (cookie, hidden field or URL) on every request | |
| POEAA-38 | Server Session State | | Session state must stay on the server between requests | Server memory or local storage keyed by a session ID | |
| POEAA-39 | Database Session State | | Session state must survive across servers and restarts | Session data is stored as rows in the database, keyed by session | |

### POEAA Base

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| POEAA-40 | Gateway | | Calls to an outside system or resource should be hidden behind one object | An object wrapping the external API in a simple interface of your own design | see also Messaging Gateway, Facade |
| POEAA-41 | Mapper | | Two independent subsystems must exchange data without depending on each other | A separate object that moves data between the two and is known by neither | |
| POEAA-42 | Layer Supertype | | Every class in a layer needs the same common behaviour | One base class for the layer holds the shared behaviour | |
| POEAA-43 | Separated Interface | | A package must depend on an abstraction whose implementation lives elsewhere | Define the interface in one package and implement it in another, so dependencies point inward | |
| POEAA-44 | Registry | | Code needs a well-known place to find shared objects or services | A global or scoped lookup object holding the shared instances | see also Singleton |
| POEAA-45 | Money | | Monetary amounts need correct arithmetic, rounding and currency handling | A value type pairing an amount with a currency and doing safe arithmetic and allocation | see also Value Object |
| POEAA-46 | Special Case | | Callers keep checking for null or an unusual case | A subclass that gives a harmless default behaviour for the special case | related term: Null Object |
| POEAA-47 | Plugin | | Which implementation runs should be chosen by configuration, not by code | Implementations are linked at configuration or startup time behind one interface | see also Strategy, Pluggable Component Framework |
| POEAA-48 | Service Stub | | A slow or unavailable external service should be replaced during testing | A fake implementation of the service interface used in tests | |
| POEAA-49 | Record Set | | Tabular data should be handled in memory in the same shape as a query result | An in-memory table structure of rows and columns | |

## DDD — Domain-Driven Design Reference

### DDD Putting the model to work

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-3 | Ubiquitous Language | | Developers and domain experts must use the same precise terms, in talk and in code | One vocabulary per bounded context, used unchanged in code, tests and documents | see also Bounded Context |

### DDD Building blocks

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-10 | Layered Architecture | | Domain logic must be isolated from UI, application and infrastructure code | Layers that depend only downward, with the domain layer free of technical concerns | |
| DDD-11 | Entity | | An object is defined by a continuing identity, not by its attribute values | A stable identity that persists through changes in attributes; equality by identity | |
| DDD-12 | Value Object | | An object is defined only by its attributes and has no identity of its own | Immutable; equality by attribute values; replaced rather than modified | POEAA (Base patterns); see also Money, Embedded Value |
| DDD-13 | Domain Event | | A business occurrence matters to other parts of the system | An immutable record of a domain fact, named in past tense, published for others to handle | see also Event Message, Event Sourcing |
| DDD-14 | Domain Service | | An important domain operation does not belong naturally to any entity or value | A stateless operation named in the ubiquitous language, taking domain objects as parameters | DDD Reference "Services"; see also Service Layer |
| DDD-15 | Module | | A large model must be split into cohesive, loosely coupled parts that tell its story | Packages named in the domain language, grouping concepts with high cohesion | |
| DDD-16 | Aggregate | | A cluster of objects must change together under invariants that must always hold | A root entity is the only entry point; invariants are enforced within one transaction per aggregate | see also Coarse-Grained Lock |
| DDD-17 | Repository | | Domain code must get and store aggregates without knowing persistence details | A collection-like interface per aggregate root, hiding queries and storage | POEAA (Metadata mapping); see also Query Object |
| DDD-18 | Factory | | Creating an aggregate or complex object involves rules the object should not carry | A separate method or object that builds a valid whole aggregate in one step | see also Factory Method, Abstract Factory |

### DDD Supple design

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-20 | Intention-Revealing Interface | | Callers should understand what an operation does without reading how | Names and signatures state effect and purpose, not mechanism | |
| DDD-21 | Side-Effect-Free Function | | Complex logic should be safe to call and combine without hidden changes | Computation in functions that return results and change no observable state | |
| DDD-22 | Assertion | | The effects of operations and the invariants of objects must be explicit | Stated pre- and post-conditions and invariants, checked by tests or code | |
| DDD-23 | Standalone Class | | A concept should be understandable without many other classes | A class whose dependencies are reduced to the minimum, ideally only primitives | |
| DDD-24 | Closure of Operations | | Operations should combine freely without introducing new types | Operations take and return values of one type, so results feed further calls | |
| DDD-25 | Declarative Design | | Rules should be stated as specifications rather than procedures | Executable declarations (rules, specifications) composed and evaluated by generic code | see also Specification |

### DDD Context mapping

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-29 | Context Map | | The relationships between several bounded contexts must be visible and agreed | A document naming each context and the relationship pattern on each boundary | |
| DDD-30 | Partnership | | Two teams succeed or fail together and must coordinate their contexts | Joint planning and integration of the two contexts' changes | |
| DDD-31 | Shared Kernel | | Two contexts must share a small part of their model | A small explicitly shared subset of the model, changed only by agreement of both teams | |
| DDD-32 | Customer-Supplier Development | Customer-Supplier Development Teams | A downstream context depends on an upstream one that can accommodate its needs | Downstream requirements are planned into upstream work, with joint acceptance tests | |
| DDD-33 | Conformist | | A downstream context must use an upstream model it has no power to change | The downstream adopts the upstream model as is, with no translation | see also Anti-Corruption Layer |
| DDD-35 | Open Host Service | | Many consumers need access to a context through a stable protocol | A published service protocol, designed for all consumers rather than for each one | see also Published Language |
| DDD-36 | Published Language | | Contexts must exchange information in a documented common language | A well-documented shared interchange format, often combined with an open host service | see also Canonical Data Model |
| DDD-37 | Separate Ways | | Integration between two contexts costs more than it returns | No integration: each context solves its needs independently | |
| DDD-38 | Big Ball of Mud | | Part of the system has no consistent model and should be contained rather than fixed | Draw a boundary around the mess and do not let its models spread outside it | |

### DDD Distillation

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-40 | Core Domain | | Effort must be focused on the part of the model that gives the product its value | Identify the core explicitly and give it the best people and design attention | |
| DDD-41 | Generic Subdomain | | Part of the domain is needed but not distinctive | Isolate it in its own module and buy, reuse or keep its design simple | see also Bounded Context |
| DDD-44 | Cohesive Mechanism | | A complex algorithm obscures the model that uses it | Move the computation into a separate framework behind an intention-revealing interface | |
| DDD-45 | Segregated Core | | Core concepts are tangled with supporting code | Refactor the core into its own module, with supporting code depending on it | |
| DDD-46 | Abstract Core | | Several modules interact through concepts that should be modelled once | Put the abstract model of the key interactions in its own module; specialisations live elsewhere | |

### DDD Large-scale structure

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDD-50 | Responsibility Layers | | A large model needs an overall structure by kind of responsibility | Broad layers of responsibility (e.g. capability, operation, policy) with downward dependency | |
| DDD-51 | Knowledge Level | | Users must be able to configure rules and types without code changes | A separate set of objects describing the structure and behaviour of the base level | |
| DDD-52 | Pluggable Component Framework | | Independently built components must work together through shared interfaces | Shared abstract interfaces plus a framework that loads conforming components | see also Plugin |

## AGT — Agent patterns

### AGT Agent workflows

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| AGT-1 | Augmented LLM | | One model call needs facts, actions or memory it does not have | A model call given retrieval, tool and memory interfaces it can invoke during the call | APC augmented-llm |
| AGT-2 | Prompt Chaining | | A task splits into fixed steps known before it starts | A fixed sequence of model calls, each consuming the previous output, with checks between steps | APC prompt-chaining; Separate from Pipes and Filters: the stages are model calls with checks between them; see also Pipes and Filters |
| AGT-3 | Task Router | | Different kinds of input need different prompts, models or handlers | A classifier step labels each input and dispatches it to exactly one specialised handler | APC routing; Separate from Content-Based Router: the router is a model classifying free input, not rules over fields; see also Content-Based Router |
| AGT-4 | Parallelization | | Independent sub-tasks or repeated judgements can run at the same time | Independent model calls run concurrently; code combines their outputs by section or by vote | APC parallelization; Separate from Scatter-Gather: includes voting over identical calls; see also Scatter-Gather |
| AGT-5 | Orchestrator-Workers | | The sub-tasks are known only after the input is read | An orchestrator decides sub-tasks at run time, dispatches workers and merges their results | APC orchestrator-workers; Separate from Process Manager: the sub-tasks are invented at run time; see also Process Manager |
| AGT-6 | Evaluator-Optimizer | Generator-Critic Loop | Output quality can be judged against stated criteria and improves with feedback | A generator produces; a separate evaluator scores against criteria and feeds back; loop until met or capped | APC evaluator-optimizer; see also Augmented LLM |
| AGT-7 | ReAct | Reason+Act | The next action depends on what the last tool call returned | A loop of one reasoning step, one tool call and one observation, until the model stops | APC react |
| AGT-8 | Plan-and-Execute | Plan-Then-Execute | A multi-step task benefits from a whole plan before any action | A planner writes the full step list once; an executor runs each step; replanning only on failure | APC plan-and-execute |
| AGT-9 | Human-in-the-Loop | HITL | An action is risky or irreversible enough that a person must approve it | Execution pauses at a defined point until a person approves, edits or rejects the proposed action | APC human-in-the-loop; see also Stop Hook |
| AGT-10 | Step Budget | Iteration Cap | An agent loop could run, spend or retry without end | A hard cap on iterations or tool calls; reaching it stops the loop with a reported reason | APC step-budget; for loops that call failing tools; see also Circuit Breaker |
| AGT-11 | Stop Hook | | Whether an agent may end its turn must be decided by code, not by the model | A predicate runs when the agent tries to stop and either lets it stop or sends it back with a reason | APC stop-hook |
| AGT-12 | Input and Output Guardrails | Guardrails | Model inputs or outputs can carry harmful, malformed or out-of-policy content | Validators run on inputs before the model and on outputs before use; a failure blocks or rewrites | APC input-output-guardrails; Separate from Gatekeeper: checks both directions around a model, not a front component; see also Gatekeeper |

## DDDB — Domain-Driven Design (2003 book)

### DDDB Supple design

| ID | Pattern | Aliases | Use when | Core mechanism | Ref / See also |
|---|---|---|---|---|---|
| DDDB-1 | Specification | | A business rule that selects or validates objects is needed in several places | A predicate object with is-satisfied-by, combinable with and, or, not, reused for validation and selection | DDD 2003 ch. 9; Evans and Fowler, Specifications |
