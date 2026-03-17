---
name: visualizer
description: "Expert guidance for creating interactive HTML visualizations, dashboards, games, and calculators"
allowed-tools:
  - create_html_widget
---

# Visualizer Skill

You are an expert at creating rich, interactive HTML visualizations. Use this skill whenever the user asks you to create charts, dashboards, games, calculators, or any visual widget.

## When to Create Visualizations

- **Charts & Graphs**: Line charts for trends, bar charts for comparisons, pie charts for composition, scatter plots for relationships
- **Dashboards**: Multi-metric displays combining several chart types with KPI cards
- **Interactive Tools**: Calculators, converters, configurators, form wizards
- **Games & Simulations**: Simple browser-based games, physics simulations, procedural art
- **Data Explorers**: Filterable tables, searchable lists, interactive maps

## Architecture Guidelines

1. **Single-File HTML**: All visualizations must be self-contained in one HTML file with inline CSS and JavaScript.
2. **CDN Dependencies Only**: Load libraries from CDN — never reference local files. See `references/cdn-libraries.md` for approved libraries and usage patterns.
3. **Responsive Design**: Use relative units, flexbox/grid, and media queries so widgets work on any screen size.
4. **Visual Polish**: Apply consistent color palettes, smooth transitions, proper typography, and adequate whitespace.
5. **Performance**: Minimize DOM updates, use `requestAnimationFrame` for animations, debounce resize handlers.
6. **Accessibility**: Include `aria` labels, ensure sufficient color contrast, support keyboard navigation where applicable.

## Chart Type Selection

| Data Pattern | Recommended Chart | When to Use |
|---|---|---|
| Trend over time | Line chart | Show how values change across a time axis |
| Category comparison | Bar chart (vertical) | Compare discrete categories |
| Ranking | Horizontal bar chart | Show items ordered by value |
| Part of whole | Pie / Donut chart | Show composition (≤7 segments) |
| Distribution | Histogram | Show frequency distribution of values |
| Correlation | Scatter plot | Show relationship between two variables |
| Flow / Process | Sankey diagram | Show how values flow between stages |
| Hierarchy | Treemap | Show nested categorical data with size encoding |
| Geographic | Choropleth / Bubble map | Show data with geographic dimension |

## Best Practices

- Always include a descriptive title and axis labels on charts
- Use tooltips for detailed information on hover
- Apply a cohesive color scheme — prefer 3–5 colors maximum
- Add smooth animations for data transitions
- Include a legend when multiple data series are present
- Handle edge cases: empty data, single data point, very large values
