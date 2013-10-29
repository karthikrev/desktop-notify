import os


class Plugin(object):
    pass


class PluginManager:
    def __init__(self, notifier):
        self.plugins = []
        self.plugin_path = ( "./" if os.path.dirname(__file__) == "" else os.path.dirname(__file__) ) + "/../plugins"
        self._import_plugins()
        self._initialize_plugins()
        self.notifier = notifier    # TODO: This is wrong... should be kwargs

    def _import_plugins(self):
        self.modules = [ module.split('.')[0] for module in os.listdir(self.plugin_path) if module.endswith(".py") ]
        for module in self.modules:
            m = __import__(module)

    def _initialize_plugins(self):
        for plugin in Plugin.__subclasses__():
            obj = plugin()
            self.plugins.append(obj)

    def call_plugin(self):
        for plugin in self.plugins:
            getattr(plugin,'notify')(self.notifier)   #TODO none of them should be hard coded
