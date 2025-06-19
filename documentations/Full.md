Below is a tab-by-tab breakdown of every major visualization in the codebase. For each visualization you’ll find:

1. **Data**: what source and fields we used
2. **How & Why**: how we built it and our rationale
3. **Alternatives**: other ways to show the same insight, with pros/cons
4. **Our Advantage**: what makes our choice superior for this scenario
5. **Preprocessing**: any filtering, aggregation, assumptions or calculations
6. **Extra Notes**: potential questions or gotchas

---

# 🏟️ Match Analysis Tabs (in `match_overview_simple.py`)

## 📍 Shot Maps

### 1. Data

- Event-level data from StatsBomb via `load_match_data(match_id)`
- Filtered for events where `type == "Shot"`
- We extract `location` (x,y), `shot_statsbomb_xg`, and `shot_outcome`.

### 2. How & Why

- We draw a custom soccer pitch (Plotly shapes) and overlay shot markers.
- Marker **size** ∝ xG, **color/symbol** by outcome, **hover** shows xG & outcome.
- Rationale: scatter on pitch gives exact spot and quality of each attempt.

### 3. Alternatives

- Heat-map of shot density
  - pro: highlights shooting “hotspots”
  - con: loses individual shot quality and outcome detail
- Zonally aggregated bar chart (“shot zones”)
  - pro: easily comparable across predefined zones
  - con: arbitrary zones may hide nuances
- Temporal shot chart
  - pro: shows when shots occurred
  - con: loses spatial exactness

### 4. Our Advantage

- Precise spatial & quality representation (xG)
- Intuitive color/symbol encoding of outcome
- Interactive hover for player-level detail

### 5. Preprocessing

- Filter `events_df[type=="Shot"]`
- If `team_name` or `player_name` specified, further filter by nested dict lookup
- Extract coordinate arrays, xG, outcomes

### 6. Extra Notes

- We explicitly do **not** show own goals on shot map (they aren’t recorded as shots).
- Marker size scaling uses a linear transform for visibility.

---

## 🔗 Pass Networks

### 1. Data

- All successful passes (`type=="Pass"` & `pass_outcome` is NaN) for one team
- Related substitutions to map subbed-on players back to originals.

### 2. How & Why

- Compute pairwise pass counts between players → graph edges
- Compute average field position for each player → graph nodes
- Edge width∝frequency, node size∝total involvement (passes in+out), position labeled by role acronym.
- Rationale: network graph reveals team shape & passing relationships.

### 3. Alternatives

- Chord diagram
  - pro: elegant circular layout
  - con: spatial relationship (field shape) lost
- Heat map of passes between zones
  - pro: highlights zones rather than individuals
  - con: no per-player insight
- Sankey diagram
  - pro: clear flows
  - con: linear layout not spatial

### 4. Our Advantage

- Nodes positioned on pitch → intuitive spatial tactics
- Interactive hover reveals exact counts & sub info
- Distinct node shapes/colors mark substitutes vs starters

### 5. Preprocessing

- Filter events, map substitutions
- Build list of (`passer`, `recipient`) and count frequencies
- Compute average x,y per player (including sub replacements)
- Threshold edges at 15% of max pass frequency to declutter

### 6. Extra Notes

- Dynamic thresholding ensures small messy links are pruned.
- Substitution mapping preserves continuity of passing stats.

---

## 📈 xG Timeline

### 1. Data

- All shots sorted by minute; `shot_statsbomb_xg`, `shot_outcome`.
- Also “own goal” events from `Own Goal For/Against` types.

### 2. How & Why

- Cumulative sum of xG over match minutes plotted as line for each team
- Vertical dashed lines + annotations mark goals & own-goals.
- Rationale: shows match momentum and whether score matches chance creation.

### 3. Alternatives

- Rolling xG difference chart
  - pro: directly shows advantage swings
  - con: less intuitive for raw momentum build
- Bar chart of xG per interval
  - pro: quantifies each period
  - con: loses continuous story

### 4. Our Advantage

- Continuous cumulative view is familiar & easy to read
- Goal markers annotated in-chart, no separate legend needed
- Handles simultaneous goals/own-goals elegantly

### 5. Preprocessing

- Filter shots, sort by `minute`
- cumsum of `shot_statsbomb_xg` per team
- Insert start (0,0) and end (90, last_xg) points for full axis coverage
- Process related events to capture own-goals without duplication

### 6. Extra Notes

- Handles multiple goals at same minute with offsets
- Own goals require scanning related event IDs.

---

## 📊 Match Stats (Side-by-side bars)

### 1. Data

- Counts from `events_df`: shots, fouls, goals, own goals, etc.
- Computed xG sums and shot types.

### 2. How & Why

- For each metric (e.g. Shots, xG, Pass Accuracy), draw two horizontal bars side-by-side
- Value labels inside bars, color coded by winner/loser.
- Rationale: immediate side-by-side quantitative comparison.

### 3. Alternatives

