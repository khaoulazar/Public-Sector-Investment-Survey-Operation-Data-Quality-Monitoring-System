# RLS turned my report into a scalable and secure asset 
## Row-Level Security (RLS) — Regional Data Access Control

## Overview

This dashboard is shared across **12 regions**, each with its own supervisor and field teams, but it runs as a **single Power BI model** rather than 12 separate reports. Row-Level Security (RLS) is the mechanism that makes this possible: it dynamically filters the data each user sees based on their identity, so every supervisor opens the same dashboard but only ever sees their own region.

## Why RLS — the business case

Before RLS, the alternatives were:
- **One dashboard per region** — 12 reports to build, maintain, and keep in sync every time a measure or visual changes
- **One shared dashboard with no restriction** — every supervisor could see every other region's data, which is both a governance risk and a trust problem for a data-collection operation involving 48 surveyors and sensitive administrative unit data

RLS solves both problems at once: **one model, one set of visuals, one place to maintain logic** — with access boundaries enforced at the data layer, not left to convention or to each supervisor's discipline.

### What RLS delivers

- **Zero cross-region data leakage.** A supervisor in Region A cannot see, filter, or export data from Region B — not because of a hidden slicer, but because the underlying query itself is scoped before it ever reaches the visual layer.
- **One dashboard, 12 supervisors, multiple agent teams.** A single published report serves all 12 regions and their surveyor teams simultaneously. No duplicated maintenance, no version drift between regional copies.
- **~80% improvement in load times.** Each user's queries are scoped to their own region's rows instead of scanning all 2,068 administrative units. Filtering at the source, rather than after the fact, is what actually moves performance — and it's a reminder that the highest-value improvement to a dashboard is rarely a new chart. It's controlling **who sees what, and how much they have to look through to see it.**

## How it works

1. **A security mapping table** links each Power BI user (by email/UPN) to the region(s) they're authorized to see.
2. **A DAX filter expression on the role** applies that mapping to the fact and dimension tables, so every visual, measure, and drill-down automatically respects the boundary — no per-visual configuration needed.
3. **Roles are assigned in the Power BI Service** under **Security → Row-level security**, mapping each supervisor's account to their region's role.
4. **Filter propagation** follows the model's relationships: restricting the region dimension cascades down to the fact tables and every dependent visual, without needing to duplicate the filter logic elsewhere.

## Testing & Validation

Before publishing, each role was validated using **View As Roles** in Power BI Desktop, confirming for every one of the 12 regions that:
- Only that region's administrative units, surveyors, and progress metrics are visible
- Aggregate totals (KPI cards, global Pareto charts) correctly reflect the scoped subset, not the full dataset
- No cross-region drill-through or tooltip leaks data outside the assigned scope

## Key takeaway

Security isn't a feature bolted onto a finished dashboard — it's part of the data model design from day one. For a shared operational tool used by multiple regional teams, **RLS turned a governance requirement into a performance win.**
