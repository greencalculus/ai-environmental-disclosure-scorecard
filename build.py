#!/usr/bin/env python3
"""Build ai-disclosure-scorecard.csv / .json: what ten AI developers publish about their environmental footprint.

Long format, one row per developer x indicator. `status` says what we found:
  measured   - the developer published a figure it measured in production
  stated     - the developer stated a figure without publishing the method
  modelled   - the developer's own researchers published a modelled estimate
  published  - a company-wide figure from the developer's own report
  not_found  - we found no figure from the developer as of the retrieval date
Values are copied exactly as published; `change_*` columns are the only derived values.

    python3 build.py
"""
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).parent
RETRIEVED = "2026-10-22"
VERSION = "2026.10.22"

FIELDS = ["id", "developer", "indicator", "status", "value", "unit", "period", "scope",
          "change_vs_prior_year_pct", "change_vs_baseline_pct", "baseline_period",
          "source_title", "source_url", "source_date", "retrieved", "notes"]

DEVELOPERS = ["Google", "OpenAI", "Microsoft", "Meta", "Amazon", "Apple", "Anthropic", "xAI", "DeepSeek", "Mistral AI"]
INDICATORS = ["energy_per_prompt", "water_per_prompt", "carbon_per_prompt", "image_or_video_per_item",
              "company_emissions", "data_center_pue", "data_center_wue"]

S = {
    "google_er": ("Google 2026 Environmental Report", "https://sustainability.google/reports/google-2026-environmental-report/", "2026-06"),
    "gemini": ("Elsworth et al., Measuring the environmental impact of delivering AI at Google scale (arXiv 2508.15734)", "https://arxiv.org/abs/2508.15734", "2025-08-21"),
    "altman": ("Sam Altman, The Gentle Singularity", "https://blog.samaltman.com/the-gentle-singularity", "2025-06-10"),
    "ms_fact": ("Microsoft 2026 Environmental Data Fact Sheet", "https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf", "2026"),
    "ms_report": ("Microsoft 2026 Environmental Sustainability Report", "https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Sustainability-Report-PDF.pdf", "2026"),
    "ms_joule": ("Oviedo et al., Energy use of AI inference: efficiency pathways and test-time compute, Joule (Microsoft Research)", "https://doi.org/10.1016/j.joule.2026.102430", "2026-04"),
    "ms_blog": ("Microsoft Cloud blog, Scaling AI with 8 to 20x energy efficiency", "https://www.microsoft.com/en-us/microsoft-cloud/blog/2026/06/15/scaling-ai-with-8-to-20x-energy-efficiency/", "2026-06-15"),
    "meta_edi": ("Meta 2025 Environmental Data Index", "https://sustainability.atmeta.com/asset/2025-environmental-data-index", "2025"),
    "amzn": ("Amazon 2025 Sustainability Report", "https://sustainability.aboutamazon.com/2025-amazon-sustainability-report.pdf", "2026"),
    "aws": ("Amazon Sustainability: AWS Cloud", "https://sustainability.aboutamazon.com/products-services/aws-cloud", "2026"),
    "apple": ("Apple Environmental Progress Report 2026", "https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2026.pdf", "2026"),
    "mistral": ("Mistral AI, Our contribution to a global environmental standard for AI", "https://mistral.ai/news/our-contribution-to-a-global-environmental-standard-for-ai", "2025-07-22"),
    "heatmap": ("Heatmap, Anthropic carbon emissions", "https://heatmap.news/climate/anthropic-carbon-emissions", "2026-06-17"),
    "mittr": ("O'Donnell and Crownhart, We did the math on AI's energy footprint (MIT Technology Review)", "https://www.technologyreview.com/2025/05/20/1116327/ai-energy-usage-climate-footprint-big-tech/", "2025-05-20"),
}

