# arin-log

A lightweight, cross-platform logging package for long-running pipelines.
A virtual assistant for the user. A clean archive for the developer.

---

## What is `arin_log`?

`arin_log` combines two roles in one package:

1. **A virtual assistant (Arin)** who talks to the user on the console
   and keeps them informed about what the script is doing.
2. **A clean, technical log file** that contains only the beacons:
   start, exception, exit. Meant for the developer who has to
   reconstruct later what happened.

The user sees a story. The developer sees a trail. That is the core.

**Arin is not an AI.** She is a voice — a smart logger with a
character. This is a deliberate choice not to abuse the AI hype.

---

## Installation

```bash
pip install arin-log
```

On first import, a folder dialog appears asking where you want to
store your log files. The choice, together with the default colors,
is saved in:

- **Windows:** `%APPDATA%\arin_log\config_log.json`
- **Linux/macOS:** `~/.arin_log/config_log.json`

The dialog appears only once. On every next run, `arin_log` reads
this file and skips the dialog.

If you want to change the log folder later:

```python
from arin_log import change_folder
change_folder()
```

---

## Quick example

```python
from arin_log import log_start, log_notes, log_except, log_exit
from sys import _getframe

log_start("my_pipeline", logloc="pipeline")

try:
    log_notes("startup ; loading data", logloc="pipeline")
    # ... your work ...
    log_notes("success ; data loaded", logloc="pipeline")
except Exception:
    log_except(_getframe(), "data ; loading ; fail", logloc="pipeline")
    log_exit("my_pipeline", imp=False, logloc="pipeline")

log_exit("my_pipeline", imp=True, logloc="pipeline")
```

**What the user sees on the console:**

```
Arin : startup ; loading data
Arin : success ; data loaded
Arin my_pipeline ; 14:32:11 ; completed
```

**What ends up in the log file:**

```
26-10-04.pipeline.log

my_pipeline ; 14:32:11 ; running

startup ; loading data
success ; data loaded

my_pipeline ; 14:32:11 ; completed
------------------------------------------------------------
```

---

## What makes `arin_log` different?

| Aspect | `arin_log` | Loguru / stdlib / structlog |
|---|---|---|
| **Context propagation** | One parameter `logloc` travels through the whole call chain; every submodule becomes part of the same log file | `LoggerAdapter`, `contextvars`, or manual config |
| **Console vs. log file** | Deliberately separated: console = everything (with Arin as a voice), log file = only the beacons | Everything goes to the same handlers |
| **Archive** | One log file per main module per day, with automatic section separation per subtask | Scattered files or one big file |
| **Arin as virtual assistant** | A character who guides the user, not a log-level prefix | No equivalent |
| **Exception notation** | `module.function.linenumber ; time ; exception` — compact and directly usable | Full traceback or `exc_info=True` |

**Core USP:** `logloc` + daily grouping per main module + separation of
console and archive + Arin.

---

## How it works

The package consists of four modules, each with a clear task:

- **`logger.py`** — the heart: `log_start`, `log_notes`, `log_except`,
  `log_exit`, and the helpers.
- **`folder.py`** — manages the config folder and the log folder.
- **`console.py`** — console interaction: clear screen, menus.
- **`utils.py`** — JSON helpers (`load_json`, `save_json`).

### Configuration

- **`log_cnfg.json`** ships with the package as a template: the default
  color words and color codes for the console.
- **`config_log.json`** lives in `%APPDATA%\arin_log\` (Windows) or
  `~/.arin_log/` (Linux/macOS). On first run it is created by copying
  the colors from `log_cnfg.json` and adding your chosen log folder.

To customize colors, edit `config_log.json` in the config folder
above. Your changes survive `pip install --upgrade arin-log`, because
the file is never touched by pip.

---

## The log folder

`arin_log` stores its files in a folder of your choice. On first use,
a folder dialog appears. The choice is saved in `config_log.json`
(see Configuration), so it survives across sessions and is never
overwritten by a `pip install --upgrade`.

If `config_log.json` is missing or corrupt, the dialog appears again —
the package has no fallback folder. The user is expected to choose.

---

## Requirements

- Python 3.9 or higher

No external dependencies.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Status

**Alpha (0.2.0).** The core works. Tests are still in development.
