import datetime as dt

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from controllers.dashboard_controller import DashboardController
from models import Studium
from utils.charts import donut_ects, grade_semi, stacked_progress
from utils.constants import GER_MONTHS, PRUEFUNGSFORMEN
from utils.helpers import (
    format_note,
    modul_hat_bestandene_leistung,
    modul_letzte_note,
    naechster_versuch,
    parse_grade,
)


class DashboardView:
    """
    Kapselt die Benutzerinteraktion und UI-Logik des Dashboards.
    """

    def __init__(self, controller: DashboardController):
        self.controller = controller
        self.session = controller.session

    @staticmethod
    def german_month_year(d: dt.date) -> str:
        return f"{GER_MONTHS[d.month - 1]} {d.year}"

    def zeige_ziel_dialog(self, studium: Studium):
        @st.dialog("Ziele festlegen", width="large")
        def _dialog():
            beginn_default = studium.studium_beginn or dt.date.today()
            dauer_default = (
                int(studium.abschluss_dauer)
                if studium.abschluss_dauer is not None
                else 36
            )
            zielnote_default = (
                float(studium.ziel_note)
                if studium.ziel_note is not None
                else 1.7
            )

            beginn = st.date_input("Studienbeginn", value=beginn_default)
            dauer = st.number_input(
                "Geplante Studiendauer (Monate)",
                value=dauer_default,
                min_value=6,
                max_value=120,
                step=1,
            )
            zielnote = st.number_input(
                "Ziel-Ø-Note",
                value=zielnote_default,
                min_value=1.0,
                max_value=5.0,
                step=0.1,
                format="%.1f",
            )

            ects_monat = studium.gesamt_ects / float(dauer) if dauer else 0
            st.markdown(
                f"**ECTS pro Monat: {str(round(ects_monat, 1)).replace('.', ',')}**"
            )

            st.divider()
            st.subheader("Anerkannte Module")
            st.caption("Wähle hier Module aus, die dir bereits offiziell anerkannt wurden.")

            nicht_anerkannt = self.controller.lade_nicht_anerkannte_module()

            selected_module_ids: list[int] = []
            if nicht_anerkannt:
                selected_module_ids = st.multiselect(
                    "Anerkannte Module",
                    options=[m.id for m in nicht_anerkannt],
                    format_func=lambda modul_id: next(
                        f"{m.titel} ({m.modul_ects} ECTS)"
                        for m in nicht_anerkannt
                        if m.id == modul_id
                    ),
                    default=[],
                    placeholder="Module auswählen",
                )
            else:
                st.info("Es sind keine weiteren Module zur Anerkennung verfügbar.")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Speichern", use_container_width=True):
                    self.controller.aktualisiere_ziele(
                        studium, beginn, int(dauer), float(zielnote)
                    )
                    self.controller.speichere_anerkannte_module(
                        nicht_anerkannt, selected_module_ids
                    )
                    st.rerun()

            with c2:
                if st.button("Abbrechen", use_container_width=True):
                    st.rerun()

        _dialog()

    def zeige_fortschritt_charts(self, studium: Studium):
        """Zeigt Fortschrittsbalken, ECTS-Donut und Notendiagramm."""
        today = dt.date.today()
        if studium.studium_beginn and studium.abschluss_dauer:
            ist = studium.ectsIst(self.session)
            soll = studium.ectsSoll(today)
        else:
            ist = 0
            soll = 0

        total = studium.gesamt_ects
        avg = (
            studium.durchschnittsNote(self.session)
            if studium.ziel_note is not None
            else None
        )

        st.plotly_chart(
            stacked_progress(total, ist, soll),
            use_container_width=True,
            config={"displayModeBar": False, "staticPlot": True},
        )
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**ECTS-Fortschritt**")
            st.plotly_chart(
                donut_ects(ist, total, soll),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with c2:
            ziel_text = (
                format_note(studium.ziel_note)
                if studium.ziel_note is not None
                else "–"
            )
            st.markdown(f"**Durchschnittsnote – Ziel {ziel_text}**")
            st.plotly_chart(
                grade_semi(avg, ziel=studium.ziel_note),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    def zeige_semester_auswahl(self):
        """Zeigt Semesterauswahl und Formular zur Modulzuordnung. Gibt gewähltes Semester zurück."""
        st.subheader("Semester wählen & Module zuordnen")
        semester_liste = self.controller.lade_semester()
        sem_nummern = [sem.nummer for sem in semester_liste]

        sel_num = st.selectbox("Aktuelles Semester", options=sem_nummern, index=0)
        sel_sem = next(sem for sem in semester_liste if sem.nummer == sel_num)

        freie_module = self.controller.lade_freie_module()
        frei_labels = [f"{m.titel} ({m.modul_ects} ECTS)" for m in freie_module]
        st.write("Wähle Module, die du in diesem Semester belegen willst:")

        with st.form("zuordnung_form"):
            pick = st.multiselect(
                "Verfügbare Module",
                options=frei_labels,
                default=[],
                placeholder="Module auswählen",
            )
            submitted = st.form_submit_button("Speichern")

            if submitted and pick:
                pick_ids = {
                    freie_module[i].id
                    for i, label in enumerate(frei_labels)
                    if label in pick
                }
                self.controller.ordne_module_semester_zu(
                    freie_module,
                    pick_ids,
                    sel_sem.id,
                )
                st.rerun()

        return sel_sem

    def zeige_modul_liste(self, sel_sem):
        """Zeigt die Liste der einem Semester zugeordneten Module mit Noteneingabe."""
        st.divider()
        st.subheader(f"Semester {sel_sem.nummer}: gewählte Module")
        sem_modules = self.controller.lade_module_fuer_semester(sel_sem.id)

        if not sem_modules:
            st.info("Noch keine Module zugeordnet. Wähle oben Module und speichere.")
            return

        abgeschlossen_count = sum(
            1
            for m in sem_modules
            if (m.anerkannt or modul_hat_bestandene_leistung(self.session, m.id))
        )
        st.write(f"Fortschritt: **{abgeschlossen_count} / {len(sem_modules)} Module**")
        st.caption(
            f"Erreichte ECTS in diesem Semester: **{sel_sem.erreichteEctsSem(self.session)}**"
        )

        narrow = st.session_state.get("narrow_mode", False)

        for m in sem_modules:
            edit_key = f"edit_m{m.id}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            if m.anerkannt:
                c_chk, c_title, c_ects, c_form, c_actions = st.columns(
                    [0.05, 0.43, 0.08, 0.22, 0.22]
                )

                with c_chk:
                    st.checkbox(
                        "Bestanden",
                        value=True,
                        key=f"chk_m{m.id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )

                with c_title:
                    st.markdown(
                        f"<div style='padding-top:6px'>{m.titel} <i>(anerkannt)</i></div>",
                        unsafe_allow_html=True,
                    )

                with c_ects:
                    st.markdown(
                        f"<div style='padding-top:6px'>{m.modul_ects} ECTS</div>",
                        unsafe_allow_html=True,
                    )

                with c_form:
                    st.write("")

                with c_actions:
                    st.write("")

                continue

            bestanden = modul_hat_bestandene_leistung(self.session, m.id)
            gespeicherte_note = modul_letzte_note(self.session, m.id)

            if narrow:
                with st.container(border=True):
                    st.markdown(f"**{m.titel}**  ({m.modul_ects} ECTS)")

                    col1, col2, col3 = st.columns([0.3, 0.35, 0.35])

                    with col1:
                        st.checkbox(
                            "Bestanden",
                            value=bool(bestanden),
                            key=f"chk_m{m.id}",
                            disabled=True,
                            label_visibility="collapsed",
                        )

                    with col2:
                        pf_key = f"pf_{m.id}"
                        current_pf = m.pruefungsform or PRUEFUNGSFORMEN[0]
                        pf_select = st.selectbox(
                            "Prüfungsform",
                            PRUEFUNGSFORMEN,
                            index=PRUEFUNGSFORMEN.index(current_pf)
                            if current_pf in PRUEFUNGSFORMEN
                            else 0,
                            key=pf_key,
                            label_visibility="collapsed",
                            disabled=bool(bestanden),
                        )

                    with col3:
                        note_raw = st.text_input(
                            "Noteingabe",
                            value="",
                            placeholder="Note",
                            key=f"note_input_{m.id}",
                            label_visibility="collapsed",
                        )

                        if st.button(
                            "save",
                            key=f"save_{m.id}",
                            use_container_width=True,
                            help="Speichern",
                        ):
                            parsed = parse_grade(note_raw)
                            if parsed is None:
                                st.warning(
                                    "Bitte eine gültige Note zwischen 1,0 und 5,0 eingeben."
                                )
                            else:
                                ok, fehler = self.controller.speichere_pruefungsleistung(
                                    modul=m,
                                    pruefungsform=pf_select,
                                    note=float(parsed),
                                )
                                if not ok:
                                    st.error(fehler)
                                else:
                                    st.rerun()

                    if bestanden and gespeicherte_note is not None:
                        st.markdown(
                            f"**Bestanden:** {format_note(gespeicherte_note)}"
                        )

            else:
                c_chk, c_title, c_ects, c_form, c_actions = st.columns(
                    [0.05, 0.43, 0.08, 0.22, 0.22]
                )

                with c_chk:
                    st.checkbox(
                        "Bestanden",
                        value=bool(bestanden),
                        key=f"chk_m{m.id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )

                with c_title:
                    st.markdown(
                        f"<div style='padding-top:8px'>{m.titel}</div>",
                        unsafe_allow_html=True,
                    )

                with c_ects:
                    st.markdown(
                        f"<div style='padding-top:8px'>{m.modul_ects} ECTS</div>",
                        unsafe_allow_html=True,
                    )

                with c_form:
                    pf_key = f"pf_{m.id}"
                    current_pf = m.pruefungsform or PRUEFUNGSFORMEN[0]
                    pf_select = st.selectbox(
                        "Prüfungsform",
                        PRUEFUNGSFORMEN,
                        index=PRUEFUNGSFORMEN.index(current_pf)
                        if current_pf in PRUEFUNGSFORMEN
                        else 0,
                        key=pf_key,
                        label_visibility="collapsed",
                        disabled=bool(bestanden),
                    )

                with c_actions:
                    if gespeicherte_note is not None and not st.session_state[edit_key]:
                        aktueller_versuch = naechster_versuch(self.session, m.id) - 1
                        left_note, right_btn = st.columns([0.6, 0.4])

                        with left_note:
                            if bestanden:
                                st.markdown(
                                    f"**Note:** {format_note(gespeicherte_note)}"
                                )
                            else:
                                st.markdown(
                                    f"**{aktueller_versuch}. Versuch:** {format_note(gespeicherte_note)}"
                                )

                        with right_btn:
                            if st.button(
                                "edit",
                                key=f"editbtn_{m.id}",
                                use_container_width=True,
                                help="Neuen Versuch anlegen",
                            ):
                                st.session_state[edit_key] = True
                                st.rerun()

                    else:
                        col_input, col_btn = st.columns([0.6, 0.4])

                        with col_input:
                            note_raw = st.text_input(
                                "Noteingabe",
                                value="",
                                placeholder="Note",
                                key=f"note_input_{m.id}",
                                label_visibility="collapsed",
                            )

                        with col_btn:
                            if st.button(
                                "save",
                                key=f"save_{m.id}",
                                use_container_width=True,
                                help="Speichern",
                            ):
                                parsed = parse_grade(note_raw)
                                if parsed is None:
                                    st.warning(
                                        "Bitte eine gültige Note zwischen 1,0 und 5,0 eingeben."
                                    )
                                else:
                                    ok, fehler = self.controller.speichere_pruefungsleistung(
                                        modul=m,
                                        pruefungsform=pf_select,
                                        note=float(parsed),
                                    )
                                    if not ok:
                                        st.error(fehler)
                                    else:
                                        st.session_state[edit_key] = False
                                        st.rerun()

    def zeige_dashboard(self):
        st.set_page_config(page_title="Studien-Dashboard", layout="wide")

        width = streamlit_js_eval(js_expressions="screen.width")
        st.session_state["narrow_mode"] = bool(width and width < 1600)

        studium = self.controller.lade_studium()

        left, right = st.columns([0.75, 0.25])

        with left:
            st.title("Dashboard")
            if studium and studium.abschluss_ziel:
                st.subheader(
                    f"Geplanter Abschluss {self.german_month_year(studium.abschluss_ziel)}"
                )

        with right:
            if studium and st.button("Ziele einstellen", use_container_width=True):
                self.zeige_ziel_dialog(studium)

        if studium is None:
            st.error("Es konnte kein Studium geladen werden.")
            return

        if (
            studium.studium_beginn is None
            or studium.abschluss_dauer is None
            or studium.ziel_note is None
        ):
            st.info("Bitte lege zuerst deine Studienziele fest.")

        self.zeige_fortschritt_charts(studium)
        sel_sem = self.zeige_semester_auswahl()
        self.zeige_modul_liste(sel_sem)