- Radar chart
  - pro: multi-variate in single spider
  - con: prone to misinterpretation, not precise
- Table
  - pro: exact numbers
  - con: no visual emphasis

### 4. Our Advantage

- Bars are intuitive, length proportional
- Color duality signals advantage at a glance
- Narrative description accompanies the chart

### 5. Preprocessing

- Compute home vs away metrics with dict lookups & Pandas filters
- Derive pass accuracy = successful/total passes ×100
- Compute possession via pass share

### 6. Extra Notes

- Designed to fit in fixed-width container.
- Alternate visualizations are documented in info pop-ups.

---

## 🎯 Key Events

### 1. Data

- Events of types: Shot goals, own goals, cards, fouls, substitutions from `events_df`.

### 2. How & Why

- Build chronological list of event‐dicts with `minute`, `type+icon`, `team`, `player`, `description`
- Render as styled cards in scrollable panel.
- Rationale: narrative timeline of match turning points

### 3. Alternatives

- Gantt-style timeline
  - pro: relative spacing clear
  - con: more complex to implement in Dash & limited vertical real estate
- Event scatter on minute axis
  - pro: compact
  - con: loses rich textual description

### 4. Our Advantage

- Full descriptions, team-color backgrounds, icons → immediately understandable
- Scrollable for many events

### 5. Preprocessing

- Consolidate `Shot`→Goal events, map own goals via related IDs
- Detect cards via multiple columns (`bad_behaviour_card`, `type` in `Yellow Card`, etc.)
- Foul and substitution events appended

### 6. Extra Notes

- Robust card detection attempts multiple columns to cover StatsBomb schema variations.

---

## 💰 Formations (Matplotlib + mplsoccer)

### 1. Data

- Starting XI and tactics from sbopen (`event`, `tactics`), ball receipts for heatmap.

### 2. How & Why

- Use `mplsoccer.VerticalPitch.formation` to draw nominal formation
- Overlay KDE‐based heatmaps of actual ball receipts per position
- Player name labels beside each KDE subplot
- Rationale: compares nominal shape vs real positional tendencies

### 3. Alternatives

- Static diagram of shapes only
  - pro: simple
  - con: no movement patterns
- Full tracking heatmap
  - pro: precise movement
  - con: not available in StatsBomb event data

### 4. Our Advantage

- Combines official formation graphic with real event-based density
- Vertical layout conserves horizontal space

### 5. Preprocessing

- Merge `event` & `tactics` on starting XI event ID
- Filter receipts only for starters, map 3+ word names to first+last
- Compute KDE for each position

### 6. Extra Notes

- Formation offsets defined per formation to avoid subplot overlap.
- Falls back gracefully if no starting XI or receipt events.

---

# 📊 Tournament Overview Tabs (`tournament_layout`)

## ⚽ Goals Analysis

1. **Data**: match‐level summary from `load_euro_2024_matches()`.
2. **Viz**: horizontal bar of total goals by team, color gradient by value; grid of top 5 teams cards.
3. **Alternatives**: pie chart (loses ranking), table (no visual emphasis).
4. **Advantage**: clear ranking, hover shows goals/match ratio.
5. **Preproc**: aggregate home+away goals, compute goals/match.
6. **Notes**: top teams highlighted below chart.

## 🏆 Team Performance

1. **Data**: standings from same match dataframe.
2. **Viz**: Plotly Table with colored cells + stacked‐bar W/D/L for top 8.
3. **Alternatives**: conventional HTML table (less style), line chart of points (no W/D/L breakdown).
4. **Advantage**: color‐coded columns speed pattern recognition; stacked bars show distribution.
5. **Preproc**: compute W/D/L, GF/GA, goal difference, points, win%.
6. **Notes**: interactive sorting possible in Dash table too.

## 📈 Match Insights

1. **Data**: entire competition matches.
2. **Viz**: histogram of goals/match, histogram of goal differences, pie of outcomes.
3. **Alternatives**: boxplots (hides count), violin (too academic).
4. **Advantage**: histograms show frequencies, pie communicates proportions.
5. **Preproc**: derive total_goals, goals_diff, boolean flags, percentages.
6. **Notes**: mean line annotated in goals histogram.

## 🔎 Top Performers _(players-tab placeholder)_

1. **Data**: placeholder lists of scorers/keepers.
2. **Viz**: overlaid bar (goals+assists), dual‐axis keeper chart, radar chart.
3. **Alternatives**: simple lists, static images.
4. **Advantage**: interactive hover, multi‐dimensional radar.
5. **Preproc**: N/A for demo; in production would query event/lineup.
6. **Notes**: color gradients encode magnitude.

---

# 🔎 Event Explorer (`event_explorer.py`)

## 🎛️ Event Summary Stats

1. **Data**: filtered `events_df` by team/match/type/player/time.
2. **Viz**: four cards (Total Events, Players Involved, Most Common Event, Time Window).
3. **Alternatives**: small table (denser, less visual).
4. **Advantage**: big numbers, color accents make summary pop.
5. **Preproc**: apply dropdown & slider filters; compute `.value_counts()` etc.
6. **Notes**: filters chain consistently across summary, timeline, table.

