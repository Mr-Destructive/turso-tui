import json
import os

import requests

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, ListItem


class TursoTUI(App):
    """A Textual app to interact with Turso database."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    API_TOKEN = ""
    BASE_URL = "https://api.turso.tech/v1"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        for org in self.list_orgs():
            yield ListItem(Label(org))
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def load_auth(self):
        """Load authentication token."""
        load_dotenv()
        self.API_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

    def call_api(self, endpoint: str):
        url = f"{self.BASE_URL}/{endpoint}"
        self.load_auth()
        res = requests.get(url, headers={"Authorization": f"Bearer {self.API_TOKEN}"})
        return res

    def list_orgs(self):
        """List organizations."""
        orgs = self.call_api("organizations")
        org_list = [org["slug"] for org in orgs.json()]
        return org_list


if __name__ == "__main__":
    app = TursoTUI()
    app.run()
