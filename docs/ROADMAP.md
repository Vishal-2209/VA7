# VA7 Roadmap

**Last updated:** 2026-07-26

## Current Phase: Production Validation

**Status:** In progress

Both `va7-core` (0.1.0) and `va7-identity` (0.1.0) are feature-frozen. The next step is building a real production application on top of them to validate the design through actual usage.

**Exit criteria:**
- Application is deployed and serving real users
- No critical issues discovered in production
- API friction points documented
- Performance baseline established

## Future Packages

Packages below are planned but NOT designed yet. Each will be built only after concrete needs emerge from production experience.

### v0.3 — Organization Layer

**Depends on:** Production validation of core + identity

| Package | Purpose | Status |
|---|---|---|
| va7-org | Multi-tenant organizations, workspaces, memberships | **Planned** |
| va7-notify | Notification delivery (email, SMS, in-app) | **Planned** |
| va7-audit | Activity logging, change tracking | **Planned** |

**Design questions to answer from production:**
- How are organizations structured? Flat or hierarchical?
- What membership roles are needed?
- How do tenants isolate data?
- What notifications are sent?
- What activities need auditing?

### v0.4 — Business Logic

**Depends on:** va7-org design

| Package | Purpose | Status |
|---|---|---|
| va7-billing | Subscription plans, payment processing | **Planned** |
| va7-workflow | Task automation, approvals | **Experimental** |
| va7-analytics | Usage tracking, reporting | **Experimental** |

### v0.5 — Advanced Features

**Depends on:** Production experience

| Package | Purpose | Status |
|---|---|---|
| va7-search | Full-text search, filtering | **Deferred** |
| va7-cache | Caching strategies, invalidation | **Deferred** |
| va7-queue | Background job processing | **Deferred** |

## Intentionally Deferred

These features are NOT planned for any specific version:

| Feature | Reason |
|---|---|
| GraphQL support | REST is sufficient for now; add if needed |
| Admin interface customization | Django admin is adequate |
| Internationalization | Add when multi-language is needed |
| Mobile SDKs | API-first; SDKs can be generated later |
| Real-time/WebSockets | Add when real-time features are needed |
| OAuth/social login | Use Django's native backends |
| MFA/TOTP | Use VerificationMethod interface |
| API key authentication | Use Django's BaseBackend |

## Design Principles for Future Packages

1. **Validate before building** — No package without production proof of need
2. **Compose, don't extend** — Packages should work together, not inherit from each other
3. **Django-native** — Use Django's systems; don't reinvent
4. **Minimal surface area** — Fewer public APIs = fewer breaking changes
5. **Event-driven coupling** — Packages communicate via events, not imports
6. **Configuration over code** — Behavior should be configurable, not hardcoded

## Version Timeline

| Version | Target | Scope |
|---|---|---|
| 0.1.0 | Current | Core + Identity (feature-frozen) |
| 0.1.x | Ongoing | Bug fixes from production |
| 0.2.0 | TBD | Improvements based on production feedback |
| 0.3.0 | TBD | Organization layer (if needed) |
| 1.0.0 | TBD | Stable API, production-proven |

## How to Influence the Roadmap

The roadmap is driven by production experience, not speculation. To influence it:

1. **Build with VA7** — Use it in a real project
2. **Document friction** — Report every awkward API, missing feature, or repetitive pattern
3. **Share feedback** — Open issues with concrete use cases
4. **Contribute** — Submit PRs for bug fixes and improvements

**The best way to shape VA7's future is to use it today.**
