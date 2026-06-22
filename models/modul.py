from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.database_setup import Base
from models.pruefungsform import Pruefungsform


class Modul(Base):
    __tablename__ = "modul"

    id = Column(Integer, primary_key=True)
    titel = Column(String, nullable=False)
    modul_ects = Column(Integer, default=5, nullable=False)
    pruefungsform = Column(String, default=Pruefungsform.KLAUSUR.value, nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=True)
    anerkannt = Column(Boolean, default=False, nullable=False)

    pruefungsleistungen = relationship("Pruefungsleistung", backref="modul", cascade="all, delete-orphan")

    def setPruefungsform(self, form: str):
        gueltige_werte = {pf.value for pf in Pruefungsform}
        if form in gueltige_werte:
            self.pruefungsform = form