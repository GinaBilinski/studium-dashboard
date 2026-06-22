from models import Modul, Pruefungsleistung, Studium
from repositories.studium_repository import StudiumRepository
from utils.constants import MAX_VERSUCHE
from utils.helpers import naechster_versuch


class DashboardController:
    """
    Orchestriert Benutzeraktionen des Dashboards.
    Die fachlichen Berechnungen bleiben in den Modellen
    bzw. in Hilfsfunktionen.
    """

    def __init__(self, repository: StudiumRepository):
        self.repository = repository
        self.session = repository.session

    # Lesezugriffe laufen über den Controller, damit die View
    # nicht direkt auf das Repository zugreifen muss.

    def lade_studium(self):
        return self.repository.lade_studium()

    def lade_semester(self):
        return self.repository.lade_semester()

    def lade_freie_module(self):
        return self.repository.lade_freie_module()

    def lade_module_fuer_semester(self, semester_id: int):
        return self.repository.lade_module_fuer_semester(semester_id)

    def lade_nicht_anerkannte_module(self):
        return self.repository.lade_nicht_anerkannte_module()

    def aktualisiere_ziele(
        self,
        studium: Studium,
        beginn,
        dauer: int,
        zielnote: float,
    ) -> None:
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
        modul.setPruefungsform(pruefungsform)

        versuch = naechster_versuch(self.session, modul.id)
        if versuch > MAX_VERSUCHE:
            return False, "Maximale Anzahl an Versuchen erreicht."

        pl = Pruefungsleistung(modul_id=modul.id, versuch=versuch)
        pl.note = float(note)

        self.repository.speichern(modul, pl)
        return True, None