"""Build an analysis-ready NHANES 2017-March 2020 file for egfr40.

Reads the raw files saved by data_gen.py, merges them on SEQN, computes
CKD-EPI 2021 eGFR, and recodes each predictor into the inputs expected by
egfr40.add_egfr40_risk_col.

Usage:
    python preprocessing.py
    python preprocessing.py --csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
import typer

from egfr40 import ckd_epi_2021

app = typer.Typer(add_completion=False)

RAW_FILES = ["P_DEMO", "P_BIOPRO", "P_ALB_CR", "P_GHB", "P_BPXO",
             "P_BMX", "P_BPQ", "P_DIQ", "P_MCQ", "P_SMQ"]


def yes_no(s):
    """NHANES 1 = yes, 2 = no; 7 (refused), 9 (don't know) and blank -> NaN."""
    return s.map({1: 1.0, 2: 0.0})


def load_raw(raw_dir: Path) -> pd.DataFrame:
    """Left-join every raw file onto DEMO by SEQN."""
    df = pd.read_parquet(raw_dir / "P_DEMO.parquet")
    for name in RAW_FILES[1:]:
        other = pd.read_parquet(raw_dir / f"{name}.parquet")
        dup = [c for c in other.columns if c in df.columns and c != "SEQN"]
        df = df.merge(other.drop(columns=dup), on="SEQN", how="left")
    return df


def build(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({"SEQN": df["SEQN"]})

    # --- Survey design (keep for weighted estimates) ---
    for c in ["SDMVPSU", "SDMVSTRA", "WTMECPRP", "WTINTPRP"]:
        if c in df.columns:
            out[c] = df[c]

    # --- Demographics ---
    out["age"] = df["RIDAGEYR"]  # top-coded at 80
    out["sex"] = df["RIAGENDR"].map({1: "male", 2: "female"})
    male = (df["RIAGENDR"] == 1).astype(float).where(df["RIAGENDR"].notna())
    out["pregnant"] = (df.get("RIDEXPRG") == 1).astype(int)

    # --- Kidney ---
    out["scr"] = df["LBXSCR"]  # mg/dL
    out["eGFR"] = ckd_epi_2021(df["LBXSCR"], df["RIDAGEYR"], male)
    out["uACR"] = df["URDACT"]  # mg/g

    # --- Blood pressure: mean of available oscillometric readings ---
    sbp_cols = [c for c in ["BPXOSY1", "BPXOSY2", "BPXOSY3"] if c in df.columns]
    out["sbp"] = df[sbp_cols].mean(axis=1, skipna=True)

    # Antihypertensive use: only asked of those ever told they have
    # hypertension (BPQ020 == 1). Those told "no" are not on BP meds.
    bp_q = "BPQ050A" if "BPQ050A" in df.columns else "BPQ040A"
    bp_meds = yes_no(df[bp_q])
    bp_meds = bp_meds.where(df["BPQ020"] == 1, np.where(df["BPQ020"] == 2, 0.0, np.nan))
    out["bp_meds"] = bp_meds

    # --- Cardiovascular history (self-reported) ---
    out["hf"] = yes_no(df["MCQ160B"])
    chd = yes_no(df["MCQ160C"])
    mi = yes_no(df["MCQ160E"])
    # CHD = coronary heart disease or heart attack
    out["chd"] = np.fmax(chd, mi)
    out["afib"] = 0  # not collected in NHANES

    # --- Smoking ---
    smoked_100 = df["SMQ020"]
    now = df["SMQ040"]  # 1 every day, 2 some days, 3 not at all
    smoking = pd.Series(np.nan, index=df.index, dtype=object)
    smoking[smoked_100 == 2] = "never"
    smoking[(smoked_100 == 1) & now.isin([1, 2])] = "current"
    smoking[(smoked_100 == 1) & (now == 3)] = "former"
    out["smoking"] = smoking

    # --- Body size ---
    out["bmi"] = df["BMXBMI"]

    # --- Diabetes ---
    out["hba1c"] = df["LBXGH"]  # %
    diq010 = df["DIQ010"]  # 1 yes, 2 no, 3 borderline
    insulin = yes_no(df["DIQ050"]).fillna(0)
    oral = yes_no(df["DIQ070"]).fillna(0)
    told_dm = diq010 == 1
    # Diabetes = diagnosed, on diabetes medication, or HbA1c >= 6.5%
    dm = told_dm | (insulin == 1) | (oral == 1) | (df["LBXGH"] >= 6.5)
    dm_known = diq010.isin([1, 2, 3]) | df["LBXGH"].notna()
    out["dm"] = dm.astype(float).where(dm_known)
    out["insulin"] = insulin
    out["oral_dm"] = oral

    return out


def apply_inclusion(df: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    """Adults 20-80, not pregnant, eGFR >= 15, complete model inputs."""
    flow = [("All participants", len(df))]

    df = df[df["age"].between(20, 80)]
    flow.append(("Age 20-80", len(df)))

    df = df[df["pregnant"] == 0]
    flow.append(("Not pregnant", len(df)))

    df = df[df["eGFR"].notna()]
    flow.append(("Serum creatinine available", len(df)))

    df = df[df["eGFR"] >= 15]
    flow.append(("eGFR >= 15 (excludes kidney failure)", len(df)))

    required = ["eGFR", "uACR", "sbp", "bp_meds", "hf", "chd",
                "smoking", "bmi", "dm"]
    df = df.dropna(subset=required)
    df = df[df["uACR"] > 0]
    flow.append(("Complete model inputs", len(df)))

    df = df[~((df["dm"] == 1) & df["hba1c"].isna())]
    flow.append(("HbA1c present if diabetic", len(df)))

    return df.reset_index(drop=True), flow


@app.command()
def main(
    raw_dir: Path = typer.Option(Path("data/raw"), help="Raw files from data_gen.py."),
    out_dir: Path = typer.Option(Path("data/processed"), help="Where to save output."),
    csv: bool = typer.Option(False, "--csv", help="Also save a CSV backup."),
):
    out_dir.mkdir(parents=True, exist_ok=True)

    df = build(load_raw(raw_dir))
    analytic, flow = apply_inclusion(df)

    typer.echo("Inclusion flow:")
    for step, n in flow:
        typer.echo(f"  {step:<40} {n:>7,}")

    path = out_dir / "nhanes_egfr40.parquet"
    analytic.to_parquet(path, index=False)
    if csv:
        analytic.to_csv(out_dir / "nhanes_egfr40.csv", index=False)

    typer.echo(f"\nsaved  {path} ({len(analytic):,} rows)")
    typer.echo(f"  diabetes: {int(analytic['dm'].sum()):,}")
    typer.echo(f"  eGFR < 60: {int((analytic['eGFR'] < 60).sum()):,}")


if __name__ == "__main__":
    app()
