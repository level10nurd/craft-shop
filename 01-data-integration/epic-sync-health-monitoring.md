# Sync Health Monitoring Dashboard - Brownfield Enhancement

## Epic Goal

Add a simple web-based monitoring dashboard to provide real-time visibility into sync operations status and enable proactive issue detection for the Craft Contemporary Data Integration Service.

## Epic Description

**Existing System Context:**

- Current relevant functionality: Python-based data sync service between Lightspeed Retail POS and Supabase database with automated daily synchronization
- Technology stack: Python 3.x, Supabase (PostgreSQL), cron scheduling, basic logging system
- Integration points: Existing sync_log and sync_state tables, current logging infrastructure, scheduled sync scripts

**Enhancement Details:**

- What's being added/changed: Simple Flask-based web dashboard to display sync status, recent sync history, and basic health metrics
- How it integrates: Connects to existing Supabase database to read sync_log and sync_state tables, no changes to core sync logic
- Success criteria: Dashboard displays current sync status, shows last 7 days of sync history, provides clear visual indicators for healthy vs. problematic syncs

## Stories

1. **Story 1:** Create basic Flask web application with authentication and sync status overview page showing current state of all entity syncs

2. **Story 2:** Add sync history dashboard displaying recent sync operations with filtering by date range and entity type, including error details

3. **Story 3:** Implement health indicators and basic alerting system with visual status indicators and optional email notifications for failed syncs

## Compatibility Requirements

- [x] Existing APIs remain unchanged
- [x] Database schema changes are backward compatible (read-only access to existing tables)
- [x] UI changes follow existing patterns (new standalone web interface)
- [x] Performance impact is minimal (read-only queries with basic caching)

## Risk Mitigation

- **Primary Risk:** Additional database load from dashboard queries impacting sync performance
- **Mitigation:** Implement read-only database connections with query result caching and limit dashboard query frequency
- **Rollback Plan:** Remove Flask application and any new configuration files - core sync system remains unaffected

## Definition of Done

- [x] All stories completed with acceptance criteria met
- [x] Existing functionality verified through testing (sync operations continue normally)
- [x] Integration points working correctly (dashboard accurately reflects sync state)
- [x] Documentation updated appropriately (README updated with dashboard setup instructions)
- [x] No regression in existing features (sync performance maintains current levels)

---

**Story Manager Handoff:**

"Please develop detailed user stories for this brownfield epic. Key considerations:

- This is an enhancement to an existing system running Python 3.x with Supabase PostgreSQL backend
- Integration points: sync_log table, sync_state table, existing .env configuration
- Existing patterns to follow: Python logging patterns, Supabase client usage, environment variable configuration
- Critical compatibility requirements: Read-only database access, no impact on existing sync scripts, maintain current sync performance
- Each story must include verification that existing functionality remains intact

The epic should maintain system integrity while delivering real-time visibility into sync operations for the Craft Contemporary Data Integration Service."