from sqlalchemy import func, exists
from db.database_setup import Session
from models.pruefungsleistung import Pruefungsleistung
from utils.constants import MAX_VERSUCHE


def parse_grade(text: str) -> float | None:
    """Wandelt eine Texteingabe in eine gültige Note (1,0–5,0) um. Gibt None zurück bei ungültiger Eingabe."""
    if not text:
        return None
    s = text.strip().replace(",", ".")  # Komma durch Punkt ersetzen für float-Konvertierung
    try:
        v = float(s)
    except ValueError:
        return None
    return round(v, 1) if 1.0 <= v <= 5.0 else None


def modul_hat_bestandene_leistung(session: Session, modul_id: int) -> bool:
    """Gibt True zurück, wenn das Modul mindestens eine bestandene Prüfungsleistung hat."""
    return session.query(exists().where(
        (Pruefungsleistung.modul_id == modul_id) & (Pruefungsleistung.bestanden.is_(True))
    )).scalar()


def modul_letzte_note(session: Session, modul_id: int) -> float | None:
    """Gibt die Note des letzten Prüfungsversuchs eines Moduls zurück."""
    row = (
        session.query(Pruefungsleistung._note)
        .filter(Pruefungsleistung.modul_id == modul_id)
        .order_by(Pruefungsleistung.versuch.desc(), Pruefungsleistung.id.desc())  # Neuester Versuch zuerst
        .first()
    )
    return None if row is None else row[0]


def naechster_versuch(session: Session, modul_id: int) -> int:
    """Gibt die Nummer des nächsten Prüfungsversuchs für ein Modul zurück."""
    cur = (
        session.query(func.coalesce(func.max(Pruefungsleistung.versuch), 0))
        .filter(Pruefungsleistung.modul_id == modul_id)
        .scalar()
    )
    return int(cur or 0) + 1  # Höchster bisheriger Versuch + 1


def format_note(note: float) -> str:
    """Formatiert eine Note mit einer Nachkommastelle und deutschem Komma (z. B. 1,7)."""
    return f"{note:.1f}".replace(".", ",")