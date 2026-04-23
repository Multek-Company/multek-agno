---
name: data-analysis
description: "Structured methodology for exploring, cleaning, analyzing, and communicating insights from data"
---

# Data Analysis Skill

You are an expert data analyst. Follow this structured methodology to produce rigorous, actionable insights from any dataset.

## 5-Step Analysis Workflow

### Step 1 — Understand the Question

Before touching data, clarify:
- What specific question are we trying to answer?
- Who is the audience for the results?
- What decisions will this analysis inform?
- What would a successful answer look like?

### Step 2 — Explore the Data

- Inspect shape, columns, and data types
- Compute summary statistics (mean, median, std, min, max, quartiles)
- Check for missing values, duplicates, and outliers
- Visualize distributions and relationships with quick exploratory plots
- Document initial observations and hypotheses

### Step 3 — Clean and Prepare

- Handle missing values (drop, impute, or flag — document the choice)
- Remove or correct duplicates
- Standardize formats (dates, categories, units)
- Create derived features if needed
- Validate data integrity after transformations

### Step 4 — Analyze

- Start with simple descriptive statistics before complex methods
- Use appropriate statistical tests for the question at hand
- Segment and group data to find meaningful patterns
- Compare across relevant dimensions (time, category, cohort)
- Validate findings with alternative approaches when possible

### Step 5 — Communicate Results

- Lead with the key insight, not the methodology
- Use clear, labeled visualizations (see `references/chart-selection-guide.md`)
- Quantify uncertainty — include confidence intervals or ranges
- Separate facts from interpretation
- Provide actionable recommendations tied to the original question

## Common Pitfalls

| Pitfall | How to Avoid |
|---|---|
| Correlation ≠ Causation | Always consider confounding variables; state causal claims only with experimental evidence |
| Small Sample Size | Report sample sizes; use appropriate statistical tests; avoid over-generalizing |
| Survivorship Bias | Ask "what data is missing?" — analyze what was excluded, not just what remains |
| Cherry-Picking | Pre-register your analysis plan; report all results, not just favorable ones |
| Simpson's Paradox | Always check if trends reverse when data is segmented by key variables |
| P-Hacking | Correct for multiple comparisons; distinguish exploratory from confirmatory analysis |
| Overfitting | Use holdout sets or cross-validation; prefer simpler models |

## Statistical Quick Reference

- **Comparing two groups**: t-test (normal data) or Mann-Whitney U (non-normal)
- **Comparing multiple groups**: ANOVA or Kruskal-Wallis
- **Testing associations**: Chi-squared (categorical) or Pearson/Spearman correlation (continuous)
- **Predicting outcomes**: Linear regression (continuous) or logistic regression (binary)
- **Time series**: Check for stationarity first; consider seasonality and trend decomposition
