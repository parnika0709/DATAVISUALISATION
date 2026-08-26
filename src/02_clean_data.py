from pathlib import Path
import re
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "startups.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "startups_clean.csv"


def normalize_column_name(column):
    column = str(column).strip()
    column = re.sub(r"\s+", " ", column)
    return column


def find_column(df, possible_names):
    normalized = {
        re.sub(r"[^a-z0-9]", "", str(col).lower()): col
        for col in df.columns
    }

    for name in possible_names:
        key = re.sub(r"[^a-z0-9]", "", name.lower())

        if key in normalized:
            return normalized[key]

    # Fuzzy matching
    for col in df.columns:
        clean_col = re.sub(r"[^a-z0-9]", "", str(col).lower())

        for name in possible_names:
            clean_name = re.sub(r"[^a-z0-9]", "", name.lower())

            if clean_name in clean_col or clean_col in clean_name:
                return col

    return None


def clean_text(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value.lower() in {
        "",
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "unknown",
        "undisclosed"
    }:
        return np.nan

    return value


def clean_city(value):
    value = clean_text(value)

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    # Common formatting problems
    value = value.replace(",", "")

    city_map = {
        "Bangalore": "Bengaluru",
        "Bengaluru": "Bengaluru",
        "Delhi NCR": "Delhi",
        "New Delhi": "Delhi",
        "Gurgaon": "Gurugram",
        "Gurugram": "Gurugram",
        "Noida": "Noida",
        "Bombay": "Mumbai"
    }

    return city_map.get(value, value)


def clean_industry(value):
    value = clean_text(value)

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    # Keep the original category but clean formatting
    value = re.sub(r"\s+", " ", value)

    return value


def parse_money(value):
    """
    Converts common money formats into numeric values.

    Examples:
    100
    $100
    ₹100 Cr
    100 Crores
    100000000
    """
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    if value in {"", "nan", "none", "n/a", "na", "undisclosed"}:
        return np.nan

    value = value.replace(",", "")
    value = value.replace("$", "")
    value = value.replace("₹", "")
    value = value.replace("rs.", "")
    value = value.replace("rs", "")

    multiplier = 1

    if "crore" in value or "cr" in value:
        multiplier = 1
        value = re.sub(r"crores?", "", value)
        value = value.replace("cr", "")

    elif "million" in value or "m" in value:
        multiplier = 0.083  # approximate USD million → INR crore
        value = re.sub(r"million", "", value)
        value = value.replace("m", "")

    elif "billion" in value or "b" in value:
        multiplier = 83.0  # approximate USD billion → INR crore
        value = re.sub(r"billion", "", value)
        value = value.replace("b", "")

    value = re.sub(r"[^0-9.\-]", "", value)

    try:
        number = float(value)
        return number * multiplier
    except ValueError:
        return np.nan


def main():

    print("=" * 70)
    print("CLEANING STARTUP DATA")
    print("=" * 70)

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}\n"
            "Place the Kaggle CSV inside data/raw/startups.csv"
        )

    df = pd.read_csv(RAW_FILE)

    df.columns = [normalize_column_name(c) for c in df.columns]

    # ---------------------------------------------------------
    # Detect important columns
    # ---------------------------------------------------------

    startup_col = find_column(df, [
        "Startup Name",
        "Company Name",
        "Startup",
        "Company",
        "Name"
    ])

    industry_col = find_column(df, [
        "Industry",
        "Industry Vertical",
        "Industry/Vertical",
        "Sector",
        "Vertical"
    ])

    city_col = find_column(df, [
        "City",
        "Location",
        "Headquarters",
        "Startup Location"
    ])

    funding_col = find_column(df, [
        "Funding Amount",
        "Amount",
        "Amount in USD",
        "Amount($)",
        "Funding"
    ])

    date_col = find_column(df, [
        "Date",
        "Funding Date",
        "Date of Funding",
        "Funding Date"
    ])

    round_col = find_column(df, [
        "Funding Round",
        "Round",
        "Stage",
        "Funding Type"
    ])

    investors_col = find_column(df, [
        "Investors",
        "Investor",
        "Investors Name",
        "Investor Name"
    ])

    print("\nDetected columns:")
    print(f"Startup   : {startup_col}")
    print(f"Industry  : {industry_col}")
    print(f"City      : {city_col}")
    print(f"Funding   : {funding_col}")
    print(f"Date      : {date_col}")
    print(f"Round     : {round_col}")
    print(f"Investors : {investors_col}")

    # ---------------------------------------------------------
    # Rename columns into a standard internal format
    # ---------------------------------------------------------

    rename_map = {}

    if startup_col:
        rename_map[startup_col] = "startup_name"

    if industry_col:
        rename_map[industry_col] = "industry"

    if city_col:
        rename_map[city_col] = "city"

    if funding_col:
        rename_map[funding_col] = "funding_crore"

    if date_col:
        rename_map[date_col] = "funding_date"

    if round_col:
        rename_map[round_col] = "funding_round"

    if investors_col:
        rename_map[investors_col] = "investors"

    df = df.rename(columns=rename_map)

    # ---------------------------------------------------------
    # Create missing columns if necessary
    # ---------------------------------------------------------

    required_columns = [
        "startup_name",
        "industry",
        "city",
        "funding_crore",
        "funding_date",
        "funding_round",
        "investors"
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = np.nan

    # ---------------------------------------------------------
    # Cleaning
    # ---------------------------------------------------------

    df["startup_name"] = df["startup_name"].apply(clean_text)
    df["industry"] = df["industry"].apply(clean_industry)
    df["city"] = df["city"].apply(clean_city)
    df["funding_round"] = df["funding_round"].apply(clean_text)
    df["investors"] = df["investors"].apply(clean_text)

    df["funding_crore"] = df["funding_crore"].apply(parse_money)

    df["funding_date"] = pd.to_datetime(
        df["funding_date"],
        errors="coerce",
        dayfirst=True
    )

    df["year"] = df["funding_date"].dt.year

    # ---------------------------------------------------------
    # Remove obvious duplicate rows
    # ---------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(f"\nRemoved duplicates: {before - after:,}")

    # ---------------------------------------------------------
    # Remove records with no startup name
    # ---------------------------------------------------------

    df = df.dropna(subset=["startup_name"])

    # ---------------------------------------------------------
    # Make numeric columns numeric
    # ---------------------------------------------------------

    df["funding_crore"] = pd.to_numeric(
        df["funding_crore"],
        errors="coerce"
    )

    # Negative funding values are invalid
    df.loc[df["funding_crore"] < 0, "funding_crore"] = np.nan

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)

    print(f"\nOutput file:")
    print(OUTPUT_FILE)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nFinal columns:")
    print(list(df.columns))


if __name__ == "__main__":
    main()