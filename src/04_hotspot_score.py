from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "processed" / "startups_clean.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "hotspot_scores.csv"


def min_max(series):
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(0, index=series.index)

    if maximum == minimum:
        return pd.Series(1, index=series.index)

    return (series - minimum) / (maximum - minimum)


def main():

    df = pd.read_csv(INPUT_FILE)

    # ---------------------------------------------------------
    # City-level metrics
    # ---------------------------------------------------------

    city = (
        df.dropna(subset=["city"])
        .groupby("city")
        .agg(
            startup_count=("startup_name", "nunique"),
            funding_crore=("funding_crore", "sum"),
            industry_count=("industry", "nunique"),
            investor_count=("investors", "nunique")
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # Growth metric
    # ---------------------------------------------------------

    yearly_city = (
        df.dropna(subset=["city", "year"])
        .groupby(["city", "year"])
        .agg(
            startups=("startup_name", "nunique")
        )
        .reset_index()
    )

    growth_values = []

    for city_name in city["city"]:

        temp = yearly_city[
            yearly_city["city"] == city_name
        ].sort_values("year")

        if len(temp) >= 2:

            first_value = temp.iloc[0]["startups"]
            last_value = temp.iloc[-1]["startups"]

            if first_value > 0:
                growth = (last_value - first_value) / first_value
            else:
                growth = 0

        else:
            growth = 0

        growth_values.append(growth)

    city["growth"] = growth_values

    # ---------------------------------------------------------
    # Normalize metrics
    # ---------------------------------------------------------

    city["startup_score"] = min_max(
        city["startup_count"]
    )

    city["funding_score"] = min_max(
        city["funding_crore"]
    )

    city["industry_score"] = min_max(
        city["industry_count"]
    )

    city["investor_score"] = min_max(
        city["investor_count"]
    )

    city["growth_score"] = min_max(
        city["growth"]
    )

    # ---------------------------------------------------------
    # Final score
    # ---------------------------------------------------------

    city["hotspot_score"] = (
        city["startup_score"] * 0.30
        + city["funding_score"] * 0.30
        + city["industry_score"] * 0.15
        + city["investor_score"] * 0.10
        + city["growth_score"] * 0.15
    ) * 100

    city["hotspot_score"] = city["hotspot_score"].round(2)

    city = city.sort_values(
        "hotspot_score",
        ascending=False
    )

    city["rank"] = range(1, len(city) + 1)

    city.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 70)
    print("INNOVATION HOTSPOT SCORE CREATED")
    print("=" * 70)

    print(
        city[
            [
                "rank",
                "city",
                "startup_count",
                "funding_crore",
                "hotspot_score"
            ]
        ].head(15).to_string(index=False)
    )

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()