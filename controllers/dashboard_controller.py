from models import Modul, Pruefungsleistung, Studium
from repositories.studium_repository import StudiumRepository
from utils.constants import MAX_VERSUCHE
from utils.helpers import naechster_versuch


class DashboardController:
    """Orchestriert den Anwendungsablauf zwischen View, Repository und Modellklassen."""

    def __init__(self, repository: StudiumRepository):
        self.repository = repository
        self.session = repository.session

    def lade_studium(self):
        """Lädt das Studium aus der Datenbank."""
        return self.repository.lade_studium()

    def lade_semester(self):
        """Lädt alle Semester sortiert nach Nummer."""
        return self.repository.lade_semester()

    def lade_freie_module(self):
        """Lädt alle Module, die noch keinem Semester zugeordnet sind."""
        return self.repository.lade_freie_module()

    def lade_module_fuer_semester(self, semester_id: int):
        """Lädt alle Module eines bestimmten Semesters."""
        return self.repository.lade_module_fuer_semester(semester_id)

    def lade_nicht_anerkannte_module(self):
        """Lädt alle Module, die noch nicht anerkannt wurden."""
        return self.repository.lade_nicht_anerkannte_module()

    def aktualisiere_ziele(
        self,
        studium: Studium,
        beginn,
        dauer: int,
        zielnote: float,
    ) -> None:
        """Speichert Studienziele und berechnet den monatlichen ECTS-Soll-Wert."""
        studium.studium_beginn = beginn
        studium.abschluss_dauer = int(dauer)
        studium.ziel_note = float(zielnote)
        studium.ects_pro_monat = studium.gesamt_ects / float(dauer)

        self.repository.speichern(studium)

    def speichere_anerkannte_module(
        self,
        nicht_anerkannte_module: list[Modul],
        selected_module_ids: list[int],
    ) -> None:
        """Markiert ausgewählte Module als anerkannt und ordnet sie Semester 1 zu, falls noch nicht zugeordnet."""
        for modul in nicht_anerkannte_module:
            if modul.id in selected_module_ids:
                modul.anerkannt = True
                if modul.semester_id is None:
                    modul.semester_id = 1  

        self.repository.speichern(*nicht_anerkannte_module)

    def ordne_module_semester_zu(
        self,
        freie_module: list[Modul],
        selected_ids: set[int],
        semester_id: int,
    ) -> None:
        """Ordnet ausgewählte Module einem bestimmten Semester zu."""
        for modul in freie_module:
            if modul.id in selected_ids:
                modul.semester_id = semester_id

        self.repository.speichern(*freie_module)

    def speichere_pruefungsleistung(
        self,
        modul: Modul,
        pruefungsform: str,
        note: float,
    ) -> tuple[bool, str | None]:
        """Legt einen neuen Prüfungsversuch an, sofern die maximale Versuchsanzahl nicht überschritten ist."""
        modul.setPruefungsform(pruefungsform)

        versuch = naechster_versuch(self.session, modul.id)
        if versuch > MAX_VERSUCHE:
            return False, "Maximale Anzahl an Versuchen erreicht."

        pl = Pruefungsleistung(modul_id=modul.id, versuch=versuch)
        pl.note = float(note)

        self.repository.speichern(modul, pl)
        return True, None