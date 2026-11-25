import logging
import tomllib
from pathlib import Path

def setup_logging():
    pyproject_path = Path(__file__).resolve().parent.parent.parent.parent / "pyproject.toml"
    app_log_level = "DEBUG"
    
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                app_log_level = data.get("tool", {}).get("bridge_to_bridge_api", {}).get("log_level", "DEBUG")
        except Exception:
            pass

    app_log_level = app_log_level.upper()

    # Basic config for root logger (underlying modules)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Application-specific logger
    app_logger = logging.getLogger("bridge_to_bridge_api")
    app_logger.setLevel(app_log_level)
