# Chart Selection Guide

Choose the right chart based on your analytical goal and data characteristics.

---

## By Analytical Goal

### Showing Change Over Time

| Chart | When to Use | Tips |
|---|---|---|
| **Line chart** | Continuous data over time (daily revenue, temperature) | Use for ≤7 series; add markers for sparse data |
| **Area chart** | Emphasize volume/magnitude over time | Use stacked area for part-of-whole over time |
| **Bar chart (vertical)** | Discrete time periods (quarterly, yearly) | Better than line for few time points |
| **Sparkline** | Inline trend indicator without detail | Great for dashboards with many metrics |

### Comparing Categories

| Chart | When to Use | Tips |
|---|---|---|
| **Bar chart (vertical)** | Compare ≤12 categories | Sort by value for easier scanning |
| **Bar chart (horizontal)** | Long category labels or ranking | Always sort by value |
| **Grouped bar** | Compare categories across 2–3 series | Limit groups to avoid clutter |
| **Lollipop chart** | Clean alternative to bar chart | Less visual weight, good for many items |

### Showing Composition

| Chart | When to Use | Tips |
|---|---|---|
| **Pie / Donut** | ≤7 parts, one time point | Always include percentages; start at 12 o'clock |
| **Stacked bar** | Composition across categories or time | Use 100% stacked for proportional comparison |
| **Treemap** | Hierarchical composition with many items | Use color to encode a second variable |
| **Waffle chart** | Emphasize human-readable proportions | Best for percentages the audience should feel (e.g., "3 in 10") |

### Showing Distribution

| Chart | When to Use | Tips |
|---|---|---|
| **Histogram** | Distribution of one continuous variable | Choose bin width carefully; try multiple |
| **Box plot** | Compare distributions across groups | Show outliers; add jittered points for small n |
| **Violin plot** | Distribution shape comparison | Better than box plot when shape matters |
| **Density plot** | Smooth distribution comparison | Use transparency for overlapping distributions |

### Showing Relationships

| Chart | When to Use | Tips |
|---|---|---|
| **Scatter plot** | Two continuous variables | Add trendline; use color/size for 3rd/4th dimension |
| **Bubble chart** | Three continuous variables | Size = third variable; always include legend |
| **Heatmap** | Correlation matrix or 2D frequency | Use diverging color scale for correlations |
| **Connected scatter** | Two variables that change over time | Add arrows or labels to show direction |

### Showing Geographic Data

| Chart | When to Use | Tips |
|---|---|---|
| **Choropleth** | Data by region/country | Use sequential color scale; normalize by population if needed |
| **Bubble map** | Point-based geographic data | Size = magnitude; avoid overlapping bubbles |
| **Flow map** | Movement between locations | Use curved lines; vary thickness for volume |

---

## General Principles

1. **Start simple** — a well-labeled bar chart beats a confusing advanced visualization
2. **Minimize chart junk** — remove gridlines, borders, and decorations that don't encode data
3. **Use color intentionally** — highlight what matters; gray out context
4. **Label directly** — put labels on/near data points instead of relying on legends
5. **Respect zero** — bar charts must start at zero; line charts may not need to
6. **Consider your audience** — executives want headlines; analysts want detail
7. **Tell one story per chart** — if you need to make two points, make two charts
