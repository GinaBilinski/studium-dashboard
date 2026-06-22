from sqlalchemy.orm import Session

from models import Modul, Semester, Studium


class StudiumRepository:
    """
    Kapselt den Datenzugriff für das Dashboard.
    Enthält bewusst keine Geschäftslogik.
    """

    def __init__(self, session: Session):
        self.session = session

    def lade_studium(self) -> Studium | None:
        return self.session.query(Studium).first()

    def lade_semester(self) -> list[Semester]:
        return self.session.query(Semester).order_by(Semester.nummer).all()

    def lade_freie_module(self) -> list[Modul]:
        return (
            self.session.query(Modul)
            .filter(Modul.semester_id.is_(None))
            .order_by(Modul.id)
            .all()
        )

    def lade_module_fuer_semester(self, semester_id: int) -> list[Modul]:
        return (
            self.session.query(Modul)
            .filter(Modul.semester_id == semester_id)
            .order_by(Modul.id)
            .all()
        )

    def lade_nicht_anerkannte_module(self) -> list[Modul]:
        return (
            self.session.query(Modul)
            .filter(Modul.anerkannt.is_(False))
            .order_by(Modul.id)
            .all()
        )

    def speichern(self, *objekte) -> None:
        for obj in objekte:
            if obj is not None:
                self.session.add(obj)
        self.session.commit()