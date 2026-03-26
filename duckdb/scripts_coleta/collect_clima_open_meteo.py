from pathlib import Path
import requests
import pandas as pd

from utils_paths import DATA_DIR, ensure_dir


def build_output_path(year: int, semester: int, month: int, city_slug: str) -> Path:
    folder = (
        DATA_DIR
        / "clima"
        / f"ano={year}"
        / f"semestre={semester}"
        / f"mes={month:02d}"
    )
    ensure_dir(folder)
    return folder / f"clima_{city_slug}_{year}_{month:02d}.parquet"


def semester_from_month(month: int) -> int:
    return 1 if month <= 6 else 2


def fetch_clima_open_meteo(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    cidade: str,
    estado: str = "MT",
) -> pd.DataFrame:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "America/Cuiaba",
        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    daily = data.get("daily", {})
    df = pd.DataFrame(
        {
            "data": pd.to_datetime(daily.get("time", [])),
            "estado": estado,
            "cidade": cidade,
            "latitude": latitude,
            "longitude": longitude,
            "temperatura_media": daily.get("temperature_2m_mean", []),
            "temperatura_maxima": daily.get("temperature_2m_max", []),
            "temperatura_minima": daily.get("temperature_2m_min", []),
            "precipitacao_mm": daily.get("precipitation_sum", []),
            "velocidade_vento": daily.get("wind_speed_10m_max", []),
        }
    )

    return df


def save_by_month(df: pd.DataFrame, city_slug: str) -> None:
    if df.empty:
        print("Nenhum dado climático retornado.")
        return

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["semestre"] = df["mes"].apply(semester_from_month)

    for (ano, semestre, mes), part in df.groupby(["ano", "semestre", "mes"]):
        output_path = build_output_path(ano, semestre, mes, city_slug)
        part.drop(columns=["ano", "mes", "semestre"]).to_parquet(output_path, index=False)
        print(f"Salvo: {output_path}")


if __name__ == "__main__":
    # Exemplo: Sorriso - MT
    latitude = -12.5458
    longitude = -55.7114
    cidade = "Sorriso"
    city_slug = "sorriso"

    df_clima = fetch_clima_open_meteo(
        latitude=latitude,
        longitude=longitude,
        start_date="2025-01-01",
        end_date="2025-06-30",
        cidade=cidade,
        estado="MT",
    )

    save_by_month(df_clima, city_slug)