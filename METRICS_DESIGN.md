# Listing Metrics Design Spec

## Goal

Add higher-value operational metrics to the existing top-right analytics card system without turning the app into a marketplace or adding external marketplace API dependencies.

The dashboard should answer three questions immediately:

1. What inventory exists and what is it worth?
2. What needs action today?
3. Where are listings blocked from getting posted or sold?

## Current implementation audit

### Data model

`models.py:34-54` defines `ListingItem` with the fields currently available for metrics:

- `created_at`
- `deadline_at`
- `auction_ends_at`
- `sold_at`
- `archived_at`
- `status`: `drafting`, `ready`, `listed`, `sold`, `archived`
- `previous_status`
- `listing_type`: `fixed_price` or `auction`
- `price`
- `sold_price`
- `notes`
- `posted_platforms`: dict keyed by `nextdoor`, `ebay`, `facebook`
- `posted_urls`
- `watch_count`
- `response_count`
- `photo_paths`
- `source_folder`

There is no `updated_at`, `listed_at`, per-platform listed timestamp, status history, or view count.

### Current summary calculation

`storage.py:90-113` builds the dashboard summary:

- `items = self.list_items()`
  - Active/non-archived items only.
  - `list_items()` filters out `status == "archived"` at `storage.py:16-20`.
- `all_items = self.list_all_items()`
  - Includes archived items.
- `live_items = [item for item in items if item.status != "sold"]`
  - Includes drafting, ready, and listed items.
- `sold_items = [item for item in all_items if _is_sold(item)]`
  - `_is_sold()` counts active sold items and archived items whose `previous_status == "sold"` at `storage.py:160-163`.

Existing keys:

| Key | Logic | Rendered today? |
|---|---|---|
| `total` | `len(items)` | yes |
| `drafting` | active items with `status == "drafting"` | yes |
| `ready` | active items with `status == "ready"` | yes |
| `sold` | active sold + archived previous-sold | yes |
| `responses` | sum of `response_count` across active items | yes |
| `live_value` | sum of parsed `price` for active non-sold items | yes |
| `sold_value` | sum of parsed `sold_price or price` for sold items, including archived sold | yes |
| `listing_age` | oldest active non-sold `created_at`, formatted by `_age_label()` | no; calculated but not shown |

### Current rendering

`app.py:335-352` passes `summary=store.summary()` into `templates/home.html`.

`templates/home.html:35-64` renders the top-right analytics panel as:

1. Total
2. Drafting
3. Ready
4. Responses
5. Sold
6. Live value
7. Sold value

The panel uses:

- `.command-deck` two-column layout at `static/style.css:111-116`
- `.stats-grid.analytics-panel` at `templates/home.html:35`
- `.stats-grid` two-column card grid at `static/style.css:179-183`
- `.stats-grid article` gray card styling at `static/style.css:185-188`
- `.stats-grid .value-card` orange-tinted value styling at `static/style.css:204-213`

Per-item supporting signals already render inside each item card at `templates/home.html:165-182`:

- Watchers
- Responses
- Time left from `deadline_at`
- Created

Per-platform posting status renders in each platform draft at `templates/home.html:236-272` using `item.posted_platforms` and `item.posted_urls`.

Auction deadline support already exists:

- `models.py:71-75`: `auction_time_left_label`
- `drafts.py:47`: eBay draft includes `auction ends` when present
- `templates/home.html:251-253`: auction end callout in eBay draft

## Constraints and data limitations

Do not fake precision the app does not have.

- `created_at` is the only reliable age baseline. It means catalog intake time, not necessarily list/post time.
- There is no `updated_at`; stale draft metrics must use `created_at` until an update timestamp exists.
- There is no `listed_at`; average days active and conversion over time must be approximate unless status transition timestamps are added.
- `posted_platforms` is manually maintained and only records true/false, not date posted.
- Watchers/responses are manually maintained and may be stale.

Recommended approach: add useful metrics using existing fields now, then add timestamp fields later only if the first version proves useful.

