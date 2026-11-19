"""Data da última montagem do site e período mais recente de cada fonte."""
import glob
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

DADOS = Path(__file__).resolve().parents[2] / "data"


def ultimo(pasta):
    arqs = sorted(glob.glob(str(DADOS / pasta / "*.csv")))
    return Path(arqs[-1]).stem.rsplit("_", 1)[-1] if arqs else None


ms = timezone(timedelta(hours=-4))
print(json.dumps({
    "gerado_em": datetime.now(ms).strftime("%d/%m/%Y %H:%M"),
    "pam": ultimo("ibge/pam/lavouras"),
    "ppm": ultimo("ibge/ppm/rebanhos"),
    "pevs": ultimo("ibge/pevs/area_silvicultura"),
    "lspa": ultimo("ibge/lspa/estimativa_safra"),
}, ensure_ascii=False))
