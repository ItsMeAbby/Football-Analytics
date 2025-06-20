Here is a detailed explanation of the provided Python code for the sports analytics dashboard.

## `data_loader.py`

This file is responsible for fetching data from the StatsBomb API. It uses the `statsbombpy` library to get match data, event data, and competition data. The `@lru_cache` decorator is used to cache the results of functions that fetch data, which improves performance by avoiding redundant API calls.

## `preprocess.py`

This file handles data preprocessing and caching. It includes a `DataCache` class for caching processed data to a local directory. It also has functions to create match, player, and team summaries from the event data.

## `plot_utils.py`

This is the main file for creating visualizations. Here's a detailed breakdown of each visualization function:

### `create_shot_map`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered to include only "Shot" events. This data includes the location of the shot (`location`), the team that took the shot (`team`), the player who took the shot (`player`), the expected goals (xG) value of the shot (`shot_statsbomb_xg`), and the outcome of the shot (`shot_outcome`).

2.  **How we achieved this visualization, and why we chose it.**
    This visualization is a scatter plot on a football pitch background. Each point on the scatter plot represents a shot. The size of the point is proportional to the xG value of the shot, and the color of the point represents the outcome of the shot (e.g., Goal, Saved, Off T). A scatter plot was chosen because it's an effective way to show the exact location of each shot and to encode additional information (xG and outcome) using size and color.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Heatmap:** A heatmap could show the areas on the pitch where most shots are taken from.
      - **Pros:** Good for showing the density of shots.
      - **Cons:** Doesn't show individual shot information like xG or outcome.
    - **Hexbin Plot:** Similar to a heatmap, a hexbin plot aggregates points into hexagonal bins.
      - **Pros:** Can be more visually appealing than a standard heatmap.
      - **Cons:** Still loses individual shot information.
    - **Bar Chart:** A bar chart could show the number of shots by outcome or by player.
      - **Pros:** Good for comparing counts.
      - **Cons:** Doesn't provide any spatial information.

4.  **How our visualization is better than others.**
    The chosen scatter plot is better because it provides a comprehensive view of the shots in a single visualization. It shows not only _where_ the shots were taken from but also the _quality_ of each shot (through xG) and the _result_ of the shot (through color). This level of detail is lost in aggregative visualizations like heatmaps or bar charts.

5.  **What was the preprocessing done for this visualization?**
    The main preprocessing step is filtering the event data to get only the "Shot" events for the selected team. The location, xG, and outcome of each shot are then extracted from the filtered data. There are no complex calculations or assumptions made in this preprocessing step.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    It's important to note that the xG values are provided by StatsBomb and are not calculated in the code. The visualization also includes a detailed football pitch background, which is drawn using the `_draw_pitch_plotly` function. This adds context to the shot locations.

### `create_pass_network`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered to include only successful "Pass" events for the selected team. The data includes the player who made the pass (`player`), the recipient of the pass (`pass_recipient`), and the location of the pass (`location`).

2.  **How we achieved this visualization, and why we chose it.**
    This visualization is a pass network graph drawn on a football pitch. Each node in the network represents a player, and the edges between the nodes represent passes between those players. The size of the nodes is proportional to the player's total involvement (passes made and received), and the width of the edges is proportional to the number of passes between the two players. A network graph was chosen because it's an excellent way to visualize the relationships and interactions between players in a team.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Adjacency Matrix:** An adjacency matrix could show the number of passes between each pair of players.
      - **Pros:** Provides a clear, numerical representation of the pass counts.
      - **Cons:** Not as intuitive or visually appealing as a network graph, and it doesn't provide any spatial information.
    - **Chord Diagram:** A chord diagram could also show the flow of passes between players.
      - **Pros:** Can be visually striking and good for showing the overall distribution of passes.
      - **Cons:** Can become cluttered with many players, and it doesn't provide spatial information.

4.  **How our visualization is better than others.**
    The chosen pass network is better because it's drawn on a football pitch, which provides a clear spatial context for the player positions and passing lanes. It effectively combines information about player positions, passing frequency, and player involvement in a single, intuitive visualization.

5.  **What was the preprocessing done for this visualization?**
    The preprocessing for this visualization is more involved than for the shot map. First, the event data is filtered to get only successful passes for the selected team. Then, the average position of each player is calculated based on the locations of their passes. The number of passes between each pair of players is also counted. Finally, a dynamic threshold is applied to filter out connections with a low number of passes.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    This visualization handles substitutions by mapping the passes of a substituted player to the player who replaced them. The nodes are colored based on the player's position, and different symbols are used to indicate if a player was substituted.

### `create_heatmap`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered to include a specific player's events of certain types (e.g., 'Pass', 'Carry', 'Shot'). The key data point is the location of each event (`location`).

2.  **How we achieved this visualization, and why we chose it.**
    This visualization is a 2D histogram, or heatmap, drawn on a football pitch. The pitch is divided into a grid, and the color of each grid cell represents the number of events that occurred in that cell. A heatmap was chosen because it's an effective way to show the density of a player's actions across the pitch.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Scatter Plot:** A scatter plot could show the location of each individual event.
      - **Pros:** Shows the exact location of each event.
      - **Cons:** Can become cluttered and difficult to interpret if there are many events.
    - **Contour Plot:** A contour plot is similar to a heatmap but uses lines to show areas of equal density.
      - **Pros:** Can be a smoother and more aesthetically pleasing way to show density.
      - **Cons:** Might be less precise than a heatmap in showing the exact density in each area.

4.  **How our visualization is better than others.**
    The heatmap is better than a scatter plot for this purpose because it provides a clearer picture of the areas where the player is most active. It avoids the over-plotting problem of a scatter plot and makes it easy to see the player's "hot zones" at a glance.