## Proposed summary groups

### Group A: Existing inventory metrics to keep

Keep these because they are already useful and cheap:

| Label | Summary key | Card style | Placement |
|---|---|---|---|
| Total | `total` | gray | Inventory section |
| Drafting | `drafting` | gray | Inventory section |
| Ready | `ready` | gray | Inventory section |
| Responses | `responses` | gray | Momentum section |
| Sold | `sold` | gray | Outcome section |
| Live value | `live_value` | orange/value | Value section |
| Sold value | `sold_value` | orange/value | Value section |

Add `Listed` because `status == "listed"` exists and is accepted by the metadata form but is currently invisible in the summary.

| Label | Summary key | Logic |
|---|---|---|
| Listed | `listed` | active items with `status == "listed"` |

### Group B: Action metrics to add first

These are the highest-value additions because they tell Drew what to do next.

| Label | Summary key | Logic | Threshold | Card style | Click/filter target |
|---|---|---|---|---|---|
| Needs photos | `needs_photos` | active non-sold items with `len(photo_paths) == 0` | any count > 0 | orange/action | future filter: `?filter=needs_photos` |
| Needs details | `needs_details` | active non-sold items missing usable title, description, or price | any count > 0 | orange/action | future filter: `?filter=needs_details` |
| Stale drafts | `stale_drafts` | active items with `status == "drafting"` and age >= 7 days | 7 days | orange/action | future filter: `?filter=stale_drafts` |
| Post gaps | `platform_gap_total` | ready/listed active items not posted to at least one platform | any count > 0 | orange/action | future filter: `?filter=post_gaps` |
| Auction due | `auction_due` | active unsold auction items with `auction_ends_at` within 48h or already ended | 48 hours | orange/action | future filter: `?filter=auction_due` |

Detailed calculation rules:

#### `needs_photos`

Count active non-sold items where:

```python
item.status != "sold" and len(item.photo_paths) == 0
```

Rationale: Listings without photos are not post-ready anywhere.

#### `needs_details`

Count active non-sold items where any of these are true:

```python
not item.title.strip()
item.title.strip().lower().startswith("untitled")
not item.description.strip()
item.description.strip().lower() in {"description needed.", "description needed"}
len(item.description.strip()) < 12
not item.price.strip()
_money_value(item.price) <= 0
```

Rationale: A listing with photos but weak details still requires manual work before posting.

Do not classify short but intentional descriptions like `Refurbished` as invalid if Drew wants ultra-short descriptions. If that becomes noisy, lower the description rule to only blank/placeholder.

#### `stale_drafts`

Count active draft items where:

```python
item.status == "drafting" and utc_now() - item.created_at >= timedelta(days=7)
```

Rationale: Without `updated_at`, `created_at` is the least-bad stale signal.

#### `platform_gap_total`

Eligible items:

```python
item.status in {"ready", "listed"}
```

Required platform keys:

```python
PLATFORM_KEYS = ("nextdoor", "ebay", "facebook")
```

For each eligible item, count it once if any platform is not posted:

```python
any(not item.posted_platforms.get(platform, False) for platform in PLATFORM_KEYS)
```

Also expose per-platform gap counts:

```python
platform_gaps = {
    platform: sum(
        1 for item in eligible_items
        if not item.posted_platforms.get(platform, False)
    )
    for platform in PLATFORM_KEYS
}
```

Rationale: Drew needs to know whether ready inventory is actually live on the selling channels.

#### `auction_due`

Count active unsold auction items where:

```python
item.listing_type == "auction"
item.auction_ends_at is not None
item.auction_ends_at - utc_now() <= timedelta(hours=48)
```

Include expired auctions in the same count. They are still action items.

Also expose:

- `auction_ended`: auction due items where `auction_ends_at <= utc_now()`
- `next_auction_deadline`: nearest future `auction_ends_at`, formatted with existing `format_time_delta()` behavior

### Group C: Health metrics to add after action metrics

These are useful, but less urgent than action blockers.

