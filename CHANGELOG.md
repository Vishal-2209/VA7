# Changelog

All notable changes to VA7 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-26

### Added

#### va7-core
- BaseModel with UUID primary keys, auto-managed timestamps, soft-delete
- Event bus: `emit()`, `listen()`, `unlisten()`, `clear()`, `get_listeners()`
- Custom DRF exception handler with standardized error envelope
- SecurityHeadersMiddleware, HealthCheckMiddleware, TrueClientIPMiddleware
- LazySettings with deep merge, dot-notation access, thread-safe loading
- ChangeTrackingMixin for created_by/updated_by fields
- SoftDeleteAdminMixin for admin restore actions
- Utility functions: is_truthy, get_env_variable, run_in_background, deprecated

#### va7-identity
- AbstractRoleUser with email auth, nullable role, UUID PK
- AbstractToken for JWT refresh token storage
- EmailBackend extending Django's ModelBackend
- HasRole permission with And/Or/Not combinators
- VerificationMethod interface with OTPMethod implementation
- OTPService with rate-limiting
- RegistrationService, PasswordResetService, EmailVerificationService
- JWT token generation and blacklisting via services/tokens.py
- 8 REST endpoints: register, login, logout, profile, password reset, email verification
- 7 identity events for cross-package hooks

#### Infrastructure
- GitHub Actions workflow for PyPI publishing
- pytest-django test suites (153 tests total)
- Full documentation: READMEs, stability reviews, auth/permissions/events/services/extension guides
