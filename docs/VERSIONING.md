# Versioning and Migration Policy

## Semantic Versioning

VA7 follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR** — Breaking changes. Requires migration effort.
- **MINOR** — New features. Backwards compatible.
- **PATCH** — Bug fixes, documentation, performance. Backwards compatible.

## Current Status

| Package | Version | Status |
|---|---|---|
| va7-core | 0.1.0 | Feature-frozen |
| va7-identity | 0.1.0 | Feature-frozen |

**Feature-frozen** means:
- No new features will be added
- No breaking changes will be made
- Only bug fixes, documentation, and performance improvements
- Real-world usage may reveal issues that require minor adjustments

## Stability Guarantees

### What's Guaranteed

- **Public API stability** — Import paths, class names, method signatures
- **Backwards compatibility** — Within a major version
- **Bug fixes** — For issues discovered in production

### What's NOT Guaranteed

- **Internal implementation details** — May change between minor versions
- **Configuration key names** — May be renamed in future major versions
- **Event payloads** — May be extended but not reduced
- **Performance characteristics** — May be optimized

## Breaking Changes

Breaking changes are reserved for MAJOR version bumps. Examples:

- Removing a public class or function
- Changing a method signature
- Renaming a configuration key
- Changing default behavior
- Removing a dependency

## Migration Path

When breaking changes are necessary:

1. **Deprecation period** — Old API works but emits warnings for at least one minor version
2. **Migration guide** — Written documentation showing before/after
3. **Automated migration** — Where possible, provide a script or tool

## Adding New Features

New features are added in MINOR versions:

- New classes, functions, or methods
- New configuration options
- New events
- New permission classes
- New verification methods

All additions are backwards compatible — existing code continues to work.

## Bug Fixes

Bug fixes are released as PATCH versions:

- Security fixes (immediate)
- Data integrity fixes (immediate)
- Behavioral fixes (within days)
- Cosmetic fixes (next release cycle)

## Pre-release Versions

Before 1.0.0, all versions are pre-release:

- **0.1.x** — Initial implementation
- **0.2.x** — Production validation, bug fixes
- **0.3.x** — Next feature set (future packages)

## Dependency Management

VA7 packages declare minimum dependency versions:

```
django>=5.1
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
```

Dependency updates are tested and validated before each release.

## Release Process

1. **Code review** — All changes reviewed
2. **Tests pass** — Full test suite (core + identity)
3. **Documentation updated** — Changelog, API docs, guides
4. **Version bumped** — In `pyproject.toml` and `__init__.py`
5. **Tagged** — Git tag for the release
6. **Published** — PyPI release

## Changelog Format

```markdown
## [0.1.1] - 2026-07-26

### Fixed
- OTP validation race condition under concurrent requests
- Soft-delete manager not filtering correctly in password reset

### Changed
- Improved error logging in logout view

### Deprecated
- Nothing

### Removed
- Nothing

### Security
- Removed hardcoded fallback secret in OTP hashing
```