## 📈 Event Timeline

1. **Data**: same filtered DataFrame, grouped by `(minute, type)` to count events.
2. **Viz**: multi‐line Plotly Express chart of event frequency over time, one line per type.
3. **Alternatives**: stacked‐area chart (visually busy), bar chart (too granular).
4. **Advantage**: simple lines, unified hover shows all types at a minute.
5. **Preproc**: groupby+size, reset_index; ensure empty state handles gracefully.
6. **Notes**: slider range 0-120, but typical matches end at 90.

## 📋 Event Data Table

1. **Data**: same filtered DataFrame.
2. **Viz**: Dash DataTable with native sort/filter, CSV export button.
3. **Alternatives**: custom HTML table (no export), Pandas DataFrame.to_html (static).
4. **Advantage**: interactive, performant up to 1,000 rows, immediate export.
5. **Preproc**: flatten nested dicts (`team`, `player`, `position`, `location`).
6. **Notes**: column selection tailored for key fields.

---

# ⚡ Tactical Analysis (`tactical_view.py`)

## 📋 Formation Analysis

1. **Data**: first 15-minute receipts + starting XI from StatsBomb via sbopen.
2. **Viz**: Matplotlib pitch by mplsoccer; scatter of average x,y per starter; name labels.
3. **Alternatives**: network of positions (no KDE), heatmap grid (no formation lines).
4. **Advantage**: classic soccer-pitch background + exact avg positions, high‐res static PNG.
5. **Preproc**: filter `minute ≤15`, groupby `player` mean coords, lookup `position` name.
6. **Notes**: fallback if no data, text effect with path_effects for label outline.

## 🛡️ Defensive Actions

1. **Data**: events where `type` in [Tackle, Interception, Block, Clearance, Foul Committed].
2. **Viz**: binned 2D heatmap on pitch via `pitch.bin_statistic` + `heatmap`.
3. **Alternatives**: scatter of individual events (too noisy), hexbin (similar but less control).
4. **Advantage**: smoothed density, normalized bins emphasize activity zones.
5. **Preproc**: drop NaNs, custom blue colormap, normalize count.
6. **Notes**: adds colorbar, handles zero‐data gracefully.

## ⚔️ Attacking Patterns

1. **Data**: final‐third events (`x>80`) of types Shot, Dribble, Pass.
2. **Viz**: scatter per type with distinct colors & legend on truncated pitch (80–120).
3. **Alternatives**: flow lines from origin to end (complex), small multiples by event (many panels).
4. **Advantage**: simple, highlights final‐third activity clusters.
5. **Preproc**: filter `x>80`, by type.
6. **Notes**: pitch clipped to final third with axis limits.

## 🎯 Set Pieces

1. **Data**: passes where `pass_type` in [Corner, Free Kick, Throw-in].
2. **Viz**: Matplotlib bar chart of counts by set-piece type.
3. **Alternatives**: pie (loses absolute counts), line chart over time (diff metric).
4. **Advantage**: direct bar labels, custom colors, grid, arrowed value labels.
5. **Preproc**: map nested `pass_type` dict to string, count `.value_counts()`.
6. **Notes**: bars have edge color for emphasis; handles missing data.

## 🔍 Secondary Analysis

### 1. Pass Length Distribution

- **Data**: successful passes with valid `x`,`y`,`pass_end_x`,`pass_end_y`.
- **Viz**: histogram of Euclidean distances, 20 bins.
- **Why**: understand directness vs short buildup.
- **Preproc**: compute √((dx)²+(dy)²).

### 2. Event Activity Timeline

- **Data**: all team events, grouped by minute.
- **Viz**: line+marker Plotly chart, custom hover shows breakdown per type.
- **Why**: spot busy minutes & breakdown.
- **Preproc**: groupby minute, build HTML hover strings.

## ⚖️ Team Comparison

1. **Data**: home & away team events, metrics: passes, pass%, shots, shot%, dribbles, dribble%, tackles, interceptions, fouls.
2. **Viz**: mirrored horizontal bars: counts on ± axis, percentages with hatch pattern.
3. **Alternatives**: side-by-side bar groups (less compact), radar (harder to read).
4. **Advantage**: symmetrical layout compares two teams easily; clear legend and center zero axis.
5. **Preproc**: count & compute percentages, handle missing duel‐type tackles, set reasonable defaults.
6. **Notes**: dynamic text formatting, custom tickvals for ± axis, top title includes result text.

---

Each of these visualizations is backed by careful preprocessing, leverages both Plotly (for interactivity) and mplsoccer/Matplotlib (for publication-quality static images), and was chosen to maximize clarity, spatial intuition, and tactical insight. The code also includes fallbacks and graceful error handling for missing data, and in-app documentation (ℹ️ pop-ups) to explain the “why” behind each choice.
