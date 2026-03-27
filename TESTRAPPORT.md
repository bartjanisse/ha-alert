# Testrapport — HA Alert Integratie

**Datum:** 2026-03-27
**Branch:** main
**Commit:** 7c85486 (+ lokale wijzigingen type-specifieke sensors)
**Python:** 3.13.12
**pytest:** 9.0.2

---

## Samenvatting

| | Aantal |
|---|---|
| Totaal tests | 22 |
| Geslaagd | **22** |
| Gefaald | 0 |
| Overgeslagen | 0 |

---

## Omgeving

De `homeassistant`-package kan op dit Windows-systeem niet volledig geïnstalleerd worden omdat de dependency `lru-dict==1.3.0` een C-compiler vereist die niet beschikbaar is. De tests worden uitgevoerd met gemockte HA-modules via `tests/conftest.py`, waarbij twee kritieke aanpassingen zorgen voor correcte werking:

- **`@callback` als passthrough** — `lambda f: f` zodat gedecoreerde methoden zoals `_notify_listeners` correct blijven werken
- **`dt_util.utcnow` als echte datetime** — retourneert `datetime.now(timezone.utc)` zodat tijdsvergelijkingen en `isoformat()`-aanroepen kloppen

---

## Resultaten per testklasse

### TestCreateAlert — Alert aanmaken

| Test | Resultaat |
|---|---|
| `test_create_minimal_alert` | PASS |
| `test_create_alert_with_title` | PASS |
| `test_create_alert_sets_repeat_interval_in_seconds` | PASS |
| `test_create_alert_without_repeat_has_no_next_repeat` | PASS |
| `test_create_multiple_alerts` | PASS |
| `test_create_alert_notifies_listeners` | PASS |
| `test_create_alert_with_condition_sets_up_listener` | PASS |

### TestDismissAlert — Alert verwijderen

| Test | Resultaat |
|---|---|
| `test_dismiss_existing_alert` | PASS |
| `test_dismiss_nonexistent_alert` | PASS |
| `test_dismiss_notifies_listeners` | PASS |
| `test_dismiss_cleans_up_condition_listener` | PASS |

### TestAcknowledgeAlert — Alert bevestigen

| Test | Resultaat |
|---|---|
| `test_acknowledge_existing_alert` | PASS |
| `test_acknowledge_nonexistent_alert` | PASS |
| `test_acknowledge_notifies_listeners` | PASS |

### TestRepeatLogic — Herhalingslogica

| Test | Resultaat |
|---|---|
| `test_repeat_resets_acknowledged` | PASS |
| `test_no_repeat_when_not_due` | PASS |
| `test_repeat_stops_after_repeat_until` | PASS |

### TestListeners — Listener-beheer

| Test | Resultaat |
|---|---|
| `test_add_and_notify_listener` | PASS |
| `test_remove_listener` | PASS |
| `test_failing_listener_does_not_crash` | PASS |

### TestStop — Opruimen

| Test | Resultaat |
|---|---|
| `test_stop_cancels_repeat_task` | PASS |
| `test_stop_cleans_up_condition_listeners` | PASS |

---

## Opgeloste failures

In een eerder testrun faalden 7 tests door problemen in de mock-omgeving. Deze zijn opgelost via aanpassingen in `tests/conftest.py`:

### 1. Listener-notificatie (4 tests opgelost)

**Was:** `@callback` van `homeassistant.core` was een `MagicMock`, waardoor methoden gedecoreerd met `@callback` (zoals `_notify_listeners`) vervangen werden door een MagicMock en nooit de echte logica uitvoerden.

**Fix:** `sys.modules["homeassistant.core"].callback = lambda f: f`

### 2. Tijdsvergelijking in herhalingslogica (3 tests opgelost)

**Was:** `dt_util.utcnow().timestamp()` retourneerde een `MagicMock`, waardoor `now >= alert["next_repeat"]` crashte met een `TypeError`.

**Fix:** `dt_util.utcnow` gekoppeld aan een echte datetime-functie, én de `.dt`-attribute van de `homeassistant.util` mock correct gekoppeld aan het juiste mock-object zodat de `from homeassistant.util import dt as dt_util` binding correct werkt.

---

## Impact huidige code-wijzigingen

De wijzigingen (type-specifieke sensors) raken uitsluitend:
- `custom_components/ha_alert/const.py` — 4 nieuwe constanten
- `custom_components/ha_alert/sensor.py` — nieuwe klasse `HAAlertTypeSensor`

Geen van de 22 bestaande tests test deze nieuwe code.

---

## Aanbevelingen

1. **Schrijf tests voor `HAAlertTypeSensor`**, bijv.:
   - Telt het juiste aantal alerts per type
   - Telt 0 als er geen alerts van dat type zijn
   - Updatet correct als een alert wordt aangemaakt of verwijderd

2. **Gebruik een CI-pipeline** (GitHub Actions op Ubuntu) voor een testomgeving met een echte HA-installatie, zonder mock-beperkingen.
