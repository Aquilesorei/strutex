"""
Plugin registry and decorator for pyapu extensibility.
"""

from typing import Dict, Type, Optional, Any, Callable
from abc import ABC


class PluginRegistry:
    """
    Central registry for all plugin types.
    
    Usage:
        # Register manually
        PluginRegistry.register("provider", "my_provider", MyProviderClass)
        
        # Retrieve
        cls = PluginRegistry.get("provider", "my_provider")
        
        # List all
        all_providers = PluginRegistry.list("provider")
    """
    
    _plugins: Dict[str, Dict[str, Type]] = {}
    
    @classmethod
    def register(cls, plugin_type: str, name: str, plugin_cls: Type) -> None:
        """
        Register a plugin class.
        
        Args:
            plugin_type: Type of plugin (e.g., "provider", "security", "validator")
            name: Unique name for this plugin
            plugin_cls: The plugin class to register
        """
        if plugin_type not in cls._plugins:
            cls._plugins[plugin_type] = {}
        
        cls._plugins[plugin_type][name.lower()] = plugin_cls
    
    @classmethod
    def get(cls, plugin_type: str, name: str) -> Optional[Type]:
        """
        Get a registered plugin class by type and name.
        
        Args:
            plugin_type: Type of plugin
            name: Name of the plugin
            
        Returns:
            The plugin class, or None if not found
        """
        plugins = cls._plugins.get(plugin_type, {})
        return plugins.get(name.lower())
    
    @classmethod
    def list(cls, plugin_type: str) -> Dict[str, Type]:
        """
        List all plugins of a given type.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            Dictionary mapping names to plugin classes
        """
        return cls._plugins.get(plugin_type, {}).copy()
    
    @classmethod
    def list_types(cls) -> list:
        """List all registered plugin types."""
        return list(cls._plugins.keys())
    
    @classmethod
    def clear(cls, plugin_type: Optional[str] = None) -> None:
        """
        Clear registered plugins.
        
        Args:
            plugin_type: If provided, only clear this type. Otherwise clear all.
        """
        if plugin_type:
            cls._plugins.pop(plugin_type, None)
        else:
            cls._plugins.clear()
    
    @classmethod
    def discover(cls, group_prefix: str = "pyapu") -> int:
        """
        Auto-discover and register plugins from entry points.
        
        Scans for entry points matching the pattern:
        - pyapu.providers
        - pyapu.validators
        - pyapu.postprocessors
        - pyapu.security
        - etc.
        
        Args:
            group_prefix: Entry point group prefix (default: "pyapu")
            
        Returns:
            Number of plugins discovered and registered
        
        Example pyproject.toml:
            [project.entry-points."pyapu.providers"]
            my_provider = "my_package:MyProvider"
        """
        import sys
        
        discovered = 0
        
        # Python 3.10+ has importlib.metadata in stdlib
        if sys.version_info >= (3, 10):
            from importlib.metadata import entry_points
        else:
            try:
                from importlib_metadata import entry_points
            except ImportError:
                # Fallback for older Python without backport
                return 0
        
        # Get all entry point groups
        try:
            # Python 3.10+ style
            all_eps = entry_points()
            if hasattr(all_eps, 'groups'):
                groups = [g for g in all_eps.groups if g.startswith(f"{group_prefix}.")]
            else:
                # Python 3.9 style (dict-like)
                groups = [g for g in all_eps.keys() if g.startswith(f"{group_prefix}.")]
        except Exception:
            return 0
        
        for group in groups:
            # Extract plugin type from group name (e.g., "pyapu.providers" -> "provider")
            plugin_type = group.replace(f"{group_prefix}.", "").rstrip("s")
            
            try:
                if hasattr(all_eps, 'select'):
                    eps = all_eps.select(group=group)
                else:
                    eps = all_eps.get(group, [])
                
                for ep in eps:
                    try:
                        plugin_cls = ep.load()
                        cls.register(plugin_type, ep.name, plugin_cls)
                        discovered += 1
                    except Exception:
                        # Skip plugins that fail to load
                        pass
            except Exception:
                pass
        
        return discovered


def register(plugin_type: str, name: Optional[str] = None) -> Callable[[Type], Type]:
    """
    Decorator to register a plugin class.
    
    Args:
        plugin_type: Type of plugin (e.g., "provider", "security")
        name: Optional name. If not provided, uses lowercase class name.
        
    Usage:
        @register("provider")
        class MyProvider(Provider):
            ...
        
        @register("provider", name="custom_name")
        class AnotherProvider(Provider):
            ...
    """
    def decorator(cls: Type) -> Type:
        plugin_name = name if name else cls.__name__.lower()
        PluginRegistry.register(plugin_type, plugin_name, cls)
        return cls
    
    return decorator
