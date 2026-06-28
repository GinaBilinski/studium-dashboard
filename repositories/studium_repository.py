from sqlalchemy.orm import Session
from models import Modul, Semester, Studium

class StudiumRepository:
    """Kapselt den Datenzugriff für das Dashboard."""
    def __init__(self, session: Session):
        self.session = session

    def lade_studium(self) -> Studium | None:
        """Gibt das einzige Studium-Objekt aus der Datenbank zurück."""
        return self.session.query(Studium).first()

    def lade_semester(self) -> list[Semester]:
        """Gibt alle Semester sortiert nach Semesternummer zurück."""
        return self.session.query(Semester).order_by(Semester.nummer).all()

    def lade_freie_module(self) -> list[Modul]:
        """Gibt alle Module zurück, die noch keinem Semester zugeordnet sind."""
        return (
            self.session.query(Modul)
            .filter(Modul.semester_id.is_(None))
            .order_by(Modul.id)
            .all()
        )

    def lade_module_fuer_semester(self, semester_id: int) -> list[Modul]:
        """Gibt alle Module eines bestimmten Semesters zurück."""
        return (
            self.session.query(Modul)
            .filter(Modul.semester_id == semester_id)
            .order_by(Modul.id)
            .all()
        )

    def lade_nicht_anerkannte_module(self) -> list[Modul]:
        """Gibt alle Module zurück, die noch nicht als anerkannt markiert sind."""
        return (
            self.session.query(Modul)
            .filter(Modul.anerkannt.is_(False))
            .order_by(Modul.id)
            .all()
        )

    def speichern(self, *objekte) -> None:
        """Fügt alle übergebenen Objekte zur Session hinzu und speichert sie in der Datenbank."""
        for obj in objekte:
            if obj is not None:
                self.session.add(obj)
        self.session.commit()