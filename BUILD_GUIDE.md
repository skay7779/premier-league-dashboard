# Build guide: Premier League Performance Dashboard (Tableau Public)

**The question the dashboard answers:** *What actually separates the top of the Premier League from the rest: creating more chances, or finishing them better?*

Having a question is what turns a chart collection into analysis. Recruiters remember the finding, not the chart.

---

## Step 1: Get the data (5 min)

1. Go to **football-data.co.uk → England → Premier League**.
2. Download the CSV for each of the last **five seasons** (2021/22 to 2025/26).
3. Rename them `E0_2122.csv`, `E0_2223.csv`, `E0_2324.csv`, `E0_2425.csv` and `E0_2526.csv`, and put them in the `data/` folder.

## Step 2: Prepare it with Python (5 min)

```
source ~/venvs/portfolio/bin/activate
cd ~/Finance/premier-league-dashboard     # wherever you put this folder
python prep_data.py
```

You'll get two clean files in `output/`:
- `team_season.csv`: one row per team per season (points, goals, shots, conversion rate, home/away points)
- `matches_long.csv`: one row per team per match (for form and points-race charts)

Check the printed list of champions is right. That's your data sanity check.

## Step 3: Build three dashboards in Tableau Public (3–4 hours)

Connect to both CSVs (**Connect → Text file**).

### Dashboard 1: League overview
- **League table:** Team, Played, W, D, L, GD, Points, sorted by Position. Add a **Season** filter.
- **Points race:** line chart of `CumulativePoints` by `Matchweek`, colour by Team. Highlight the top 4.

### Dashboard 2: Chance creation vs finishing (the headline)
- **Scatter plot:** `Shots` (x) vs `GoalsFor` (y), one dot per team-season, sized by `Points`.
- Add a **trend line** (Analytics pane). Teams above the line finish better than their shot volume predicts.
- **Bar chart:** `ShotConversion` by team, sorted, for the selected season.
- Add a text box with your **finding** in one sentence.

### Dashboard 3: Team deep dive
- **Team filter** (single value) and **Season** filter.
- **Form line:** `Form5` (points from the last 5 games) by `Matchweek`.
- **Home vs away:** side-by-side bars of `HomePoints` and `AwayPoints`.
- **KPI tiles:** Points, Goal difference, Shot conversion and Shot accuracy.

### Make it look professional
- One colour for the selected team, grey for everyone else.
- Titles that state the insight ("Top teams don't shoot more, they finish better"), not just "Shots vs Goals".
- Same fonts and sizes on every dashboard.

## Step 4: Publish and document (30 min)

1. **File → Save to Tableau Public.** Copy the public link.
2. Take a screenshot of each dashboard and save it in `screenshots/`.
3. Fill in the `README.md` (finding, link, screenshots).
4. Push the folder to a new GitHub repo, `premier-league-dashboard`.

## Interview talking points

- **Why this question?** Shot data shows whether results come from creating chances or from finishing them, which is a real question clubs ask.
- **What would you do with more time?** Add expected goals (xG), which measures chance quality, not just volume.
- **What was hard?** Reshaping home/away match rows into one row per team per match so every team could be analysed the same way.
