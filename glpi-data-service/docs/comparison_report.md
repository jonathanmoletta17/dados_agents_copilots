# GLPI Projects Comparison Report

## Overview
This report compares the configuration and implementation of three GLPI integration projects:
1.  **Project 04 (SIS)**: `04-glpi-smart-search` (Port 5173)
2.  **Project 04.1 (DTIC)**: `04.1-sis-smart-search` (Port 5174)
3.  **Project 05 (Data Service)**: `05-glpi-data-service`

## Configuration & Authentication

| Feature | Project 04 / 04.1 | Project 05 |
| :--- | :--- | :--- |
| **Env Loading** | Scoped (`backend/.env` or `frontend/.env`) | Centralized (`.env` in parent dir) |
| **Auth Method** | `App-Token` + `User-Token` -> `Session-Token` | `App-Token` + `User-Token` -> `Session-Token` |
| **Session Mgmt** | `requests.Session` with auto-renewal | `requests.Session` with auto-renewal |
| **Base URL** | Configurable via `GLPI_URL` | Configurable via `GLPI_DTIC_URL` / `GLPI_SIS_URL` |

## Data Fetching Strategy

| Feature | Project 04 / 04.1 | Project 05 |
| :--- | :--- | :--- |
| **Method** | Full Fetch (`fetch_all_tickets`) | Incremental Fetch (`get_tickets_incremental`) |
| **Pagination** | `range` parameter (0-1000) | `range` parameter (0-100) |
| **Search Criteria** | All tickets | `date_mod` > last_sync |
| **Order** | Default | `date_mod ASC` |

## Data Enrichment & Mapping

| Feature | Project 04 / 04.1 | Project 05 |
| :--- | :--- | :--- |
| **Actors (User/Tech)** | **Yes**. Fetches `Ticket_User` and maps IDs to Names. | **No**. Returns raw IDs or requires separate calls. |
| **Groups** | **Yes**. Fetches `Group_Ticket` and maps IDs to Names. | **No**. Returns raw IDs or requires separate calls. |
| **Entities** | **Yes**. Maps `entities_id` to Name. | **No**. Returns raw IDs. |
| **Categories** | **Yes**. Maps `itilcategories_id` to Name. | **No**. Returns raw IDs. |
| **Pending Reasons** | **Yes**. Fetches via `search/Ticket` with `forcedisplay`. | **No**. |
| **Content Format** | **Markdown**. Converts HTML to Markdown. | **Raw HTML**. |
| **Status** | **Mapped**. Converts Status ID to Text. | **Raw ID**. |

## Discrepancies & Recommendations

### 1. Lack of Data Enrichment in Project 05
**Issue**: Project 05 fetches raw ticket data. This puts the burden of resolving IDs (Users, Groups, Entities) on the consumer or requires many additional API calls.
**Recommendation**: Implement an "Enrichment Layer" in Project 05 that:
- Caches Metadata (Users, Groups, Entities, Categories).
- Resolves IDs to Names before storing/returning data.
- Fetches Relationships (Actors, Groups) for each batch of tickets.

### 2. Content Formatting
**Issue**: Project 05 stores raw HTML content.
**Recommendation**: Integrate `TextProcessor` (from Project 04) to convert HTML to Markdown for consistent consumption.

### 3. Pending Reasons
**Issue**: Project 05 does not capture "Pending Reasons", which is critical for SLA analysis.
**Recommendation**: Add a step to fetch Pending Reasons using the `search/Ticket` endpoint, similar to Project 04.

### 4. Configuration Standardization
**Issue**: Project 05 uses a custom `Config` class that loads from a parent `.env`.
**Recommendation**: Keep the centralized `.env` approach as it supports multiple contexts (SIS/DTIC) better than the single-scoped approach of 04/04.1, but ensure variable naming is consistent (`GLPI_URL` vs `GLPI_SIS_URL`).

## Conclusion
To standardize Project 05, we must port the **Enrichment Logic** from Project 04/04.1 into the `GLPIClient` or a new `TicketService` class in Project 05. This will ensure the data service provides complete, usable data.
