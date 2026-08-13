# Chart catalog — formatting tips and variations

One entry per leaf of the decision tree. Read only the entry for the chart Step 2 landed on. Tips are
chart-specific; the three universal principles (declutter / focus / insight-title) are in SKILL.md and
apply on top of these.

---

## Horizontal Bar Chart
*comparison · static · few items (≤ 7)*

Bars run left-to-right; categories stack down the side. The default for comparing a handful of named
categories — horizontal because the labels read naturally and never need rotating.

- Order the bars by value (biggest to smallest), unless the categories have their own natural order
  (age bands, dates, sizes) — then keep that.
- Start the value axis at 0 — always. A truncated bar misrepresents the ratio between bars.
- Keep the gap between bars narrower than the bars themselves.
- Label values at the end of each bar and drop the value axis entirely, or keep the axis and drop the
  labels — never both.
- One accent colour on the bar that carries the insight; the rest light grey.

**Variations**
- **Clustered (grouped) bar** — comparing sub-categories within each category against each other.
- **Stacked bar** — comparing category totals while still showing each total's breakdown.

---

## Column Chart
*comparison · static · many items (> 7)*

Vertical bars. Use over horizontal bars when you have many categories or when the categories are
ordered left-to-right (especially time buckets).

- Start the value axis at 0 — always.
- If category labels collide, prefer horizontal bars over rotating the text to a diagonal.
- Order by value unless the categories carry a natural order.
- Direct-label the columns you want read; grey the rest.

**Variations**
- **Stacked column** — show each column's internal breakdown as well as its total.
- **Waterfall** — when the columns are additive steps building to a running total.
- **Mekko (Marimekko)** — when column *width* should also encode a second measure (e.g. segment size).

---

## Single Line Chart
*comparison · over time · single series*

One series over a continuous time axis. The cleanest way to show one thing moving through time.

- The value axis need not start at 0 — the chart shows change, and a zoomed axis reads honestly. Only
  force 0 if a reader would otherwise misjudge the magnitude of the movement.
- Keep the line heavier than the axes; fade or remove gridlines.
- Label the line directly at its right end instead of using a legend.
- Annotate the one or two points that carry the story (a peak, a launch, an inflection).

**Variations**
- **Area** — when the magnitude beneath the line matters as much as the line.

---

## Multiple Line Chart
*comparison · over time · multiple series*

Several series over the same time axis, compared against each other. Best for 2–4 series; beyond that
lines cross into spaghetti.

- Grey every line except the one the insight is about; give that one the accent colour.
- Direct-label each line at its end — legends force the eye to ping-pong.
- Cap it at ~4 series. More than that, either small-multiple it (one mini-chart per series) or
  highlight one line at a time.
- Don't force the axis to 0 if it flattens the comparison.

---

## Scatter Plot
*relationship · 2 variables* — also *distribution · 2 variables*

Each point is one observation placed by its two values. Shows correlation, clusters, and outliers.

- Put the presumed cause / independent variable on the X axis, the effect on Y.
- Add a trend line only when a relationship is real and worth stating; label its direction in words.
- Use light, semi-transparent dots so dense regions read through overplotting.
- Circle or colour the outliers or the cluster that is the point; grey the rest.

**Variations**
- **Heatmap** — when points overplot heavily; bin them and encode density as colour.
- **Paired (dumbbell) bar** — when you're really comparing two states per category, not a cloud.

---

## Bubble Chart
*relationship · 3 variables*

A scatter plot where a third measure sets each dot's **area**. Use only when the third variable
genuinely earns a dimension.

- Encode the third variable as *area*, never diameter — the eye reads area, and diameter double-counts.
- Keep the bubble count low; overlapping bubbles hide the smaller ones.
- Never start bubble sizing so small that the smallest bubbles vanish.

---

## Histogram
*distribution · 1 variable*

Bars over *ranges* of one continuous variable, showing how values cluster. Not a bar chart — the X
axis is a number line, and the bars touch.

- Bars touch (no gaps) — the axis is continuous.
- Try a few bin widths; too many bins is noise, too few hides the shape.
- Start the count (Y) axis at 0.
- Mark the mean or a threshold with a reference line if it's part of the story.

---

## Box Plot / Violin Plot
*distribution · 3+ variables (comparing distributions across groups)*

Summarises each group's distribution — median, quartiles, spread, outliers — so several distributions
sit side by side. Violin adds the density shape.

- Order the boxes by median, or by a natural category order.
- Keep outlier dots but grey them unless an outlier *is* the story.
- Use a violin over a box when the shape (bimodal, skewed) matters more than the quartiles.
- Add a light note on what the box parts mean — most audiences don't read box plots fluently.

---

## Pie / Donut
*composition · static · simple* — **use sparingly**

Shows parts of a single whole. The eye compares angles and areas poorly, so reach for it only with
very few slices and no need for precise comparison — otherwise a bar chart is clearer.

- Cap it at ~3–5 slices; more than that, switch to a bar chart of the shares.
- Order slices largest-first, starting at 12 o'clock.
- Label slices directly with category and percentage; drop the legend.
- Never explode slices or tilt to 3-D — both wreck the one thing a pie is for (part-to-whole).
- Prefer a donut only if you'll use the hole for a total or label.

**Always pair this recommendation with the caveat:** a horizontal bar of the same shares is usually
easier to read; recommend the pie only when the whole-ness itself is the message and slices are few.

**Variations**
- **Sunburst** — hierarchical parts-of-parts as concentric rings.
- **Treemap** — many parts of a whole packed as nested rectangles; area encodes share.

---

## Waterfall
*composition · static · additive*

Shows how a starting value becomes an ending value through a sequence of additions and subtractions
(e.g. opening balance → +/– drivers → closing balance).

- Colour increases and decreases distinctly, and set totals apart from steps.
- Keep the step order meaningful (the real sequence, or biggest-driver-first).
- Connect steps with light lines so the running total reads.

---

## Stacked Column
*composition · over time · few periods (≤ 7)*

Columns split into segments, one column per period, so both the total and its mix are visible across a
few time buckets.

- Keep the most important segment on the baseline (bottom) — it's the only one the eye can measure
  precisely; the floating segments are read approximately.
- Hold segment order consistent across all columns.
- Cap segment count (~5); many thin segments become unreadable.
- Grey all but the segment the story is about.

---

## Stacked Area
*composition · over time · many periods (> 7)*

The stacked-column idea over a continuous, many-period timeline — the mix of a whole evolving over
time.

- Order bands with the most stable / most important on the baseline.
- Keep bands to a handful; many bands blur.
- If the *total* is the message, a single area or line is clearer than a stack.
- Consider a 100 %-stacked area when only the shifting *share* matters, not the absolute total.

---

## Line Chart (trend)
*trend*

When the message is direction over time — is this rising, falling, flattening? — the plain line is the
tool. (Mechanically the same as the comparison line charts above; the *intent* is the trend itself.)

- Don't force the axis to 0 — the trend is the point, and 0 can flatten it.
- Fade gridlines; heavier line.
- Annotate the inflection or the event that explains the turn.

**Variations**
- **Multiple line** — a few series' trends together.
- **Area / Stacked area** — when magnitude or an evolving composition rides along with the trend.

---

## Big Number / KPI Card
*single_value*

One number, large, when a single metric is the whole message. No axes, no chart — just the figure and
its context.

- Show the figure large; add one line of comparison (vs target, vs last period) and its direction.
- A tiny sparkline beside it can carry recent trend without stealing focus.
- Colour the delta by good/bad only if the direction's meaning is unambiguous to the audience.
- One card, one number — a wall of KPI cards buries the one that matters.
