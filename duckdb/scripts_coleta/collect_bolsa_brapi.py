from pathlib import Path
import pandas as pd
import yfinance as yf

from utils_paths import DATA_DIR, ensure_dir


def build_output_path(year: int, semester: int, month: int, ticker: str) -> Path:
    folder = (
        DATA_DIR
        / "bolsa"
        / f"empresa={ticker.upper()}"
        / f"ano={year}"
        / f"semestre={semester}"
        / f"mes={month:02d}"
    )
    ensure_dir(folder)
    return folder / f"bolsa_{ticker.lower()}_{year}_{month:02d}.parquet"


def semester_from_month(month: int) -> int:
    return 1 if month <= 6 else 2


def normalize_b3_ticker(ticker: str) -> str:
    """
    No Yahoo Finance, ações da B3 normalmente usam o sufixo .SA
    Ex.: SLCE3 -> SLCE3.SA
    """
    ticker = ticker.upper().strip()
    return ticker if ticker.endswith(".SA") else f"{ticker}.SA"


def fetch_yahoo_history(
    ticker: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    yahoo_ticker = normalize_b3_ticker(ticker)

    # auto_adjust=False para manter OHLC bruto
    df = yf.Ticker(yahoo_ticker).history(
        start=start_date,
        end=end_date,
        auto_adjust=False
    )

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()

    # Alguns ambientes retornam "Date", outros podem vir com timezone
    date_col = "Date" if "Date" in df.columns else df.columns[0]

    df = df.rename(
        columns={
            date_col: "data",
            "Open": "preco_abertura",
            "High": "preco_maximo",
            "Low": "preco_minimo",
            "Close": "preco_fechamento",
            "Volume": "volume",
        }
    )

    df["data"] = pd.to_datetime(df["data"]).dt.tz_localize(None)
    df["ticker"] = ticker.upper().strip()

    colunas_necessarias = [
        "data",
        "ticker",
        "preco_abertura",
        "preco_maximo",
        "preco_minimo",
        "preco_fechamento",
        "volume",
    ]

    df = df[colunas_necessarias].sort_values("data").reset_index(drop=True)

    return df


def save_by_month(df: pd.DataFrame, ticker: str) -> None:
    if df.empty:
        print("Nenhum dado de mercado retornado.")
        return

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["semestre"] = df["mes"].apply(semester_from_month)

    for (ano, semestre, mes), part in df.groupby(["ano", "semestre", "mes"]):
        output_path = build_output_path(ano, semestre, mes, ticker)
        part.drop(columns=["ano", "mes", "semestre"]).to_parquet(output_path, index=False)
        print(f"Salvo: {output_path}")


if __name__ == "__main__":
    ticker = "SLCE3"
    df_bolsa = fetch_yahoo_history(
        ticker=ticker,
        start_date="2025-01-01",
        end_date="2025-07-01",  # end é exclusivo
    )
    save_by_month(df_bolsa, ticker)