# (developer, indicator) -> dict. Anything not listed is not_found.
F = {
    ("Google", "energy_per_prompt"): dict(status="measured", value=0.24, unit="Wh", period="May 2025", scope="median Gemini Apps text prompt", src="gemini",
        notes="Includes idle machines, host CPU and RAM and data center overhead. Energy per median prompt fell 33x over 12 months."),
    ("Google", "water_per_prompt"): dict(status="measured", value=0.26, unit="mL", period="May 2025", scope="median Gemini Apps text prompt, on-site cooling water", src="gemini"),
    ("Google", "carbon_per_prompt"): dict(status="measured", value=0.03, unit="gCO2e", period="May 2025", scope="median Gemini Apps text prompt, market-based", src="gemini",
        notes="Carbon per median prompt fell 44x over 12 months."),
    ("Google", "company_emissions"): dict(status="published", value=14473100, unit="tCO2e", period="2025", scope="ambition-based total", src="google_er",
        prior=12233300, base=8002500, base_period="2019",
        notes="Google: rise 'primarily driven by increases in supply chain activities'. 100% annual renewable electricity match for the ninth year."),
    ("Google", "data_center_pue"): dict(status="published", value=1.09, unit="ratio", period="TTM Q2 2026", scope="fleet", src="google_er"),
    ("OpenAI", "energy_per_prompt"): dict(status="stated", value=0.34, unit="Wh", period="2025", scope="average ChatGPT query", src="altman",
        notes="Stated in a blog post; no method published."),
    ("OpenAI", "water_per_prompt"): dict(status="stated", value=0.32, unit="mL", period="2025", scope="average ChatGPT query", src="altman",
        notes="Stated as 0.000085 US gallons, 'roughly one fifteenth of a teaspoon'. What the water covers is not stated."),
    ("Microsoft", "energy_per_prompt"): dict(status="modelled", value=0.31, unit="Wh", period="2026", scope="median query, frontier-scale models (not Copilot-specific)", src="ms_joule",
        notes="Modelled, interquartile range 0.16 to 0.60 Wh; long reasoning responses use more than 10x as much."),
    ("Microsoft", "water_per_prompt"): dict(status="modelled", value="0.0-0.067", unit="mL", period="2026", scope="typical query, on-site water", src="ms_blog"),
    ("Microsoft", "company_emissions"): dict(status="published", value=20290000, unit="tCO2e", period="FY2025", scope="Scope 1+2 (market) + 3, Table 1B", src="ms_fact",
        prior=16215000, base=12881000, base_period="FY2020",
        notes="Market-based Scope 2 rose from 259,090 to 2,707,428 tCO2e (Table 1A). Microsoft: rise 'driven primarily by the expansion of our datacenter infrastructure and stopping our use of non-additional, unbundled renewable energy certificates'."),
    ("Microsoft", "data_center_pue"): dict(status="published", value=1.17, unit="ratio", period="FY2025", scope="fleet", src="ms_report"),
    ("Microsoft", "data_center_wue"): dict(status="published", value=0.27, unit="L/kWh", period="FY2025", scope="fleet", src="ms_report"),
    ("Meta", "company_emissions"): dict(status="published", value=8200595, unit="tCO2e", period="2024", scope="total, location and market as reported", src="meta_edi",
        prior=7496232, base=5129000, base_period="2020", notes="Latest report available on the retrieval date covers 2024."),
    ("Meta", "data_center_pue"): dict(status="published", value=1.08, unit="ratio", period="2024", scope="data centers", src="meta_edi"),
    ("Meta", "data_center_wue"): dict(status="published", value=0.19, unit="L/kWh", period="2024", scope="data centers", src="meta_edi"),
    ("Amazon", "company_emissions"): dict(status="published", value=80850000, unit="tCO2e", period="2025", scope="carbon footprint, whole company", src="amzn",
        prior=69550000, base=51170000, base_period="2019",
        notes="Published as 80.85 MMT. Whole company, retail and logistics included, not AWS alone. Scope 2 up 34% year on year."),
    ("Amazon", "data_center_pue"): dict(status="published", value=1.14, unit="ratio", period="2025", scope="AWS global", src="aws"),
    ("Amazon", "data_center_wue"): dict(status="published", value=0.12, unit="L/kWh", period="2025", scope="AWS global", src="aws"),
    ("Apple", "company_emissions"): dict(status="published", value=15300000, unit="tCO2e", period="FY2025", scope="gross emissions", src="apple",
        base=38400000, base_period="FY2015",
        notes="Published as 15.3 Mt, flat against FY2024. Many Apple Intelligence features run on the device rather than in a data center."),
    ("Mistral AI", "water_per_prompt"): dict(status="measured", value=45, unit="mL", period="2025", scope="400-token Le Chat response, full life cycle", src="mistral",
        notes="Life-cycle assessment with Carbone 4 and ADEME, peer reviewed by Resilio and Hubblo; includes server manufacturing."),
    ("Mistral AI", "carbon_per_prompt"): dict(status="measured", value=1.14, unit="gCO2e", period="2025", scope="400-token Le Chat response, full life cycle", src="mistral",
        notes="Also 0.16 mg Sb eq of materials. Training plus 18 months of use of Mistral Large 2: 20.4 ktCO2e and 281,000 m3 of water. No energy per response and no company-wide inventory."),
}

