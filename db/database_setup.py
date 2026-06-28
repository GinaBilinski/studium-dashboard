from sqlalchemy import create_engine, text, func, exists
from sqlalchemy.orm import Session, declarative_base
from pathlib import Path

Base = declarative_base()
DB_PATH = Path("studium.db")  # Datenbankdatei im Projektverzeichnis
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)


def migrate_schema():
    """Erstellt fehlende Tabellen und migriert alte Datenbankstrukturen."""
    from models.modul import Modul
    from models.pruefungsleistung import Pruefungsleistung

    Base.metadata.create_all(engine)
    with Session(engine) as s:
        # Prüfen ob alte Spalten note/bestanden in der Modul-Tabelle existieren
        cols = {c[1] for c in s.execute(text("PRAGMA table_info(modul)")).fetchall()}
        has_note = "note" in cols
        has_bestanden = "bestanden" in cols
        if has_note or has_bestanden:
            # Alte Daten auslesen und in Pruefungsleistung-Einträge umwandeln
            rows = s.execute(text("SELECT id, COALESCE(bestanden, 0) AS b, note FROM modul")).fetchall()
            for mid, b_alt, note_alt in rows:
                exists_pl = s.query(
                    exists().where(Pruefungsleistung.modul_id == mid)
                ).scalar()
                if (b_alt or note_alt is not None) and not exists_pl:
                    pl = Pruefungsleistung(
                        modul_id=mid,
                        versuch=1,
                        note=note_alt,
                        bestanden=bool(b_alt or (note_alt is not None and note_alt <= 4.0)),
                    )
                    s.add(pl)
            s.commit()


def seed_if_empty():
    """Befüllt eine leere Datenbank mit Startwerten für Studium, Semester und Module."""
    from models.studium import Studium
    from models.semester import Semester
    from models.modul import Modul

    Base.metadata.create_all(engine)
    migrate_schema()

    with Session(engine) as s:
        # Studium anlegen, falls noch keines vorhanden
        if s.query(func.count(Studium.id)).scalar() == 0:
            s.add(Studium(
                gesamt_ects=180,
                studium_beginn=None,
                abschluss_dauer=None,
                ects_pro_monat=None,
                ziel_note=None,
            ))

        # Sechs Semester anlegen, falls noch keine vorhanden
        if s.query(func.count(Semester.id)).scalar() == 0:
            for i in range(1, 7):
                s.add(Semester(nummer=i))

        # Module des Studiengangs anlegen, falls noch keine vorhanden
        if s.query(func.count(Modul.id)).scalar() == 0:
            demo = [
                ("Grundlagen der industriellen Softwaretechnik", 5),
                ("Einführung in das wissenschaftliche Arbeiten für IT und Technik", 5),
                ("Requirements Engineering", 5),
                ("Spezifikation", 5),
                ("Grundlagen der objektorientierten Programmierung mit Java", 5),
                ("Datenmodellierung und Datenbanksysteme", 5),
                ("Datenstruktur und Java-Klassenbibliothek", 5),
                ("Programmierung von Webanwendungsoberflächen", 5),
                ("Algorithmen, Datenstrukturen und Programmiersprachen", 5),
                ("Qualitätssicherung im Softwareprozess", 5),
                ("IT-Architekturmanagement", 5),
                ("Programmierung von industriellen Informationssystemen mit Java EE", 5),
                ("Ethik und Nachhaltigkeit in der IT", 5),
                ("IT-Projektmanagement", 5),
                ("Techniken und Methoden der agilen Softwareentwicklung", 5),
                ("Mobile Software Engineering am Beispiel der Android-Plattform", 5),
                ("Seminar Software Engineering", 5),
                ("Projekt Agiles Software Engineering", 5),
                ("IT-Infrastruktur", 5),
                ("IT-Service Management", 5),
                ("Projekt Mobile Software Engineering", 5),
                ("Cloud Programming", 5),
                ("Einführung in Datenschutz und IT-Sicherheit", 5),
                ("DevOps und Continuous Delivery", 5),
                ("Gestaltung und Ergonomie von User Interfaces", 5),
                ("Einführung in die Programmierung mit Python", 5),
                ("Projekt: Software Development", 5),
                ("Einführung in Data Science", 5),
                ("Objektorientierte & funktionale Programmierung mit Python", 5),
                ("Mathematik: Lineare Algebra", 5),
                ("Mathematik: Analysis", 5),
                ("Statistical Computing", 5),
                ("Deep Learning", 5),
                ("Kollaboratives Arbeiten", 5),
                ("Bachelorarbeit", 9),
                ("Kolloquium", 1),
            ]
            for titel, ects in demo:
                s.add(Modul(
                    titel=titel, modul_ects=ects,
                    pruefungsform="Klausur",
                    semester_id=None, anerkannt=False
                ))

        s.commit()