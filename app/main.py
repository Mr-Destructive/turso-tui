import json
import os

import requests

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, ListItem, DataTable


class TursoTUI(App):
    """A Textual app to interact with Turso database."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    BASE_URL = "https://api.turso.tech/v1"
    API_TOKEN = ""
    ORG_SLUG = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        # for org in self.list_orgs():
        #    yield ListItem(Label(org))
        yield DataTable(id="dbs")
        yield DataTable(id="db-stats")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query("#dbs")[0]
        table.add_columns("Name", "Regions", "Type", "Version", "Group")
        table.add_rows(self.list_dbs())
        tableInfo = self.query("#db-stats")[0]
        tableInfo.add_columns("Query", "Rows Read", "Rows Written")
        tableInfo.add_rows(self.db_info(""))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def load_auth(self):
        """Load authentication token."""
        load_dotenv()
        self.API_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")
        self.ORG_SLUG = os.environ.get("TURSO_ORG_SLUG")

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

    def list_dbs(self):
        """List databases."""
        dbs = self.call_api(f"organizations/{self.ORG_SLUG}/databases")
        db_list = [
            (
                db["Name"],
                db["primaryRegion"],
                db["type"],
                db["version"],
                db.get("group"),
            )
            for db in dbs.json()["databases"]
        ]
        return db_list

    def db_usage(self, db_slug):
        """Get database usage."""
        resp = self.call_api(f"organizations/{self.ORG_SLUG}/databases/{db_slug}/usage")
        db_usage = [(k, v) for k, v in resp.json()["total"].items()]
        return db_usage

    def db_stats(self, db_slug):
        """Get database stats."""
        resp = self.call_api(f"organizations/{self.ORG_SLUG}/databases/{db_slug}/stats")
        db_stats = [
            (row["query"], row["rows_read"], row["rows_written"])
            for row in resp.json().get("top_queries", [])
        ]
        return db_stats

    def db_instances(self, db_slug):
        """Get database instances."""
        resp = self.call_api(
            f"organizations/{self.ORG_SLUG}/databases/{db_slug}/instances"
        )
        db_instances = [
            ("instance_uuid", row["uuid"]) for row in resp.json()["instances"]
        ]
        return db_instances

    def db_info(self, db_slug):
        db_usage = self.db_usage(db_slug)
        db_stats = self.db_stats(db_slug)
        return db_usage + db_stats


if __name__ == "__main__":
    app = TursoTUI()
    app.run()
