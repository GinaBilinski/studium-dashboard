from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from db.database_setup import Base


class Pruefungsleistung(Base):
    """Repräsentiert einen Prüfungsversuch eines Moduls mit Note und Bestandenstatus."""

    __tablename__ = "pruefungsleistung"

    id = Column(Integer, primary_key=True)
    modul_id = Column(Integer, ForeignKey("modul.id"), nullable=False)
    _note = Column("note", Float, nullable=True)  # Intern gespeichert, Zugriff über Property note
    bestanden = Column(Boolean, default=False, nullable=False)
    versuch = Column(Integer, default=1, nullable=False)

    @property
    def note(self) -> float | None:
        """Gibt die Note des Prüfungsversuchs zurück."""
        return self._note

    @note.setter
    def note(self, wert: float | None):
        """Setzt die Note und aktualisiert automatisch den Bestandenstatus."""
        self._note = wert
        self.bestanden = self.ist_bestanden

    @property
    def ist_bestanden(self) -> bool:
        """Gibt True zurück, wenn eine Note vorhanden ist und diese 4,0 oder besser ist."""
        return self._note is not None and self._note <= 4.0
