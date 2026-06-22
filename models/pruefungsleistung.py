from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from db.database_setup import Base


class Pruefungsleistung(Base):
    __tablename__ = "pruefungsleistung"

    id = Column(Integer, primary_key=True)
    modul_id = Column(Integer, ForeignKey("modul.id"), nullable=False)
    _note = Column("note", Float, nullable=True)
    bestanden = Column(Boolean, default=False, nullable=False)
    versuch = Column(Integer, default=1, nullable=False)

    @property
    def note(self) -> float | None:
        return self._note

    @note.setter
    def note(self, wert: float | None):
        self._note = wert
        self.bestanden = self.ist_bestanden

    @property
    def ist_bestanden(self) -> bool:
        return self._note is not None and self._note <= 4.0
