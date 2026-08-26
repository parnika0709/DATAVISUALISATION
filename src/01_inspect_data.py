from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "raw" / "startups.csv"


def main():
    if not DATA_FILE.exists():
        print(f"\nERROR: Dataset not found:\n{DATA_FILE}")
        print("\nPlace your Kaggle CSV at:")
        print("data/raw/startups.csv")
        return

    print("=" * 70)
    print("INDIA INNOVATION ECONOMY - DATA INSPECTION")
    print("=" * 70)

    df = pd.read_csv(DATA_FILE)

    print(f"\nRows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    print("\nCOLUMN NAMES")
    print("-" * 70)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:2}. {column}")

    print("\nDATA TYPES")
    print("-" * 70)
    print(df.dtypes)

    print("\nMISSING VALUES")
    print("-" * 70)

    missing = df.isnull().sum()
    missing_percent = (missing / len(df) * 100).round(2)

    missing_table = pd.DataFrame({
        "Missing": missing,
        "Percentage": missing_percent
    })

    print(missing_table[missing_table["Missing"] > 0])

    print("\nDUPLICATES")
    print("-" * 70)
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    print("\nSAMPLE DATA")
    print("-" * 70)
    print(df.head(10).to_string())

    print("\nUNIQUE VALUES")
    print("-" * 70)

    for column in df.columns:
        if df[column].nunique(dropna=True) <= 30:
            print(f"\n{column}:")
            print(df[column].dropna().unique())

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()