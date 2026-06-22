from sqlalchemy import Column, Integer, func, select, exists, or_
from sqlalchemy.orm import Session
from db.database_setup import Base
from models.modul import Modul
from models.pruefungsleistung import Pruefungsleistung


class Semester(Base):
    __tablename__ = "semester"

    id = Column(Integer, primary_key=True)
    nummer = Column(Integer, nullable=False)

    def erreichteEctsSem(self, session: Session) -> int:
        subq_bestanden = (
            select(Pruefungsleistung.id)
            .where((Pruefungsleistung.modul_id == Modul.id) 
            & (Pruefungsleistung.bestanden.is_(True))
            )
            .limit(1)
        )
        total = (
            session.query(func.coalesce(func.sum(Modul.modul_ects), 0))
            .filter(Modul.semester_id == self.id,
                    or_(Modul.anerkannt.is_(True), exists(subq_bestanden)))
            .scalar()
        )
        return int(total or 0)