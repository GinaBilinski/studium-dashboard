from sqlalchemy import func, exists
from db.database_setup import Session
from models.pruefungsleistung import Pruefungsleistung
from utils.constants import MAX_VERSUCHE


def parse_grade(text: str) -> float | None:
    if not text:
        return None
    s = text.strip().replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return round(v, 1) if 1.0 <= v <= 5.0 else None


def modul_hat_bestandene_leistung(session: Session, modul_id: int) -> bool:
    return session.query(exists().where(
        (Pruefungsleistung.modul_id == modul_id) & (Pruefungsleistung.bestanden.is_(True))
    )).scalar()


def modul_letzte_note(session: Session, modul_id: int) -> float | None:
    row = (
        session.query(Pruefungsleistung._note)
        .filter(Pruefungsleistung.modul_id == modul_id)
        .order_by(Pruefungsleistung.versuch.desc(), Pruefungsleistung.id.desc())
        .first()
    )
    return None if row is None else row[0]


def naechster_versuch(session: Session, modul_id: int) -> int:
    cur = (
        session.query(func.coalesce(func.max(Pruefungsleistung.versuch), 0))
        .filter(Pruefungsleistung.modul_id == modul_id)
        .scalar()
    )
    return int(cur or 0) + 1

def format_note(note: float) -> str:
    return f"{note:.1f}".replace(".", ",")