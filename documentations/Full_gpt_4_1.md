# Detailed Data Visualization Explanation & Design Rationales (Tab-wise)

This document provides a **deep dive into the thought process, choices, preprocessing, and design for each visualization** in your Euro 2024 analytics app. For **each major dashboard/tab/visualization**, you get:

1. **Data Source and Description**
2. **Why This Visualization Was Chosen**
3. **Alternative Visualizations Considered (with pros/cons)**
4. **Why Our Choice is Best**
5. **Preprocessing, Calculations, Assumptions**
6. **Potential Questions/Considerations**

> The same structure is followed for:
>
> - **Match Overview (with its subtabs)**
> - **Tournament Overview (tabs in overview)**
> - **Event Data Explorer**
> - **Tactical View**

---

# 1. Match Overview (Tabs: Shot Maps, Pass Networks, xG Timeline, Match Stats, Key Events, Formations)

---

## Tab: **📍 Shot Maps**

### 1. What was the data

- **Source:** StatsBomb event data, loaded per-match.
- **Filtered:** Only events with `type == "Shot"`, separated by `team` (home/away).
- **Fields used:** `[x, y]` (shot location), `shot_outcome`, `shot_statsbomb_xg`, `player`, `team`.

---

### 2. How we achieved this visualization & why this

- **Type:** Overlaid soccer pitch with scatter plot of shots.
- **Encodings:**
  - **Position:** (x, y) on pitch
  - **Circle Size:** Proportional to xG (expected goal value)
  - **Color/Symbol:** Coded by shot outcome (Goal, Saved, Blocked, etc.)
  - **Hover:** Player, xG, outcome
- **Why:** Gives immediate, intuitive feel of:
  - Where shots were taken from (zones, distances)
  - Shot quality (high-xG vs speculative)
  - Outcome immediacy (which shots led to goals)
  - Attacking tendencies (clustered or spread)
- **Interactive:** Allows hover, zoom, filter (for player/team if desired).

---

### 3. Alternatives Considered

| Alternative        | Pros                                | Cons                                  |
| ------------------ | ----------------------------------- | ------------------------------------- |
| Heatmap            | Shows density/hot zones             | Loses detail (who shot, outcome, xG)  |
| Table/Stats        | Exact details; sortable             | No spatial/visual intuition           |
| Shot Zones\*\*     | Good for aggregate tactical pattern | Hides granularity/individual attempts |
| Temporal Shot Plot | When in match shots were taken      | Not spatial                           |

---

### 4. Why is Shot Map Best?

- **Combines spatial, qualitative, and outcome info in one view.**
- Easily compare both teams (side by side).
- Immediate context for dangerous chances vs speculative.
- Industry standard for post-match analysis.

---

### 5. Preprocessing

- **Load event data per match.**
  - Unpack `location` into numerical x, y.
  - Filter `type == "Shot"`.
  - Handle `shot_outcome` as dict/string.
- **Assumptions:**
  - All coordinates are on same pitch scale.
  - Only non-null shots shown.
- **Logic:**
  - Circle size = f(xG). Special gold color/emoji for goals.
  - Own goals are **not shown** (not recorded as shots in original data).

---

### 6. Important Considerations

- **Why do some shots have zero xG?** (e.g. penalties in some data)
- **Why not show own goals?** (Not in 'Shot' events; can explain if asked.)
- **What about clustering?** (Why not heatmap? Heatmap is available as an advanced feature.)

---

---

## Tab: **🔗 Pass Networks**

### 1. What was the data

- **Source:** StatsBomb events per match.
- **Filtered:** Only events where `type == "Pass"` **and** where `pass_outcome` is `null` (i.e. successful).
- **Fields:** `[x, y]` (start position), `player`, `pass_recipient`, teams, position, substitution info.

---

### 2. Visualization approach & rationale

- **Type:** Soccer pitch overlay, Network graph.
- **Encodings:**
  - **Nodes:** Players. Placement = avg (x, y) of pass actions.
  - **Node Size:** Passing involvement (passes made + received).
  - **Node Color:** Player's position.
  - **Node Shape:** Different for substituted players.
  - **Edges (lines):** Pass connections, thickness proportional to frequency.
  - **Interactivity:** Hover for role/pass counts; distinguish frequent partnerships.
- **Why:**
  - Reveals shape ("formation in possession"), central playmakers.
  - Visualizes tactical structure and dominant connections.

---

### 3. Alternatives Considered

