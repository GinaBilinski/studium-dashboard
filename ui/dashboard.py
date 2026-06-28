from sqlalchemy.orm import Session
from controllers.dashboard_controller import DashboardController
from db.database_setup import engine, seed_if_empty
from repositories.studium_repository import StudiumRepository
from ui.dashboard_view import DashboardView

def render_dashboard():
    seed_if_empty()

    with Session(engine) as session:
        repository = StudiumRepository(session)
        controller = DashboardController(repository)
        view = DashboardView(controller)
        view.zeige_dashboard()