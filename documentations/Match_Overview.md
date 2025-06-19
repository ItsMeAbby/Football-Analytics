# Match Overview – Detailed Visualization Breakdown

Below is a breakdown of each visualization in the **Match Analysis** (“Match Overview”) tab. For each, we cover:

1. **Data**
2. **Approach & Rationale**
3. **Alternative Visualizations (Pros & Cons)**
4. **Why Our Visualization Is Better**
5. **Preprocessing & Assumptions**
6. **Other Important Notes**

---

## 1. Shot Maps

### 1. Data

- `events_df` filtered to rows where `type == 'Shot'`.
- For each shot:
  - `.location` → `(x, y)`
  - `.shot_statsbomb_xg` → xG value
  - `.shot_outcome` → outcome name (“Goal”, “Saved”, etc.)

### 2. Approach & Rationale

- **Scatter plot** on a full-size soccer pitch drawn with Plotly shapes.
- Shots are plotted at their exact `(x,y)` coordinates.
- **Circle size** ∝ xG (higher xG = bigger circle).
- **Color & symbol** encode shot outcome; goals use a gold circle and “⚽” in hover text.
- Chosen to convey both spatial (where) and qualitative (how good) aspects of every attempt.

### 3. Alternatives

- **Heatmap of shot density**  
  – Pros: highlights “hot zones” of shooting activity  
  – Cons: loses individual-shot context (xG/outcome)
- **Hexbin aggregation**  
  – Pros: smooths noise, good for large datasets  
  – Cons: coarse bins hide precise locations
- **Shot–time timeline**  
  – Pros: shows tempo  
  – Cons: loses spatial dimension

### 4. Why Ours Is Better

- Precise: shows each shot’s exact location.
- Multidimensional: encodes xG, outcome, team, and player.
- Interactive: hover for details; legend toggles outcome categories.

### 5. Preprocessing & Assumptions

- Filter `events_df[type == 'Shot']`.
- Extract `x, y` from `.location` list.
- Fill missing xG with `0`.
- Build lists of coordinates, xG, outcomes.
- Use a fallback “No shot data available” annotation if empty.

### 6. Other Notes

- Uses Plotly’s offline (“Agg”) backend for headless rendering.
- Caches data via `@lru_cache` to avoid repeated API calls.
- Configured pitch dimensions (120×80) to StatsBomb conventions.

---

## 2. Pass Networks

### 1. Data

- `events_df` filtered to:
  - `type == 'Pass'`
  - `pass_outcome` is `NaN` (successful passes)
  - `team` matches the selected team
- Substitutions processed to map replaced players back to originals.

### 2. Approach & Rationale

- Model the team as a **graph**:
  - **Nodes** = players, placed at their average on-ball `(x,y)`
  - **Edges** = number of successful passes between two players
- **Node size** ∝ total involvement (passes made + received).
- **Edge width/transparency** ∝ pass frequency.
- Chosen to reveal formation shape, key playmakers, and link strength.

### 3. Alternatives

- **Chord diagram** (circular arcs)  
  – Pros: compact overview  
  – Cons: loses pitch context; less intuitive to map to field positions
- **Adjacency matrix**  
  – Pros: precise counts  
  – Cons: non-spatial, harder to relate to tactics
- **Heatmap of pass density**  
  – Pros: shows zones of activity  
  – Cons: doesn’t show who passed to whom

### 4. Why Ours Is Better

- Spatially grounded: you see actual pitch positioning.
- Highlights both individual influence (node size) and pairwise links (edge weight).
- Interactive tooltips deliver exact pass counts, player names, positions.

### 5. Preprocessing & Assumptions

- Build `pass_connections_list` with (`passer`, `recipient`, `passes`).
- Map substitutes back to original players via `sub_mapping`.
- Compute each player’s average `x` and `y` from all their pass events.
- Dynamically set a **minimum-pass threshold** (15% of max passes or 2).
- Normalize line widths and transparency based on pass counts.
- Position abbreviations provided via `positions_dict_acronym`.

### 6. Other Notes

- Falls back to an annotation if no passes meet thresholds.
- Caches intermediate CSV (`team_name_passes.csv`) for debugging.
- Uses Plotly for interactive zoom/pan and hover details.

---

## 3. xG Timeline

### 1. Data

- `events_df` filtered to `type == 'Shot'`.
- Own goals (`Own Goal For`/`Against`) also processed via `related_events`.

### 2. Approach & Rationale

- **Cumulative line chart** of xG vs. match minute, one line per team.
- Markers at each cumulative point; dashed vertical lines + annotations for each goal (including own goals).
- Chosen to show momentum swings and how expected-threat evolved over time.

### 3. Alternatives

- **Area chart** under cumulative line  
  – Pros: visual fill  
  – Cons: can obscure overlapping lines
- **Bar chart of xG per shot**  
  – Pros: shows individual contributions  
  – Cons: loses cumulative context
- **Rolling-average xG curve**  
  – Pros: smooth momentum  
  – Cons: hides individual events

### 4. Why Ours Is Better

- Directly compares two teams’ raw xG accumulation.
- Goal markers keep events contextualized.
- Interactive hover delivers minute & xG details, unified hover mode for comparison.

### 5. Preprocessing & Assumptions

- Sort shots by `.minute`; compute `.shot_statsbomb_xg`.
- Prepend `(0,0)` and append `(90,last_xg)` to ensure full timeline display.
- Extract and group both real goals and own goals; avoid double‐counting via `processed_event_ids`.
- Handle multiple goals in same minute by staggering annotations horizontally/vertically.