NOTFOUND = {
    "Anthropic": ("heatmap", "Heatmap (17 Jun 2026) found no sustainability report or climate commitments; Anthropic did not respond."),
    "xAI": (None, ""),
    "DeepSeek": (None, ""),
}

IMAGE_NOTE = ("No developer publishes per-image or per-video figures. Independent measurements by MIT Technology Review on open models: "
              "Stable Diffusion 3 Medium image 2,282 J; 5-second CogVideoX video about 3.4 MJ.")


def pct(a, b):
    return round((a - b) / b * 100, 1)


def rows():
    out = []
    for d in DEVELOPERS:
        for ind in INDICATORS:
            f = F.get((d, ind))
            r = dict.fromkeys(FIELDS, "")
            r.update(developer=d, indicator=ind, retrieved=RETRIEVED)
            if f:
                t, u, dt = S[f["src"]]
                r.update(status=f["status"], value=f["value"], unit=f["unit"], period=f["period"], scope=f["scope"],
                         source_title=t, source_url=u, source_date=dt, notes=f.get("notes", ""))
                if "prior" in f:
                    r["change_vs_prior_year_pct"] = pct(f["value"], f["prior"])
                if "base" in f:
                    r["change_vs_baseline_pct"] = pct(f["value"], f["base"])
                    r["baseline_period"] = f["base_period"]
            else:
                r["status"] = "not_found"
                r["notes"] = f"We found no figure from {d} as of {RETRIEVED}."
                if ind == "image_or_video_per_item":
                    t, u, dt = S["mittr"]
                    r.update(source_title=t, source_url=u, source_date=dt, notes=r["notes"] + " " + IMAGE_NOTE)
                elif d in NOTFOUND and NOTFOUND[d][0]:
                    t, u, dt = S[NOTFOUND[d][0]]
                    r.update(source_title=t, source_url=u, source_date=dt, notes=r["notes"] + " " + NOTFOUND[d][1])
            out.append(r)
    for i, r in enumerate(out, 1):
        r["id"] = i
    return out


def summary(rs):
    def who(ind, ok):
        return sorted({r["developer"] for r in rs if r["indicator"] == ind and r["status"] in ok})
    pub = ("measured", "stated", "modelled", "published")
    per_prompt = sorted(set(who("energy_per_prompt", pub)) | set(who("water_per_prompt", pub)) | set(who("carbon_per_prompt", pub)))
    rising = sorted(r["developer"] for r in rs if r["indicator"] == "company_emissions" and r["change_vs_prior_year_pct"] not in ("", None) and r["change_vs_prior_year_pct"] > 0)
    return {
        "developers": len(DEVELOPERS),
        "energy_per_prompt": who("energy_per_prompt", pub),
        "any_per_prompt_figure": per_prompt,
        "image_or_video": who("image_or_video_per_item", pub),
        "company_emissions": who("company_emissions", pub),
        "company_emissions_rising_year_on_year": rising,
    }


def main():
    rs = rows()
    with open(HERE / "ai-disclosure-scorecard.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rs)
    meta = {"title": "AI Environmental Disclosure Scorecard", "version": VERSION, "retrieved": RETRIEVED,
            "license": "CC-BY-4.0", "publisher": "GreenCalculus", "summary": summary(rs), "rows": rs}
    (HERE / "ai-disclosure-scorecard.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(len(rs), "rows")
    print(json.dumps(meta["summary"], indent=1))


if __name__ == "__main__":
    main()