| Alternative       | Pros                            | Cons                                 |
| ----------------- | ------------------------------- | ------------------------------------ |
| Heatmap (touches) | Shows zones of team presence    | Cannot see passing 'links'/structure |
| Chord diagram     | Highlights pass pairs/frequency | Not spatial, no pitch context        |
| Table matrix      | Precise pass counts by pair     | Hard to read, no formation           |
| Static formation  | Shows positions                 | No info on relationships             |

---

### 4. Why is Network Graph Best?

- It uniquely **shows both team structure, and the flow of play** (who combines with who).
- Encodes **roles, substitutions, and involvement** in a single, visual, spatial way.
- Used professionally (e.g., The Athletic, StatsBomb).

---

### 5. Preprocessing

- **Parse and unpack nested player and recipient info.**
- **Correct for substitutions** (map minutes played, merge replaced players if needed).
- **Average positions** based on actions, not a-priori lineup.
- **Threshold for edge** (line) inclusion: only show frequent pass pairs (for clarity).
- **Color by position**: role abbreviations used.
- **Assumptions:**
  - Pitch coordinates normalized.
  - If a player substituted on/off, their connections are tracked for their stint.

---

### 6. Important Considerations

- **Why label with position, not full name?** (Tactical focus, crowding prevention, better abstraction.)
- **How to interpret node/edge size?** (Node: involvement; Edge: pass frequency.)
- **What about failed passes?** (Not shown to avoid clutter.)
- **What does it say about tactics?** (Who is ball-player, width, build-up patterns.)

---

---

## Tab: **📈 xG Timeline**

### 1. What was the data

- **Source:** Per-match StatsBomb events.
- **Filtered:** `type == "Shot"` for each team.
- **xG:** `shot_statsbomb_xg`
- **Goal info:** `shot_outcome` == 'Goal', plus own goal special event parsing.
- **Timeline:** By `minute` of event.

---

### 2. Why this visualization?

- **Type:** Line chart (cumulative).
- **Encodings:**
  - X-axis: Match minute
  - Y-axis: Cumulated xG
  - Color: By team
  - Dotted verticals/annotations: Actual goals (who, when), own goal handling
  - Hover: Shows value at each shot/time
- **Why:**
  - Shows **when and how much threat was created**.
  - Compares quality vs actual result (over/under-performing).
  - Reveals big moments: sudden spikes = big chance, penalty, clustered shots.

---

### 3. Alternatives Considered

| Alternative          | Pros                             | Cons                                      |
| -------------------- | -------------------------------- | ----------------------------------------- |
| Bar chart per minute | Good for burstiness              | Hides accumulation, not easily comparable |
| xG Differential Line | Shows direct gap between teams   | Less intuitive if both are low/high       |
| Step chart           | More literal for cumulative data | Line chart is standard, easier flex       |

---

### 4. Why cumulative line chart is best

- **Directly encodes "momentum" and comparative attacking output.**
- Lets you see swings, periods of dominance, and performance vs. expected.
- Easily overlay both teams for comparison.

---

### 5. Preprocessing, assumptions

- **Sort shots by minute.**
- **Cumulative sum per team.**
- **Careful annotation of actual goals (shots with 'Goal' outcome, and own goals parsed from special events).**
- **If xG fields are missing, zero is assumed.**
- **Edge cases:** Some shots may not have xG (very rare), handled as 0.

---

### 6. Further notes

- **Why show both xG & result?** (Highlights teams playing "above/below xG" – luck or finishing.)
- **What about non-shot goals (own goal)?** Careful to annotate both teams properly.
- **What if asked "Is xG fair?"** (Cite professional adoption and predictive power.)

---

---

## Tab: **📊 Match Stats**

### 1. What was the data

- **Source:** StatsBomb event data, per-match.
- **Aggregates calculated:** For both teams, for these stats:
  - Shots, shots on target, passes (successful/failed), possession (from pass counts), xG, goals.

---

### 2. Why this visualization?

- **Type:** Side-by-side bar (horizontal) chart.
- **Encodings:**
  - Two-colored bars for each stat: home vs away, with direct numeric labels inside.
- **Why:**
  - Allows at-a-glance, immediate comparison of both efficiency (xG, passes), effectiveness (shots, shots OT), and result (score).
  - Color-encoding by team for easy reading.

---

### 3. Alternatives Considered

| Alternative     | Pros                                  | Cons                                             |
| --------------- | ------------------------------------- | ------------------------------------------------ |
| Table           | Exact numbers, sortable               | Less intuitive for difference                    |
| Radar/spider    | Multi-variate comparison in one chart | Not classical for match-by-match, can be misread |
| Difference bars | Quick to see deltas                   | Loses individual value context                   |