| Label | Summary key | Logic | Card style | Note |
|---|---|---|---|---|
| Avg live age | `avg_live_age` | average whole days since `created_at` for active non-sold items | gray | approximate until `listed_at` exists |
| Oldest live | `listing_age` | already calculated; render existing key | gray or orange if >14d | current key is unused |
| Conversion | `conversion_rate` | sold / sellable total | gray | use current catalog-wide metric first |
| 30d sold | `sold_30d` | sold items with `sold_at` in last 30 days | gray | requires `sold_at`; older sold records may lack it |
| Response rate | `response_rate` | active items with `response_count > 0` / active non-sold items | gray | manual response counts only |

#### `avg_live_age`

Use active non-sold items:

```python
live_items = [item for item in items if item.status != "sold"]
avg_days = sum((utc_now() - item.created_at).days for item in live_items) / len(live_items)
```

Format as:

- `No live listings` when empty
- `<1d` when average is under 1 day
- `3d avg` for whole-day averages

#### `conversion_rate`

Recommended v1 logic:

```python
sellable_items = [
    item for item in all_items
    if item.status in {"ready", "listed", "sold"}
    or (item.status == "archived" and item.previous_status in {"ready", "listed", "sold"})
]
conversion_rate = len(sold_items) / len(sellable_items)
```

Format as `0%` when denominator is zero.

Do not include `drafting` in the denominator; drafts were not actually sellable yet.

#### `sold_30d`

Use:

```python
sold_at is not None and sold_at >= utc_now() - timedelta(days=30)
```

Fallback: do not infer from `archived_at` unless explicitly labeled `closed_30d`. Sold and archived are different events.

## Recommended top-right UI layout

Keep the orange/gray card language. Add light section labels inside the same right-hand analytics panel so the grid does not become a random block of numbers.

### Proposed order

Within `templates/home.html:35-64`, replace the flat seven-card list with this ordered structure:

1. Action row, orange/action cards
   - Needs photos
   - Needs details
   - Stale drafts
   - Post gaps
   - Auction due
2. Inventory row, gray cards
   - Total
   - Drafting
   - Ready
   - Listed
3. Momentum/outcome row, gray cards
   - Responses
   - Sold
   - Avg live age
   - Conversion
4. Value row, existing orange/value cards
   - Live value
   - Sold value

If vertical space becomes too tall, hide secondary health metrics behind a `<details>` block labeled `More metrics`, but keep the action row always visible.

### Card styles

Add these CSS concepts instead of inventing a new visual system:

- Existing default gray card: normal informational metrics.
- Existing `.value-card`: dollar values.
- New `.attention-card`: action metrics.

Recommended `.attention-card` behavior:

- If count is zero: keep gray/default style so zero looks calm.
- If count is nonzero: orange border/gradient and orange-dark number.

Possible template pattern:

```jinja2
<article class="attention-card{% if summary.needs_photos %} active{% endif %}">
  <span>Needs photos</span>
  <strong>{{ summary.needs_photos }}</strong>
</article>
```

### Platform gap display

Do not make three full cards for Nextdoor/eBay/Facebook in the first pass; it will crowd the panel.

Use one main `Post gaps` card:

- Strong value: `summary.platform_gap_total`
- Small subline: `ND {{ summary.platform_gaps.nextdoor }} / eBay {{ summary.platform_gaps.ebay }} / FB {{ summary.platform_gaps.facebook }}`

This preserves the card grid and still surfaces the platform-specific gap.

### Auction due display

Use one `Auction due` card:

- Strong value: `summary.auction_due`
- Small subline:
  - `{{ summary.auction_ended }} ended` if ended count > 0
  - else `Next {{ summary.next_auction_deadline }}` if present
  - else `None scheduled`

## Recommended implementation shape

### File changes

1. `storage.py`
   - Import `timedelta`.
   - Add module constant:
     ```python
     PLATFORM_KEYS = ("nextdoor", "ebay", "facebook")
     ```
   - Extend `CatalogStore.summary()` with the new keys.
   - Add helper functions for:
     - `_needs_details(item)`
     - `_age_days(item)`
     - `_format_days_average(days)`
     - `_percent(numerator, denominator)`
     - `_platform_gaps(items)`

