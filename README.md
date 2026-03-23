# TMDB API Testing Portfolio

A comprehensive API testing portfolio project built on the [TMDB (The Movie Database) public API](https://developer.themoviedb.org/docs). Demonstrates a complete QA workflow spanning contract testing, functional testing, mock server scenarios, CI/CD integration, Allure reporting, and k6 performance baselines.

**Live Allure Report:** [rohannair03.github.io/tmdb-api-tests](https://rohannair03.github.io/tmdb-api-tests)  
**Stack:** Postman · Newman · GitHub Actions · Allure · k6

---

## Table of Contents

- [Project Structure](#project-structure)
- [Phase 1 — Postman Setup](#phase-1--postman-setup)
- [Phase 2 — Contract Testing](#phase-2--contract-testing)
- [Phase 3 — Mock Server](#phase-3--mock-server)
- [Phase 4 & 5 — Functional Test Suite](#phase-4--5--functional-test-suite)
- [Phase 6 — Newman CLI & GitHub Actions](#phase-6--newman-cli--github-actions)
- [Phase 7 — Allure Reporting](#phase-7--allure-reporting)
- [Phase 8 — k6 Performance Baseline](#phase-8--k6-performance-baseline)
- [Real API Behavioral Findings](#real-api-behavioral-findings)
- [Running Locally](#running-locally)

---

## Project Structure

```
tmdb-api-tests/
├── .github/
│   └── workflows/
│       ├── newman.yml          # Functional tests — push, PR, daily schedule
│       └── k6.yml              # Performance tests — weekly schedule
├── schemas/                    # JSON Schema definitions (tv4)
├── k6-baseline.js              # 1 VU, 60s
├── k6-lightload.js             # 10 VUs, 90s
├── k6-moderateload.js          # 50 VUs, 90s
├── k6-spiketest.js             # 0→100→0 VUs, staged
├── k6-soaktest.js              # 20 VUs, 5 minutes
└── README.md
```

---

## Phase 1 — Postman Setup

- Created a Postman collection targeting the TMDB v3 API
- Configured environment variables: `base_url`, `api_key`, `movie_id`, `tv_id`, `person_id`
- Verified authentication via `api_key` query parameter
- Confirmed baseline connectivity with `GET /movie/popular`

---

## Phase 2 — Contract Testing

JSON Schema contract validation using the **tv4** library, with schemas stored as collection-level pre-request scripts for reuse across requests.

**Schemas validated:**
- Movie list response (`/movie/popular`, `/movie/top_rated`)
- Movie detail response (`/movie/{id}`)
- TV show detail response (`/tv/{id}`)
- Genre list response (`/genre/movie/list`)
- Search results response (`/search/movie`)

Each schema asserts required fields, correct data types, and structural integrity — catching API contract regressions independently of status code checks.

---

## Phase 3 — Mock Server

A Postman mock server simulates 6 failure scenarios to validate client-side error handling without depending on live API state.

| Scenario | Endpoint | Mocked Response |
|----------|----------|-----------------|
| Invalid Search | `GET /search/movie?query=test_500` | 500 Internal Server Error |
| Malformed JSON | `GET /search/movie?query=test_malformed` | 200 with invalid JSON string |
| Empty search results | `GET /search/movie?query=test_empty` | 200 with empty results array |
| Slow response | `GET /search/movie?query=test_slow` | 200 with delay added in mock server |
| Required Field Missing | `GET /movie/test_missing_title` | 200 with contract catching missing field |
| Field Type Changed | `GET /movie/popular` | 200 with contract catching different field |

---

## Phase 4 & 5 — Functional Test Suite

~25 tests across authentication, movies, TV, genres, chained requests, and error cases.

**Coverage areas:**

- **Auth:** Valid key returns 200; invalid key returns 401
- **Movies:** Popular, top rated, detail by ID, now playing, upcoming
- **TV:** Detail by ID, top rated, on-air
- **Genres:** Movie genre list, TV genre list
- **Search:** Query with results, empty query, special characters
- **Chained requests:** Genre ID extracted from genre list, passed into discover endpoint
- **Error cases:** Invalid IDs, missing parameters, malformed requests

Each request includes status code assertions, response time checks, and JSON Schema contract validation.

---

## Phase 6 — Newman CLI & GitHub Actions

Newman runs the full Postman collection from the command line. The CI pipeline (`.github/workflows/newman.yml`) triggers on:

- **Push** to `main`
- **Pull requests** targeting `main`
- **Daily schedule** (cron)
- **Manual trigger** via `workflow_dispatch`

Newman flags used:
- `--env-var` for secret injection via GitHub Secrets
- `--reporters` for Allure-compatible output
- `--bail` to fail fast on first error in PR checks

---

## Phase 7 — Allure Reporting

Allure reports are generated via `newman-reporter-allure@2.0.0` (pinned for compatibility with `allure-commandline`) and published to GitHub Pages.

**Live report:** [rohannair03.github.io/tmdb-api-tests](https://rohannair03.github.io/tmdb-api-tests)

The report provides per-request pass/fail status, response time trends, and failure details including response body diffs — giving a visual audit trail for every CI run.

---

## Phase 8 — k6 Performance Baseline

Five k6 scripts (v1.6.1) establish a performance baseline and validate API behaviour under varying load profiles. All tests were run from Vancouver, CA against the TMDB public API.

### Test Scenarios

| Script | VUs | Duration | p(95) Threshold | Error Threshold | Actual p(95) | Result |
|--------|-----|----------|-----------------|-----------------|--------------|--------|
| k6-baseline.js | 1 | 60s | <1000ms | rate<0.05 | ~208ms | ✅ |
| k6-lightload.js | 10 | 90s | <1500ms | rate<0.01 | 5.75ms | ✅ |
| k6-moderateload.js | 50 | 90s | <2000ms | rate<0.02 | 5.12ms | ✅ |
| k6-spiketest.js | 0→100→0 | 90s (staged) | rate<=0.00 | no 5xx | 325ms | ✅ |
| k6-soaktest.js | 20 | 5m | <2000ms | rate<=0.01 | 366ms | ✅ |

### User Journeys

Two realistic browsing journeys are simulated across load tests. Each VU randomly selects a journey per iteration via `Math.random()`, simulating a diverse user population. A 1 second think time between requests models realistic user behaviour.

**Journey 1 — Browse & Search**
1. `GET /movie/popular` — landing page
2. `GET /search/movie?query=Dune+Part+Two` — user searches for a title
3. `GET /tv/1396` — user views a TV show detail page

**Journey 2 — Genre Discovery**
1. `GET /genre/movie/list` — browse movie genres
2. `GET /genre/tv/list` — browse TV genres
3. `GET /discover/movie?with_genres=28` — explore action movies

### Observations & Findings

**CDN Caching Effect**

Light and moderate load tests produced anomalously low p(95) results (~5ms) compared to the baseline (~208ms). This reflects CDN-cached responses — repeated hits to the same endpoints within short windows are served from cache rather than the origin server. This accurately represents real user experience, as end users benefit from the same caching infrastructure in production.

**Cache Expiry Under Sustained Load**

Spike and soak tests show significantly higher p(95) (325ms and 366ms respectively) despite not having the highest concurrent VU counts. Two factors contribute:

- **Spike test:** 100 VUs generating diverse simultaneous requests bypasses cache warming, resulting in more origin fetches
- **Soak test:** Cache TTLs expire over the 5 minute duration, forcing fresh origin fetches as the test progresses — latency increases gradually rather than spiking, consistent with cache expiry rather than server degradation

**Threshold Design Decisions**

- `rate<0.05` on the baseline accommodates transient EOF errors observed on initial runs against the live API
- Light and moderate load scripts use 90s duration rather than 60s to reduce the statistical weight of single transient failures — one dropped request out of 900 has less impact than one out of 300
- `rate<=0.00` on the spike test enforces zero failure tolerance; note that `rate<0.00` is mathematically impossible and will cause k6 to flag a threshold violation even when the actual error count is zero — `<=` is required

### CI Integration

k6 runs as a separate GitHub Actions workflow (`.github/workflows/k6.yml`) on a weekly schedule (Mondays 17:30 UTC) and supports manual triggering via `workflow_dispatch`. The weekly cadence is intentional — the soak test's 5 minute duration makes the total job runtime unsuitable for push/PR triggers.

JSON summaries from all five runs are stored as CI artifacts for trend analysis over time.

---

## Real API Behavioral Findings

Two deviations from expected REST conventions were documented during functional testing:

**Finding 1 — Empty search query returns 200 instead of 422**

`GET /search/movie?query=` with an empty `query` parameter returns `200 OK` with an empty results array, rather than `422 Unprocessable Entity`. A missing or blank required parameter would conventionally return a validation error. This is a benign but noteworthy deviation — clients relying on a 422 to detect missing query input will not receive it.

**Finding 2 — Out-of-range pagination returns 400 instead of 422**

Requesting a `page` parameter beyond the valid range returns `400 Bad Request` rather than `422 Unprocessable Entity`. While both indicate a client error, 422 is the more semantically appropriate response for a validation failure on a known parameter. The inconsistency between these two findings (empty query → 200, invalid page → 400) also suggests non-uniform input validation across endpoints.

Both findings are documented as test cases in the Postman collection with assertions written against the actual observed behaviour.

---

## Running Locally

### Prerequisites

- [Postman](https://www.postman.com/) or [Newman](https://www.npmjs.com/package/newman)
- [k6](https://k6.io/docs/get-started/installation/)
- TMDB API key from [developer.themoviedb.org](https://developer.themoviedb.org)

### Newman

```bash
npm install -g newman
newman run <collection.json> --environment <environment.json> --env-var "api_key=YOUR_KEY" --env-var "base_url=https://api.themoviedb.org/3"
```

### k6

```bash
# Single script
k6 run --env TMDB_API_KEY=YOUR_KEY k6-baseline.js

# All scripts
k6 run --env TMDB_API_KEY=YOUR_KEY --summary-export=k6-baseline.json k6-baseline.js
k6 run --env TMDB_API_KEY=YOUR_KEY --summary-export=k6-lightload.json k6-lightload.js
k6 run --env TMDB_API_KEY=YOUR_KEY --summary-export=k6-moderateload.json k6-moderateload.js
k6 run --env TMDB_API_KEY=YOUR_KEY --summary-export=k6-spiketest.json k6-spiketest.js
k6 run --env TMDB_API_KEY=YOUR_KEY --summary-export=k6-soaktest.json k6-soaktest.js
```

---

*Built as a standalone QA portfolio project demonstrating end-to-end API testing practices: contract validation, functional coverage, mock server design, CI/CD integration, and performance baselining.*
