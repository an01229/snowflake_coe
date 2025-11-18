# Security Policy

## Credential Management

All credentials and secrets must be stored as environment variables or in a secure secret manager (AWS Secrets Manager, Azure Key Vault, etc.).

**Never commit:**
- Passwords or API keys
- Connection strings with embedded credentials
- `.env` files (only `.env.example` should be committed)
- YAML files with plaintext passwords

## Environment Variables

All Python scripts in this repository have been updated to use environment variables for sensitive information. See `.env.example` for the required environment variables.

To use the scripts:
1. Copy `.env.example` to `.env`
2. Fill in your actual credentials in `.env`
3. Never commit `.env` to version control

## Credential Rotation

If credentials are accidentally committed:
1. **Rotate the credentials immediately** - assume they are compromised
2. Update all systems using the old credentials
3. Consider using git-filter-repo to remove from history (coordinate with team first)
4. Enable secret scanning in your CI/CD pipeline

## Pre-commit Hooks

This repository includes a pre-commit hook configuration for secret scanning using gitleaks. To enable:

```bash
pip install pre-commit
pre-commit install
```

This will automatically scan for secrets before each commit.

## Reporting Security Issues

If you discover a security vulnerability, please report it to the repository maintainers immediately. Do not create public issues for security vulnerabilities.

Contact: saikrishna.c@anblicks.com
