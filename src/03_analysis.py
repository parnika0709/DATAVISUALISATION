from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "processed" / "startups_clean.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. Run 02_clean_data.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Basic KPIs
    # ---------------------------------------------------------

    kpis = pd.DataFrame({
        "metric": [
            "Total Records",
            "Unique Startups",
            "Total Funding (₹ Cr)",
            "Cities",
            "Industries",
            "Investors"
        ],
        "value": [
            len(df),
            df["startup_name"].nunique(),
            df["funding_crore"].sum(),
            df["city"].nunique(),
            df["industry"].nunique(),
            df["investors"].nunique()
        ]
    })

    kpis.to_csv(
        OUTPUT_DIR / "kpis.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Startup count by city
    # ---------------------------------------------------------

    city_startups = (
        df.dropna(subset=["city"])
        .groupby("city")
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum")
        )
        .reset_index()
        .sort_values("startup_count", ascending=False)
    )

    city_startups.to_csv(
        OUTPUT_DIR / "city_analysis.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Industry analysis
    # ---------------------------------------------------------

    industry_analysis = (
        df.dropna(subset=["industry"])
        .groupby("industry")
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum")
        )
        .reset_index()
        .sort_values("funding_crore", ascending=False)
    )

    industry_analysis.to_csv(
        OUTPUT_DIR / "industry_analysis.csv",
        index=False
    )

    # ---------------------------------------------------------
    # City × Industry
    # ---------------------------------------------------------

    city_industry = (
        df.dropna(subset=["city", "industry"])
        .groupby(["city", "industry"])
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum")
        )
        .reset_index()
    )

    city_industry.to_csv(
        OUTPUT_DIR / "city_industry_analysis.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Yearly ecosystem growth
    # ---------------------------------------------------------

    yearly = (
        df.dropna(subset=["year"])
        .groupby("year")
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum")
        )
        .reset_index()
        .sort_values("year")
    )

    yearly.to_csv(
        OUTPUT_DIR / "yearly_analysis.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Funding rounds
    # ---------------------------------------------------------

    rounds = (
        df.dropna(subset=["funding_round"])
        .groupby("funding_round")
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum")
        )
        .reset_index()
        .sort_values("funding_crore", ascending=False)
    )

    rounds.to_csv(
        OUTPUT_DIR / "funding_round_analysis.csv",
        index=False
    )

    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print("\nGenerated:")
    print("✓ kpis.csv")
    print("✓ city_analysis.csv")
    print("✓ industry_analysis.csv")
    print("✓ city_industry_analysis.csv")
    print("✓ yearly_analysis.csv")
    print("✓ funding_round_analysis.csv")


if __name__ == "__main__":
    main()