"""Fetch raw NHANES 2017-March 2020 pre-pandemic files for egfr40.

Downloads each XPT file from CDC and saves it unchanged as Parquet
(optionally CSV) in data/raw/. No filtering or merging here; that
lives in preprocessing.py.

Usage:
    python data_gen.py
    python data_gen.py --csv
    python data_gen.py --out-dir data/raw --overwrite
"""

import io
from pathlib import Path

import pandas as pd
import requests
import typer

app = typer.Typer(add_completion=False)

BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles"

# File -> what it provides for the egfr40 equation
FILES = {
    "P_DEMO": "age (RIDAGEYR), sex (RIAGENDR), survey design",
    "P_BIOPRO": "serum creatinine (LBXSCR) for CKD-EPI 2021 eGFR",
    "P_ALB_CR": "urine albumin-to-creatinine ratio (URDACT)",
    "P_GHB": "HbA1c (LBXGH)",
    "P_BPXO": "oscillometric systolic BP (BPXOSY1-3)",
    "P_BMX": "BMI (BMXBMI)",
    "P_BPQ": "antihypertensive medication (BPQ020, BPQ040A)",
    "P_DIQ": "diabetes (DIQ010), insulin (DIQ050), oral meds (DIQ070)",
    "P_MCQ": "heart failure (MCQ160B), CHD (MCQ160C), heart attack (MCQ160E)",
    "P_SMQ": "smoking (SMQ020, SMQ040)",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (egfr40 data_gen)"}


def fetch_xpt(name: str) -> pd.DataFrame:
    """Download one NHANES XPT file and return it as a DataFrame."""
    url = f"{BASE_URL}/{name}.xpt"
    resp = requests.get(url, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    return pd.read_sas(io.BytesIO(resp.content), format="xport", encoding="infer")


@app.command()
def main(
    out_dir: Path = typer.Option(Path("data/raw"), help="Where to save raw files."),
    csv: bool = typer.Option(False, "--csv", help="Also save a CSV backup."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Re-download existing files."),
):
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, desc in FILES.items():
        parquet_path = out_dir / f"{name}.parquet"
        if parquet_path.exists() and not overwrite:
            typer.echo(f"skip   {name} (exists)")
            continue

        typer.echo(f"fetch  {name}: {desc}")
        df = fetch_xpt(name)
        df["SEQN"] = df["SEQN"].astype("int64")
        df.to_parquet(parquet_path, index=False)
        if csv:
            df.to_csv(out_dir / f"{name}.csv", index=False)
        typer.echo(f"saved  {parquet_path} ({len(df):,} rows, {df.shape[1]} cols)")


if __name__ == "__main__":
    app()