---

### 4. Why horizontal bar with color win

- **Clear, familiar, immediately graspable by all skill levels.**
- Encodes both actual and relative value – if home and away are close, bars will be nearly even.
- Easily extensible for other stats.

---

### 5. Preprocessing

- **Count event types per team.**
- **Successful/failed passes:** Use `pass_outcome` (null = successful).
- **Possession (approximate):** by share of total passes.
- **xG:** Sum shot xG per team.
- **Edge cases:** If division by zero arises (rare, e.g., 0 passes for a team), handled with default 0%.

---

### 6. Further questions

- **What does this NOT tell you?** (Doesn't show sequence, only overall comparison.)
- **Why not use more 'advanced' stats?** (Principle of clarity, stat coverage.)

---

---

## Tab: **🎯 Key Events (Timeline)**

### 1. What was the data

- **Source:** All Events for the match (not just shots or passes).
- **Captured:**
  - Goals
  - Own Goals (special event)
  - Cards (Yellow/Red/Second Yellow)
  - Penalties (as fouls + penalty indicator)
  - Substitutions
  - Fouls
- **Fields:** `minute`, `type`, `team`, `player`, description.

---

### 2. Visualization tactic

- **Type:** Chronological timeline (list with minute, color-coded, icons).
- **Why:**
  - Follows real match broadcast/narrative.
  - Color/emoji used for event importance & instant recognition.
- **Encodings:**
  - Color: team colors.
  - Icon: event type.
  - Description: player names, specifics.

---

### 3. Alternatives Considered

| Alternative          | Pros                        | Cons                                   |
| -------------------- | --------------------------- | -------------------------------------- |
| Gantt/timeline chart | Good for time visualization | Hard to read with many events, clutter |
| Table (by type)      | Group all goals, etc        | Loses chronological/story flow         |
| Pitch map            | Where events occurred       | Not primary for event narrative        |

---

### 4. Why (styled) chronological list is best

- **Mirrors how fans/media experience matches ("minute 10: goal, 13: yellow card…")**
- Allows for hover, flexible styling per event, minimal learning curve.

---

### 5. Preprocessing

- **Extensive:**
  - Parse nested player, team.
  - Parse own goals (using related_events links).
  - Distinguish fouls, cards by column presence & card type.
  - Compose description dynamically depending on which columns are present.
  - Special icon for substitutions (replacement on for replaced).
- **Assumption:** If fields missing/ambiguous, default to 'Unknown'.

---

### 6. Key considerations

- **Edge cases:** Double events at same minute (handled by vertical stacking).
- **Why not plot on pitch?** Key events are best read sequentially.
- **What if no events of a type?** (e.g., no cards – indicated in summary.)

---

---

## Tab: **💰 Formations**

### 1. What was the data

- Uses **StatsBomb open data**: events + tactics frames.
- **Starting 11 (from special event), mapped to position on pitch**.
- **Player names, position id, formation type.**
- **Merges in position heatmaps (kdeplot of actual locations per player).**

---

### 2. Visualization strategy

- **Type:** Soccer pitch formation plot (mplsoccer), heatmap per position/role.
- **Encodings:**
  - Starting position markers ("formation lines").
  - Heatmap overlay: range of movement per player.
  - Text: Position abbreviation and player name (multi-line for long names).
- **Why:** Gives both base shape (coach's intent) AND "average"/range of actual player behavior over the match.

---

### 3. Alternatives Considered

| Alternative        | Pros                                      | Cons                                  |
| ------------------ | ----------------------------------------- | ------------------------------------- |
| Static formation   | Shows tactical 'lineup' as in lineupsheet | Misses player movement variation      |
| Individual heatmap | Deep per-player insight                   | Loses overall team structure          |
| x,y average only   | Quick summary, minimal clutter            | Hides variation, poor for fluid teams |

---

### 4. Why formation + player heatmap beats alternatives

- **Directly links tactical intention to actual player behaviors.**
- Reveals e.g. asymmetric fullback tendencies, how wide wingers really play etc.

---

### 5. Preprocessing, logic, assumptions

- **Extract starting 11 from event/tactics open frame.**
- **For each player, extract Ball Receipt events to sample positions.**
- **Merge so only positions for those 11 shown.**
- **KDE plot for movement range.**
- **Abbreviate names for display.**
- If formation not in offset dictionary, use default.

---

### 6. Additional notes

- **What about substitutions?** (Not shown here, focus on starting shape.)
- **Why `.kdeplot` not histogram?** (Avoids blocky look, more true to movement style.)

---

# 2. Tournament Overview Tabs

---

## Tab: **⚽ Goals Analysis**

### 1. Data

- **Source:** Match results – not event-level, but per-match summary (`home_score`, `away_score`).
- **Aggregated per team:** goals for (home and away), goals conceded, matches played, clean sheets, etc.

---

### 2. Visualization and reasoning

- **Bar chart:** Horizontal, "Goals Scored per Team".
- **Supplemented:** Metric cards for top teams.
- **Why:**
  - Easiest to compare raw scoring output of all teams at once.
  - Hover provides per-match rate.
  - Top teams called out with cards for key stats (goals, goals/match, clean sheets).

---

### 3. Alternatives Considered

| Alternative   | Pros                         | Cons                                       |
| ------------- | ---------------------------- | ------------------------------------------ |
| Ranking table | Readable, sortable           | Less visual, harder to compare at a glance |
| Spider/radar  | Fit for multi-metric summary | Not ideal for one metric focus             |

---

### 4. Rationale for horizontal bar

- Intuitive; sorted order makes ranking, differences pop.
- Scalable (20+ teams still readable).

---

### 5. Preprocessing

- **Aggregate home and away stats.**
- **Calculate clean sheets** per team (must extract 0 against from both home and away perspective).
- **Compute per-match averages.**

---

### 6. Possible exam questions/issues

- **Why per team not per player?** (Team trend focus. Player stats in other tab.)
- **Why not 'per 90'?** (Direct scoring totals align with tournament reporting convention.)

---

---

## Tab: **🏆 Team Performance**

### 1. Data

- **Source:** Match summary results + derived info.
- **Stats calculated:** Points (W/D/L), goals for/against, matches, win %, avg goals, etc.
- **Match-by-match breakdown for sparkline/timeline if needed.**

---

### 2. Visualization selection

- **Standings Table:** Standard points table (color-coded).
- **Stacked Bar Chart:** W/D/L distribution for top teams.
- **Why:**
  - Recreates league-table familiar to all audiences.
  - Stacked bars make it quick to see which teams are more consistent, which draw frequently, etc.

---

### 3. Alternatives

| Alternative | Pros                                                | Cons                           |
| ----------- | --------------------------------------------------- | ------------------------------ |
| Win% only   | Quickly identifies top sides                        | Hides number of matches, draws |
| Spider      | See multi-factor, but hard to read standing context |                                |

---

### 4. Why this is best

- **Table is universal reference; colors highlight strength (win, draw, loss), easy to interpret.**
- **Stacked bars clearly show team styles/trends.**

---

### 5. Preprocessing

- **Calculate all metrics per team.**
- **Sort by points then win%.**
- Deal with cases where teams have played different matches (group phase vs knockout).

---

### 6. Other discussion points

- **Why W/D/L percentages not absolute?** (Normalize for games played.)
- **How does this compare to FIFA reporting?** (Same structure.)

---

---

## Tab: **📈 Match Insights**

### 1. Data

- **Source:** Match summary for the whole tournament.
- **Metrics:** Total goals/match, goal difference, win/draw distribution, clean sheets.

---

### 2. Visualization

- **Histograms:** Goals per match, goal difference.
- **Pie chart:** Result type breakdown.
- **Why:**
  - Describes competitiveness (many draws/tight games vs. high scoring blowouts).
  - Pie gives "at a glance" feel for balance in home vs away vs draw.
  - Histograms make outliers/apparent parity visible.

---

### 3. Alternatives

| Alt      | Pros              | Cons                  |
| -------- | ----------------- | --------------------- |
| Box plot | Summarizes spread | Not intuitive for all |
| Strip    | High detail       | Cluttered             |

---

### 4. Why we did it

- **Histograms are the go-to for summary, pie charts for high-level result share.**
- More intuitive for general audience.

---

### 5. Preprocessing

- **Aggregate all matches, calculate differences and totals as new columns.**

---

### 6. Further insights

- **Why not split 'no score draws'?** Simplicity; can add on demand.
- **What does this say about playing styles?** Indirect, but important as intro context.

---

# 3. **Event Data Explorer Tab**

### 1. Data

- **Source:** All per-match events; complete event log.
- **User filterable by team, match, event type, player, time window.**

---

### 2. Visualization

- **Event Timeline plot:** Line (event count over time), color-coded by type.
- **Summary cards:** Total events, unique players, most common event, time window.
- **DataTable:** Flat-tabular event data (sortable/filterable), exportable.

---

### 3. Alternatives

| Alt                                     | Pros                  | Cons                            |
| --------------------------------------- | --------------------- | ------------------------------- |
| Heatmap                                 | Trends by minute/type | No context/individuals          |
| Sequential timeline (like Twitter feed) | Direct narrative      | Not good for frequency/patterns |

---

### 4. Why this approach

- **Combines detailed analysis (table) with pattern recognition (timeline)**.
- Fast, responsive for exploratory analysis.

---

### 5. Preprocessing

- **No aggregation unless filtered.**
- Special flattening: nested dict fields (team, player, position, location).
- Filtering is all in-memory operations – only for currently shown columns.

---

### 6. Key issues

- **What if field missing?** (All handled as 'Unknown'.)
- **How to compare matches/players fairly?** (Filters must match use case.)
- **What about export errors?** (Fail gracefully; reset filter.)

---

# 4. **Tactical View (Advanced Team Analysis)**

### 1. Data

- **Source:** Full event data for match + match summary.
- **Focus:** All team events, filtered by team and time.
- **Analysis options:** Formation, defensive, attacking, set pieces.

---

### 2. Visualization for each analysis type

#### a. **Formation (first 15min)**

- **Pitch Map:** Scatter of avg (x, y) positions per player, color by role.
- **Rationale:** Shows _operational_ (vs nominal) shape at start – crucial for tactical insight.

#### b. **Pass Network**

- **(If enabled):** Pitch network as above; see Pass Networks above.

#### c. **Defensive Heatmap**

- **Heatmap:** Density of defensive actions (tackles, interceptions, blocks, fouls)
- **Why:** Reveals pressure zones, compactness, weak points.

#### d. **Attacking Patterns**

- **Final Third Map:** Only events with x > 80 (final third of pitch).
- **Markers:** Shots (red), Dribbles (orange), Passes (blue).
- **Why:** Shows spatial approach/lane preference.

#### e. **Set Piece Usage**

- **Bar Chart:** Count of Corners, Free-Kicks, Throw-ins taken.
- **Shows**: Strategic set piece reliance.

---

### 3. Alternatives (for each)

| Alt for (a) | Pros                     | Cons                   |
| ----------- | ------------------------ | ---------------------- |
| Heatmap     | Density of movement      | Can't see structure    |
| Box plots   | Min/max/median positions | Not visual for tactics |

| Alt for (c) | Pros             | Cons                  |
| ----------- | ---------------- | --------------------- |
| Points only | Exact locations  | Hard to sense density |
| Table       | Specific numbers | No spatial insight    |

---

### 4. Why our selections

- Each chart optimized for its tactical area (network for interplay, heat for press, markers for attack, bar for set pieces).
- **Visual-first for coaches/scouts, but with raw data always accessible.**

---

### 5. Preprocessing

- **Role-based color coding** (some manual mapping if position names vary).
- **Drop invalid points (e.g. null coords).**
- **Final third filter for attack; time filter for 'early' formation.**
- **Set Piece detection:** Based on pass_type field.

---

### 6. Further issues/questions

- **Formation: early vs full match?** Often meaningful only at start—or on tactical shifts.
- **Defensive heatmap: all types or focus (e.g., only tackles)?** Optionally filterable.
- **Attacking: are assists tracked?** Yes (but this plot is location/volume, not sequence).
- **Set Piece: can we analyze conversion?** For future extension.

---

# General Design and Data Considerations

- **Data source:** All data comes from the StatsBomb event-feed; all preprocessing is reproducible.
- **Caching:** For speed/responsiveness, event and match frames are cached.
- **Preprocessing in code, not in storage:** Ensures up-to-date calculations per user selection.
- **User-interaction:** Filters and options directly impact what’s visualized—encourages exploration and "what if" analysis.
- **Code structure:** Clean separation of data (loaders), logic/preprocessing, and plotting/visual function.
- **Transparency:** All tables are exportable, hover reveals all fields—no “magic”.

---

# If you have to **justify or defend** choices

- Visual-first for pattern recognition.
- Overlay numerical details for precision.
- Borrow best-practice tools from professional analysis circles.
- Combine multiple views for a "360 degree" match/tournament analysis.
- All statistical methods are standard; all calculations fully reproducible from raw.

---

**This document can serve as a deep readme, oral defense answer script, or onboarding guide for anyone contributing or reviewing your soccer analytics dashboard project.**
