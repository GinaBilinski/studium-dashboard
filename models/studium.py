from sqlalchemy import Column, Integer, Float, Date, func, select, exists, or_
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
import datetime as dt
from db.database_setup import Base
from models.modul import Modul
from models.pruefungsleistung import Pruefungsleistung


class Studium(Base):
    __tablename__ = "studium"

    id = Column(Integer, primary_key=True)
    gesamt_ects = Column(Integer, default=180, nullable=False)
    studium_beginn = Column(Date, nullable=True)
    abschluss_dauer = Column(Integer, nullable=True)
    ects_pro_monat = Column(Float, nullable=True)
    ziel_note = Column(Float, nullable=True)

    @property
    def abschluss_ziel(self) -> dt.date | None:
        if self.studium_beginn is None or self.abschluss_dauer is None:
            return None
        return self.studium_beginn + relativedelta(months=self.abschluss_dauer)

    def ectsSoll(self, bis_datum: dt.date) -> float:
        if self.studium_beginn is None or self.abschluss_ziel is None or self.ects_pro_monat is None:
            return 0
        stop = min(bis_datum, self.abschluss_ziel)
        months = max(0, (stop.year - self.studium_beginn.year) * 12 + (stop.month - self.studium_beginn.month))
        return months * self.ects_pro_monat

    def ectsIst(self, session: Session) -> int:
        subq_bestanden = (
            select(Pruefungsleistung.id)
            .where((Pruefungsleistung.modul_id == Modul.id) & (Pruefungsleistung.bestanden.is_(True)))
            .limit(1)
        )
        total = (
            session.query(func.coalesce(func.sum(Modul.modul_ects), 0))
            .filter(or_(Modul.anerkannt.is_(True), exists(subq_bestanden)))
            .scalar()
        )
        return int(total or 0)

    def durchschnittsNote(self, session: Session) -> float | None:
        rows = (
            session.query(Pruefungsleistung._note, Modul.modul_ects)
            .join(Modul, Modul.id == Pruefungsleistung.modul_id)
            .filter(Pruefungsleistung.bestanden.is_(True), Modul.anerkannt.is_(False))
            .all()
        )
        if not rows:
            return None
        z = sum(note * ects for note, ects in rows if note is not None)
        n = sum(ects for note, ects in rows if note is not None)
        return round(z / n, 2) if n else None