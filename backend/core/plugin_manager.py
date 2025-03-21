import importlib
import os
import pkgutil
import inspect
from typing import Dict, Type, List, Any, TypeVar, Generic

T = TypeVar('T')

class PluginManager(Generic[T]):
    """
    A generic plugin manager that handles discovery and registration of plugins.
    """
    
    def __init__(self, plugin_base_class: Type[T], plugin_dir: str):
        """
        Initialize the plugin manager with a base class and directory.
        
        Args:
            plugin_base_class: The base class that all plugins must inherit from
            plugin_dir: The directory containing the plugin modules
        """
        self.plugin_base_class = plugin_base_class
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Type[T]] = {}
        self.discover_plugins()
    
    def discover_plugins(self) -> None:
        """
        Discover and register all plugins in the plugin directory.
        """
        # Ensure plugin directory exists
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            return
            
        # Get the package name for importing
        package_path = self.plugin_dir.replace(os.sep, '.')
        
        # Import all modules in the plugin directory
        for _, name, is_pkg in pkgutil.iter_modules([self.plugin_dir]):
            if not is_pkg:
                module = importlib.import_module(f"{package_path}.{name}")
                
                # Find and register all plugin classes in the module
                for attr_name, attr_value in module.__dict__.items():
                    if (inspect.isclass(attr_value) and 
                        issubclass(attr_value, self.plugin_base_class) and 
                        attr_value != self.plugin_base_class):
                        
                        plugin_id = getattr(attr_value, "plugin_id", attr_value.__name__)
                        self.register_plugin(plugin_id, attr_value)
    
    def register_plugin(self, plugin_id: str, plugin_class: Type[T]) -> None:
        """
        Register a plugin with the manager.
        
        Args:
            plugin_id: A unique identifier for the plugin
            plugin_class: The plugin class
        """
        if plugin_id in self.plugins:
            print(f"Warning: Plugin {plugin_id} is already registered. Overwriting.")
        
        self.plugins[plugin_id] = plugin_class
    
    def get_plugin(self, plugin_id: str) -> Type[T]:
        """
        Get a plugin by its ID.
        
        Args:
            plugin_id: The ID of the plugin to retrieve
            
        Returns:
            The plugin class
            
        Raises:
            KeyError: If the plugin ID is not registered
        """
        if plugin_id not in self.plugins:
            raise KeyError(f"Plugin {plugin_id} is not registered")
        
        return self.plugins[plugin_id]
    
    def get_all_plugins(self) -> Dict[str, Type[T]]:
        """
        Get all registered plugins.
        
        Returns:
            A dictionary mapping plugin IDs to plugin classes
        """
        return self.plugins
    
    def instantiate_plugin(self, plugin_id: str, *args: Any, **kwargs: Any) -> T:
        """
        Create an instance of a plugin.
        
        Args:
            plugin_id: The ID of the plugin to instantiate
            *args: Positional arguments to pass to the plugin constructor
            **kwargs: Keyword arguments to pass to the plugin constructor
            
        Returns:
            An instance of the plugin
        """
        plugin_class = self.get_plugin(plugin_id)
        return plugin_class(*args, **kwargs) 