# Contributing to the Governed Autonomous SDLC Factory

We welcome contributions from the community. This document outlines how to contribute effectively.

## Code of Conduct

Be respectful, constructive, and professional. We are building enterprise infrastructure — quality matters.

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Provide a clear description of the problem
3. Include steps to reproduce
4. Include relevant logs and error messages
5. Specify your environment (OS, Python version, Node version)

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Run type check: `cd apps/web && npm run typecheck`
6. Run frontend build: `cd apps/web && npm run build`
7. Commit with clear messages
8. Push to your fork
9. Submit a pull request

### Code Standards

- **Python**: Follow PEP 8. Use type hints. Docstrings for all public functions.
- **TypeScript**: Strict mode. No `any` types. Explicit return types for public functions.
- **Tests**: All new features must include tests. Maintain 100% pass rate.
- **Documentation**: Update docs for any user-facing changes.

### Commit Messages

Use conventional commits:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests
- `refactor:` — Code refactoring
- `chore:` — Maintenance

### Review Process

1. All PRs require at least one review
2. CI must pass (tests, build, type check)
3. Documentation must be updated
4. No merge conflicts

## Development Setup

See [docs/deployment/local.md](docs/deployment/local.md) for local development setup.

## Questions?

Open an issue with the `question` label.