5.  **What was the preprocessing done for this visualization?**
    The preprocessing involves filtering the event data for a specific player and a set of event types. Then, the event locations are binned into a 2D grid, and the number of events in each bin is counted.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    The resolution of the heatmap can be adjusted by changing the number of bins in the `np.histogram2d` function. The color scale of the heatmap can also be customized to highlight different levels of activity.

### `create_progressive_passes_viz`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered to include only "progressive passes" for the selected team. A progressive pass is defined as a pass that moves the ball significantly forward.

2.  **How we achieved this visualization, and why we chose it.**
    This visualization is a horizontal bar chart that shows the number of progressive passes made by each player. A bar chart was chosen because it's a simple and effective way to compare the number of progressive passes for each player.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Pie Chart:** A pie chart could show the proportion of progressive passes made by each player.
      - **Pros:** Good for showing parts of a whole.
      - **Cons:** Becomes difficult to read with many players.
    - **Table:** A table could list the players and their progressive pass counts.
      - **Pros:** Provides precise numerical data.
      - **Cons:** Not as visually engaging as a chart.

4.  **How our visualization is better than others.**
    The horizontal bar chart is better than a pie chart because it's easier to compare the lengths of the bars than the angles of the pie slices, especially when there are many players. It's more visually engaging than a table while still clearly showing the ranking of the players.

5.  **What was the preprocessing done for this visualization?**
    The main preprocessing step is to filter the event data to identify progressive passes based on a set of rules. These rules consider the start and end location of the pass to determine if it has moved the ball significantly forward. After filtering, the number of progressive passes for each player is counted.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    The definition of a progressive pass is a key assumption in this visualization. Different definitions could lead to different results. The height of the bar chart is also dynamically adjusted based on the number of players to ensure that it remains readable.

### `create_xg_timeline`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered to include "Shot" and "Own Goal" events. The key data points are the minute of the event (`minute`), the team (`team`), the player (`player`), the xG value of the shot (`shot_statsbomb_xg`), and the outcome of the shot (`shot_outcome`).

2.  **How we achieved this visualization, and why we chose it.**
    This visualization is a cumulative line chart that shows the cumulative xG for each team over the course of the match. It also includes markers for goals. A cumulative line chart was chosen because it's an effective way to show the flow of the match in terms of scoring chances and to see which team was creating the better opportunities at different points in the game.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Bar Chart:** A bar chart could show the final xG for each team.
      - **Pros:** Simple and easy to read.
      - **Cons:** Doesn't show how the xG accumulated over time.
    - **Shot Map:** A shot map shows the location and xG of each individual shot.
      - **Pros:** Provides detailed information about each shot.
      - **Cons:** Doesn't show the cumulative story of the match as effectively as a timeline.

4.  **How our visualization is better than others.**
    The xG timeline is better because it tells the story of the match. It shows not only the final xG but also the ebbs and flows of the game, highlighting periods of dominance for each team. The inclusion of goal markers provides a direct comparison between expected and actual goals.

5.  **What was the preprocessing done for this visualization?**
    The preprocessing involves filtering the event data for shots and own goals. The cumulative xG for each team is then calculated by taking the cumulative sum of the xG values of their shots. Goal events are also identified and prepared for plotting on the timeline.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    This visualization handles own goals by adding them to the goal markers on the timeline. It also includes logic to prevent overlapping goal annotations by staggering them vertically and horizontally.

### `create_formation_viz`

1.  **What was the data?**
    The data used is the event data for a specific match, filtered for "Ball Receipt" events for players in the starting XI. The tactical formation data is also used to get the starting formation and player positions.

2.  **How we achieved this visualization, and why we chose it.**
    This visualization shows the team's formation with player position heatmaps. It uses the `mplsoccer` library to draw a vertical pitch and overlay the formation and heatmaps. This visualization was chosen to show both the nominal formation and the actual areas where each player was active.

3.  **What were the other alternatives of visualization pros and cons of each?**

    - **Static Formation Diagram:** A simple diagram showing the starting formation.
      - **Pros:** Simple and easy to understand.
      - **Cons:** Doesn't show how the players actually moved during the match.
    - **Pass Network:** A pass network can also give an indication of the team's shape.
      - **Pros:** Shows the connections between players.
      - **Cons:** Might not be as clear as a dedicated formation visualization for showing the team's defensive and offensive shape.

4.  **How our visualization is better than others.**
    This visualization is better because it combines the nominal formation with actual player position data in the form of heatmaps. This provides a much richer and more accurate picture of the team's tactical setup than a simple static formation diagram.

5.  **What was the preprocessing done for this visualization?**
    The preprocessing involves identifying the starting XI and their formation from the tactical data. The event data is then filtered for ball receipts by these players. The location data from these events is used to create the heatmaps for each player.

6.  **Any other important aspect that may be required, or may be asked from this project regarding this visualization.**
    This visualization uses `matplotlib` and `mplsoccer` instead of `plotly`, so the figure has to be converted to a base64 string to be displayed in the Dash app. The names of players with three or more words are shortened to just the first and last words to keep the visualization clean.

## `match_overview_simple.py`

This file sets up the Dash application, including the layout and callbacks. It has two main layouts: one for match analysis and one for tournament overview. The match analysis layout has tabs for different visualizations: Shot Maps, Pass Networks, xG Timeline, Match Stats, Key Events, and Formations. The `update_match_visualizations` callback function is the key component that calls the appropriate plotting function from `plot_utils.py` based on the selected tab and then returns the corresponding visualization to the app.
