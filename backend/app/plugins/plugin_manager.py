import importlib
import pkgutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}

    def discover_plugins(self, package_name: str):
        """
        Dynamically discover and load plugins from a given python package path.
        Expected that each plugin module has a `register(event_bus)` function.
        """
        try:
            package = importlib.import_module(package_name)
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"
                module = importlib.import_module(full_module_name)
                
                if hasattr(module, "register"):
                    self.plugins[module_name] = module
                    logger.info(f"Discovered plugin: {module_name}")
        except ModuleNotFoundError:
            logger.warning(f"Plugin package {package_name} not found.")

    def initialize_plugins(self, event_bus):
        """
        Initialize all discovered plugins by passing the event bus.
        """
        for name, module in self.plugins.items():
            try:
                module.register(event_bus)
                logger.info(f"Initialized plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")

plugin_manager = PluginManager()
