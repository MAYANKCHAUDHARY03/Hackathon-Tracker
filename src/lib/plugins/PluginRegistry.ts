export interface Plugin {
  id: string;
  name: string;
  version: string;
  requiredCoreVersion: string;
  initialize: (context: PluginContext) => void;
}

export interface PluginContext {
  registerRoute: (path: string, component: React.FC) => void;
  registerWidget: (dashboardId: string, widget: React.FC) => void;
  onEvent: (event: string, handler: (payload: any) => void) => void;
}

class PluginRegistryClass {
  private plugins: Map<string, Plugin> = new Map();
  private routes: Map<string, React.FC> = new Map();
  private widgets: Map<string, React.FC[]> = new Map();
  private listeners: Map<string, ((payload: any) => void)[]> = new Map();

  registerPlugin(plugin: Plugin) {
    if (this.plugins.has(plugin.id)) {
      console.warn(`Plugin ${plugin.id} is already registered.`);
      return;
    }
    
    // Evaluate compatibility here in the future
    this.plugins.set(plugin.id, plugin);
    
    const context: PluginContext = {
      registerRoute: (path, component) => this.routes.set(path, component),
      registerWidget: (dashboardId, widget) => {
        if (!this.widgets.has(dashboardId)) this.widgets.set(dashboardId, []);
        this.widgets.get(dashboardId)?.push(widget);
      },
      onEvent: (event, handler) => {
        if (!this.listeners.has(event)) this.listeners.set(event, []);
        this.listeners.get(event)?.push(handler);
      }
    };

    try {
      plugin.initialize(context);
      console.log(`Plugin ${plugin.name} initialized successfully.`);
    } catch (e) {
      console.error(`Failed to initialize plugin ${plugin.name}:`, e);
    }
  }

  getRoutes() {
    return this.routes;
  }

  getWidgets(dashboardId: string) {
    return this.widgets.get(dashboardId) || [];
  }

  emitEvent(event: string, payload: any) {
    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.forEach(h => h(payload));
    }
  }
}

export const PluginRegistry = new PluginRegistryClass();