### 6. Other Notes

- Colors taken from Plotly qualitative palette.
- Hover template cleans up extra trace info.
- Layout tuned with margins for annotation room.

---

## 4. Match Statistics (Side-by-Side Bars)

### 1. Data

For home vs. away teams within the match:

- **Shots**: `len(events_df[type=='Shot'])`
- **Successful/Failed Passes**: `pass_outcome` is NaN vs. not-NaN
- **Pass Accuracy**: success ÷ total passes × 100
- **xG**: sum of `shot_statsbomb_xg`
- **Goals**: `home_score`, `away_score` from `match_info`

### 2. Approach & Rationale

- For each metric, display two **horizontal colored bars** side-by-side in a single row.
- Bars fill proportional widths to allow intuitive glance comparison.
- Numeric values overlaid in white.
- Chosen for quick side-by-side team‐vs‐team metric comparisons.

### 3. Alternatives

- **Radar chart**  
  – Pros: multi‐dim comparison in single chart  
  – Cons: less intuitive to read absolute differences
- **Table with conditional formatting**  
  – Pros: precise numbers  
  – Cons: less visual impact
- **Separate bar chart per metric**  
  – Pros: independent scales  
  – Cons: complex layout

### 4. Why Ours Is Better

- Compact, uniform layout – the reader scans down to compare.
- Encodes both absolute (numbers) and relative (bar width) comparison.
- Color‐coded per team for consistency with other tabs.

### 5. Preprocessing & Assumptions

- Straight counts and sums from `events_df`.
- Handling zero‐pass edge cases.
- Computation of pass accuracy only if total passes > 0.

### 6. Other Notes

- Responsive width and min‐width ensure readability on various screens.
- Bars have a minimum width of 5% to remain visible even for tiny values.

---

## 5. Key Events Timeline

### 1. Data

- **Goals**: `type=='Shot'` & `shot_outcome=='Goal'`
- **Own Goals**: `type=='Own Goal For'` + `related_events` lookups
- **Cards**: multiple columns (`bad_behaviour_card`, `type in ['Yellow Card','Red Card']`, `foul_committed_card`)
- **Penalties**: `foul_committed_penalty`
- **Substitutions**: `type=='Substitution'`

### 2. Approach & Rationale

- Chronologically sorted **list of colored DIVs**, one per event.
- Each shows `[minute]' [icon] description`, color‐coded by team or event.
- Chosen for clear narrative sequence of key moments.

### 3. Alternatives

- **Timeline scatter plot** along a horizontal axis  
  – Pros: spatial ordering  
  – Cons: less textual clarity
- **Gantt‐style bars** for events  
  – Pros: batch events per period  
  – Cons: overkill for point events
- **Interactive table**  
  – Pros: filter/sort  
  – Cons: loses visual team‐color context

### 4. Why Ours Is Better

- Reads like a match report but color‐coded for instant team identification.
- Emoji icons (⚽, 🟨, 🟥, 🔄) reinforce event types.
- Scrollable container handles matches with many events gracefully.

### 5. Preprocessing & Assumptions

- Deduplicate own goals via `processed_event_ids`.
- Attempt multiple strategies to discover cards/fouls across varying StatsBomb schemas.
- Limit “major fouls” to first ten to avoid overwhelming the list.
- Fallback debug entry if no card/foul columns found.

### 6. Other Notes

- Titles and tooltips (`title` attribute on DIV) deliver extra context.
- Event‐type icons chosen for rapid recognition in a long list.

---

## 6. Formations & Positional Heatmaps

### 1. Data

- SBopen output:
  - `event` table (with `type_name == 'Ball Receipt'`)
  - `tactics` table (with `type_name == 'Starting XI'`)
- Merge on `id` / `player_id` to get each starter’s formation, position, and all their ball‐receipt `(x,y)` events.

### 2. Approach & Rationale

- Use **mplsoccer**’s `VerticalPitch` to plot the nominal formation (lines) + positional grid.
- Over each player‐grid cell, overlay a **KDE heatmap** of their ball‐receipt locations.
- Annotate with player names broken into lines.
- Chosen to juxtapose nominal lineup with actual movement zones.

### 3. Alternatives

- **Static formation diagram**  
  – Pros: simple, quick  
  – Cons: no movement data
- **Individual player heatmaps** in separate subplots  
  – Pros: high resolution per player  
  – Cons: breaks tactical overview
- **Movement trace lines**  
  – Pros: path‐based clarity  
  – Cons: clutter with many touches

### 4. Why Ours Is Better

- Integrates **formation shape** with **positional intensity** in one view.
- Shows both where a player should be and where they actually operated.
- KDE level‐based shading makes “hot zones” intuitive.

### 5. Preprocessing & Assumptions

- Identify the correct `Starting XI` event by `tactics_formation`.
- Filter `Ball Receipt` events for those players only.
- Use a custom offset mapping (`get_formation_offsets`) to prevent label overlap for common formations.
- Simplify player names (first+last if ≥ 3 words).

### 6. Other Notes

- Backend uses Matplotlib “Agg”—converted to PNG base64 for embedding.
- Heatmap levels set to 100 for smooth gradients.
- Fallback annotation if no valid starting XI or receipts exist.

---

**This completes the deep dive into each visualization of the Match Overview tab.** Each plot is designed to be both **tactically informative** and **visually consistent** across the dashboard, leveraging interactivity and rich contextual encoding (size, color, position, icons) to tell the story of every match.
