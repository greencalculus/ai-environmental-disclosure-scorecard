# AI Environmental Disclosure Scorecard

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23556720.svg)](https://doi.org/10.5281/zenodo.23556720)

What ten AI developers publish about the environmental footprint of their AI: energy, water and carbon per prompt, per image or video, company-wide emissions, and data center efficiency (PUE and WUE). One row per developer and indicator, each traced to the developer's own publication, or marked `not_found` with the date we looked.

- **70 rows**: 10 developers (Google, OpenAI, Microsoft, Meta, Amazon, Apple, Anthropic, xAI, DeepSeek, Mistral AI) × 7 indicators.
- **Values copied exactly as published.** The only derived columns are `change_vs_prior_year_pct` and `change_vs_baseline_pct`.
- **Retrieved 22 October 2026.** `not_found` means we found no figure from the developer on that date, not that none exists. Corrections welcome.

Read with context: https://greencalculus.com/guides/is-ai-bad-for-the-environment/

## Headline (22 October 2026)

| | Developers |
|---|---|
| Publish energy per prompt | 3 of 10: Google (measured), OpenAI (stated, no method), Microsoft (modelled by its researchers) |
| Publish any per-prompt figure | 4 of 10: the three above plus Mistral AI (life-cycle water and carbon) |
| Publish per-image or per-video figures | 0 of 10 |
| Publish company-wide emissions | 5 of 10: Google, Microsoft, Meta, Amazon, Apple |
| Company emissions rising year on year | 4 of those 5 (Apple flat) |
| AI-only labs publishing company emissions | 0 (OpenAI, Anthropic, xAI, DeepSeek, Mistral AI) |

## Columns

| Column | Meaning |
|---|---|
| `id` | Row id, stable within a version |
| `developer` | The AI developer |
| `indicator` | `energy_per_prompt`, `water_per_prompt`, `carbon_per_prompt`, `image_or_video_per_item`, `company_emissions`, `data_center_pue`, `data_center_wue` |
| `status` | `measured` (measured in production), `stated` (stated, method not published), `modelled` (modelled estimate by the developer's researchers), `published` (company-wide figure from the developer's report), `not_found` |
| `value`, `unit` | As published; a range is written `low-high` |
| `period`, `scope` | What the figure covers |
| `change_vs_prior_year_pct`, `change_vs_baseline_pct`, `baseline_period` | Derived from the developer's own published totals |
| `source_title`, `source_url`, `source_date`, `retrieved` | Where and when the figure was read |
| `notes` | Quotes, definitions and caveats |

## Read before comparing

- **Per-prompt figures are not like for like.** Google's are measured medians for Gemini text prompts; OpenAI's are a one-line statement with no method; Microsoft's are a modelled estimate for frontier-scale models, not Copilot; Mistral's are a full life cycle including server manufacturing.
- **Company totals are not AI totals.** Amazon's covers retail and logistics; Apple's covers devices. None of the five splits out AI.
- **Rising totals have stated causes.** Google points to its supply chain; Microsoft to data center expansion and dropping unbundled renewable certificates. Quotes are in `notes`.

## Build

```
python3 build.py
```

## Licence and citation

CC BY 4.0. Cite this dataset (see `CITATION.cff`) and the original publisher of any figure you use. GreenCalculus takes no money from AI companies: no sponsorship, advertising or affiliate deals.