2. `templates/home.html`
   - Replace the existing seven summary cards at lines 35-64 with grouped cards.
   - Add subline markup only where needed:
     - Post gaps
     - Auction due
     - Conversion if denominator is useful later

3. `static/style.css`
   - Add `.stats-section-label` for section labels.
   - Add `.metric-subline` for small text inside cards.
   - Add `.attention-card.active` using the existing orange variables.
   - Keep responsive behavior under existing media queries.

4. `tests/test_catalog_core.py`
   - Add tests for summary calculation:
     - counts listed items
     - counts missing photos
     - counts missing details
     - counts stale drafts
     - calculates per-platform gaps
     - counts auction deadlines due/ended
     - formats avg live age and conversion

5. `tests/test_app.py`
   - Extend dashboard render test to assert new labels appear:
     - `Needs photos`
     - `Needs details`
     - `Stale drafts`
     - `Post gaps`
     - `Auction due`
     - `Avg live age`
     - `Conversion`

### Suggested summary return shape

Keep `summary` a plain dictionary so templates remain simple:

```python
{
    "total": 4,
    "drafting": 3,
    "ready": 1,
    "listed": 0,
    "sold": 0,
    "responses": 0,
    "live_value": "$448",
    "sold_value": "$0",
    "listing_age": "7d 4h",
    "needs_photos": 0,
    "needs_details": 1,
    "stale_drafts": 3,
    "platform_gap_total": 1,
    "platform_gaps": {
        "nextdoor": 1,
        "ebay": 1,
        "facebook": 1,
    },
    "auction_due": 0,
    "auction_ended": 0,
    "next_auction_deadline": "None scheduled",
    "avg_live_age": "7d avg",
    "conversion_rate": "0%",
    "sold_30d": 0,
    "response_rate": "25%",
}
```

## Implementation priority

### Phase 1: High-value action metrics

Implement first:

1. `listed`
2. `needs_photos`
3. `needs_details`
4. `stale_drafts`
5. `platform_gap_total`
6. `platform_gaps`
7. `auction_due`
8. `auction_ended`
9. render the action row

Reason: these immediately identify blockers and do not require new stored fields.

### Phase 2: Health/outcome metrics

Implement after Phase 1:

1. `avg_live_age`
2. render existing `listing_age` as `Oldest live`
3. `conversion_rate`
4. `sold_30d`
5. `response_rate`

Reason: useful, but more likely to be misread because the app does not yet track true listing dates.

### Phase 3: Add timestamps only if needed

If Drew wants more accurate conversion and age metrics, add new fields later:

- `updated_at`
- `ready_at`
- `listed_at`
- `posted_at_by_platform`: dict of platform timestamp strings
- optional `status_events`: list of `{from, to, at}`

Do not add these in Phase 1. The existing JSON catalog can support the first set of metrics without migration complexity.

## Acceptance criteria

A successful implementation should satisfy:

- Existing summary metrics still render and pass existing tests.
- New metrics are calculated in `CatalogStore.summary()` from existing catalog fields.
- The dashboard top-right panel shows action metrics before general inventory metrics.
- Zero action counts do not visually scream; nonzero action counts use the orange alert style.
- Platform gaps show one aggregate card plus per-platform subcounts.
- Auction due includes expired auctions as action items.
- Tests cover the new summary calculations and template labels.
- No external marketplace APIs are introduced.
- No self-hosted buyer marketplace features are introduced.

## Known risks

- Stale drafts use `created_at`, so an old item edited today still looks stale until `updated_at` exists.
- Conversion rate is catalog-level and approximate until true `listed_at` or status history exists.
- Manual response/watch/platform statuses can be stale; the metrics are only as accurate as manual updates.
- More cards can make the right panel tall. If it becomes noisy, keep action cards visible and move health metrics into a collapsed `More metrics` block.
