import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import notifier
import scraper


class WeeklyAgendaTests(unittest.TestCase):
    def test_reads_wednesday_events_and_weekly_outlook(self):
        day = scraper.obtener_noticias_del_dia("2026-10-28")

        self.assertIsNotNone(day)
        self.assertEqual(day["dia"], "miercoles")
        self.assertIn("FOMC", day["panorama_semanal"])
        self.assertTrue(any("decisión de tasas" in item["evento"].lower() for item in day["noticias"]))

    def test_does_not_reuse_events_from_an_old_week(self):
        self.assertIsNone(scraper.obtener_noticias_del_dia("2026-11-02"))

    @patch(
        "scraper.ahora_local",
        return_value=datetime(2026, 10, 28, 12, 30, tzinfo=ZoneInfo("America/Bogota")),
    )
    def test_finds_fomc_events_thirty_minutes_ahead(self, _mock_now):
        upcoming = scraper.obtener_proxima_noticia()

        self.assertIsNotNone(upcoming)
        self.assertEqual(upcoming["minutos"], 30)
        self.assertEqual(upcoming["noticia"]["hora"], "13:00")
        self.assertGreaterEqual(len(upcoming["noticias"]), 2)

    def test_pre_alert_logs_projection_without_calling_telegram(self):
        event = {
            "fecha": "2026-10-28",
            "hora": "13:00",
            "evento": "Prueba FOMC",
            "prevision": "4.00%",
            "anterior": "4.00%",
            "tu_analisis": "Proyección de prueba",
            "escenario_alcista": "Escenario alcista de prueba",
            "escenario_bajista": "Escenario bajista de prueba",
        }

        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root) as folder:
            log_path = Path(folder) / "forecast_history.jsonl"
            with (
                patch.object(notifier, "FORECAST_LOG", str(log_path)),
                patch.object(notifier.TelegramNotifier, "enviar_mensaje", return_value=True) as send,
            ):
                sent = notifier.TelegramNotifier().enviar_alerta_pre_noticia(event, minutos=30)

            self.assertTrue(sent)
            send.assert_called_once()
            record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(record["evento"], "Prueba FOMC")
            self.assertEqual(record["consenso"], "4.00%")


if __name__ == "__main__":
    unittest.main()
