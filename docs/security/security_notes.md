# DetTrace++ Security Notes

DetTrace is a local developer/debugging tool and demo platform.

## Current scope

- Local FastAPI service
- Local JSON-backed incident store
- No authentication
- No external network dependency required for core replay flows

## Defensive handling

- Input is normalized into structured event models
- API tests validate expected ingestion behavior
- Docker image isolates runtime dependencies
- CI verifies replay and ingestion workflows

## Not implemented

- authentication / authorization
- tenant isolation
- secrets management
- rate limiting
- production database access controls

## Safe productionization path

Before production deployment:
- add auth middleware
- add request size limits
- add structured logging
- move incident store to PostgreSQL
- add service-level rate limits
- add deployment secrets management
