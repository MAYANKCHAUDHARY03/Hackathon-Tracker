import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiKeyApi, type APIKey, type APIKeyCreate } from '@/api/apiKeyApi';
import { webhookApi, type WebhookSubscription, type WebhookSubscriptionCreate, type WebhookDelivery } from '@/api/webhookApi';
import { developerApi, type DeveloperApp, type DeveloperAppCreate } from '@/api/developerApi';
import { 
  Key, Webhook, Plus, Trash2, Copy, CheckCircle2, 
  AlertCircle, Activity, Settings2, Clock, Globe, AppWindow, Database
} from 'lucide-react';
import { format } from 'date-fns';

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

export default function Vault() {
  const { activeWorkspaceId: workspaceId } = useWorkspaceStore();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState('api-keys');

  // API Keys state
  const [isCreateKeyOpen, setIsCreateKeyOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState(false);

  // Webhooks state
  const [isCreateWebhookOpen, setIsCreateWebhookOpen] = useState(false);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [newWebhookSecret, setNewWebhookSecret] = useState('');
  const [newWebhookEvents, setNewWebhookEvents] = useState<string>('hackathon.created,submission.created');
  
  const [selectedSubscriptionId, setSelectedSubscriptionId] = useState<string | null>(null);

  // Developer Apps state
  const [isCreateAppOpen, setIsCreateAppOpen] = useState(false);
  const [newAppName, setNewAppName] = useState('');
  const [newAppRedirectUris, setNewAppRedirectUris] = useState('');
  const [generatedAppCreds, setGeneratedAppCreds] = useState<{client_id: string, client_secret: string} | null>(null);
  const [copiedAppId, setCopiedAppId] = useState(false);
  const [copiedAppSecret, setCopiedAppSecret] = useState(false);

  // Queries
  const { data: apiKeys = [], isLoading: isLoadingKeys } = useQuery({
    queryKey: ['api-keys', workspaceId],
    queryFn: () => apiKeyApi.listAPIKeys(workspaceId!),
    enabled: !!workspaceId,
  });

  const { data: webhooks = [], isLoading: isLoadingWebhooks } = useQuery({
    queryKey: ['webhooks', workspaceId],
    queryFn: () => webhookApi.listSubscriptions(workspaceId!),
    enabled: !!workspaceId,
  });

  const { data: webhookDeliveries = [], isLoading: isLoadingDeliveries } = useQuery({
    queryKey: ['webhook-deliveries', workspaceId, selectedSubscriptionId],
    queryFn: () => webhookApi.listDeliveries(workspaceId!, selectedSubscriptionId!),
    enabled: !!workspaceId && !!selectedSubscriptionId,
  });

  const { data: developerApps = [], isLoading: isLoadingApps } = useQuery({
    queryKey: ['developer-apps', workspaceId],
    queryFn: () => developerApi.getApps(workspaceId!),
    enabled: !!workspaceId,
  });

  // Mutations - API Keys
  const createKeyMutation = useMutation({
    mutationFn: (data: APIKeyCreate) => apiKeyApi.createAPIKey(workspaceId!, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', workspaceId] });
      setGeneratedKey(data.key);
      setNewKeyName('');
    }
  });

  const revokeKeyMutation = useMutation({
    mutationFn: (keyId: string) => apiKeyApi.revokeAPIKey(workspaceId!, keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', workspaceId] });
    }
  });

  // Mutations - Webhooks
  const createWebhookMutation = useMutation({
    mutationFn: (data: WebhookSubscriptionCreate) => webhookApi.createSubscription(workspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks', workspaceId] });
      setIsCreateWebhookOpen(false);
      setNewWebhookUrl('');
      setNewWebhookSecret('');
    }
  });

  const createAppMutation = useMutation({
    mutationFn: (data: DeveloperAppCreate) => developerApi.createApp(workspaceId!, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['developer-apps', workspaceId] });
      setGeneratedAppCreds({ client_id: data.client_id, client_secret: data.client_secret });
      setNewAppName('');
      setNewAppRedirectUris('');
    }
  });

  const handleCopyKey = () => {
    if (generatedKey) {
      navigator.clipboard.writeText(generatedKey);
      setCopiedKey(true);
      setTimeout(() => setCopiedKey(false), 2000);
    }
  };

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault();
    createKeyMutation.mutate({ name: newKeyName, scopes: ['*'] });
  };

  const handleCreateWebhook = (e: React.FormEvent) => {
    e.preventDefault();
    createWebhookMutation.mutate({
      url: newWebhookUrl,
      secret: newWebhookSecret || undefined,
      events: newWebhookEvents.split(',').map(s => s.trim()).filter(Boolean)
    });
  };

  const handleCreateApp = (e: React.FormEvent) => {
    e.preventDefault();
    createAppMutation.mutate({
      name: newAppName,
      redirect_uris: newAppRedirectUris.split(',').map(s => s.trim()).filter(Boolean)
    });
  };

  const closeKeyModal = () => {
    setIsCreateKeyOpen(false);
    setGeneratedKey(null);
  };

  const closeAppModal = () => {
    setIsCreateAppOpen(false);
    setGeneratedAppCreds(null);
  };

  if (!workspaceId) return <div className="p-8">Select a workspace first.</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">API Vault</h1>
        <p className="text-muted-foreground">
          Manage programmatic access and real-time events for your workspace.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 max-w-[800px]">
          <TabsTrigger value="api-keys" className="flex items-center gap-2">
            <Key className="w-4 h-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="webhooks" className="flex items-center gap-2">
            <Webhook className="w-4 h-4" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="developer-apps" className="flex items-center gap-2">
            <AppWindow className="w-4 h-4" />
            OAuth Apps
          </TabsTrigger>
          <TabsTrigger value="data-exchange" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Data Exchange
          </TabsTrigger>
        </TabsList>

        <TabsContent value="api-keys" className="space-y-6 mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>
                  Generate keys to authenticate your external services with the API.
                </CardDescription>
              </div>
              <Dialog open={isCreateKeyOpen} onOpenChange={setIsCreateKeyOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Create API Key
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  {!generatedKey ? (
                    <form onSubmit={handleCreateKey}>
                      <DialogHeader>
                        <DialogTitle>Create new API Key</DialogTitle>
                        <DialogDescription>
                          Provide a descriptive name for this key to identify its usage.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                          <Label htmlFor="key-name">Key Name</Label>
                          <Input
                            id="key-name"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            placeholder="e.g. Production CI/CD Server"
                            required
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsCreateKeyOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit" disabled={createKeyMutation.isPending || !newKeyName}>
                          {createKeyMutation.isPending ? 'Generating...' : 'Generate Key'}
                        </Button>
                      </DialogFooter>
                    </form>
                  ) : (
                    <div>
                      <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-green-600">
                          <CheckCircle2 className="w-5 h-5" /> Key Generated Successfully
                        </DialogTitle>
                        <DialogDescription className="text-amber-600 dark:text-amber-500 font-medium pt-2">
                          Please copy this key now. You will not be able to see it again!
                        </DialogDescription>
                      </DialogHeader>
                      <div className="py-6">
                        <div className="flex items-center space-x-2">
                          <Input value={generatedKey} readOnly className="font-mono bg-muted" />
                          <Button size="icon" variant="outline" onClick={handleCopyKey}>
                            {copiedKey ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="button" onClick={closeKeyModal}>
                          I have copied the key
                        </Button>
                      </DialogFooter>
                    </div>
                  )}
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {isLoadingKeys ? (
                <div className="text-center py-8 text-muted-foreground">Loading API Keys...</div>
              ) : apiKeys.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed rounded-lg bg-muted/20">
                  <Key className="w-8 h-8 mx-auto text-muted-foreground mb-3" />
                  <h3 className="text-lg font-medium">No API Keys</h3>
                  <p className="text-sm text-muted-foreground mt-1">Create your first API key to get started.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {apiKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg bg-card hover:bg-accent/5 transition-colors">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{key.name}</span>
                          <Badge variant={key.is_active ? "default" : "secondary"}>
                            {key.is_active ? 'Active' : 'Revoked'}
                          </Badge>
                        </div>
                        <div className="text-sm font-mono text-muted-foreground bg-muted px-2 py-1 rounded inline-block">
                          {key.prefix}••••••••••••
                        </div>
                        <div className="text-xs text-muted-foreground flex items-center gap-4 mt-2">
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3"/> Created {format(new Date(key.created_at), 'MMM d, yyyy')}</span>
                          {key.last_used_at && (
                            <span className="flex items-center gap-1"><Activity className="w-3 h-3"/> Last used {format(new Date(key.last_used_at), 'MMM d, yyyy')}</span>
                          )}
                        </div>
                      </div>
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => {
                          if (confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
                            revokeKeyMutation.mutate(key.id);
                          }
                        }}
                      >
                        Revoke
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="webhooks" className="space-y-6 mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Webhook Subscriptions</CardTitle>
                <CardDescription>
                  Subscribe to platform events to trigger actions in your own systems.
                </CardDescription>
              </div>
              <Dialog open={isCreateWebhookOpen} onOpenChange={setIsCreateWebhookOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Add Webhook
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <form onSubmit={handleCreateWebhook}>
                    <DialogHeader>
                      <DialogTitle>Add Webhook Subscription</DialogTitle>
                      <DialogDescription>
                        Configure where we should send event payloads.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid gap-2">
                        <Label htmlFor="webhook-url">Payload URL</Label>
                        <Input
                          id="webhook-url"
                          type="url"
                          value={newWebhookUrl}
                          onChange={(e) => setNewWebhookUrl(e.target.value)}
                          placeholder="https://api.yourdomain.com/webhooks"
                          required
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="webhook-secret">Secret (Optional)</Label>
                        <Input
                          id="webhook-secret"
                          type="password"
                          value={newWebhookSecret}
                          onChange={(e) => setNewWebhookSecret(e.target.value)}
                          placeholder="Used to sign webhook payloads"
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="webhook-events">Events (comma-separated)</Label>
                        <Input
                          id="webhook-events"
                          value={newWebhookEvents}
                          onChange={(e) => setNewWebhookEvents(e.target.value)}
                          placeholder="hackathon.created, submission.created"
                          required
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsCreateWebhookOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={createWebhookMutation.isPending || !newWebhookUrl}>
                        {createWebhookMutation.isPending ? 'Saving...' : 'Save Webhook'}
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {isLoadingWebhooks ? (
                <div className="text-center py-8 text-muted-foreground">Loading Webhooks...</div>
              ) : webhooks.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed rounded-lg bg-muted/20">
                  <Webhook className="w-8 h-8 mx-auto text-muted-foreground mb-3" />
                  <h3 className="text-lg font-medium">No Webhooks</h3>
                  <p className="text-sm text-muted-foreground mt-1">Configure your first webhook to receive real-time updates.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {webhooks.map((webhook) => (
                    <div key={webhook.id} className="p-4 border rounded-lg bg-card">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Globe className="w-4 h-4 text-blue-500" />
                          <span className="font-semibold text-sm">{webhook.url}</span>
                          <Badge variant={webhook.is_active ? "default" : "secondary"}>
                            {webhook.is_active ? 'Active' : 'Disabled'}
                          </Badge>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => setSelectedSubscriptionId(selectedSubscriptionId === webhook.id ? null : webhook.id)}>
                          {selectedSubscriptionId === webhook.id ? 'Hide Deliveries' : 'View Deliveries'}
                        </Button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {webhook.events.map(event => (
                          <Badge key={event} variant="outline" className="text-xs bg-muted/50">{event}</Badge>
                        ))}
                      </div>

                      {/* Deliveries Section */}
                      {selectedSubscriptionId === webhook.id && (
                        <div className="mt-4 pt-4 border-t">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <Activity className="w-4 h-4"/> Recent Deliveries
                          </h4>
                          {isLoadingDeliveries ? (
                            <div className="text-xs text-muted-foreground">Loading deliveries...</div>
                          ) : webhookDeliveries.length === 0 ? (
                            <div className="text-xs text-muted-foreground">No recent deliveries found.</div>
                          ) : (
                            <div className="space-y-2">
                              {webhookDeliveries.map(delivery => (
                                <div key={delivery.id} className="flex items-center justify-between p-2 text-xs border rounded bg-muted/30">
                                  <div className="flex items-center gap-3">
                                    <span className={`font-mono px-1.5 py-0.5 rounded ${
                                      delivery.status_code && delivery.status_code >= 200 && delivery.status_code < 300 
                                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                                      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                    }`}>
                                      {delivery.status_code || 'Err'}
                                    </span>
                                    <span className="font-medium">{delivery.event_type}</span>
                                  </div>
                                  <span className="text-muted-foreground">{format(new Date(delivery.created_at), 'MMM d, HH:mm:ss')}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="developer-apps" className="space-y-6 mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>OAuth Developer Apps</CardTitle>
                <CardDescription>
                  Register applications to access this workspace via OAuth 2.0.
                </CardDescription>
              </div>
              <Dialog open={isCreateAppOpen} onOpenChange={setIsCreateAppOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="w-4 h-4" /> Create App
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  {!generatedAppCreds ? (
                    <form onSubmit={handleCreateApp}>
                      <DialogHeader>
                        <DialogTitle>Register new OAuth App</DialogTitle>
                        <DialogDescription>
                          Create a new application to obtain a Client ID and Client Secret.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                          <Label htmlFor="app-name">App Name</Label>
                          <Input
                            id="app-name"
                            value={newAppName}
                            onChange={(e) => setNewAppName(e.target.value)}
                            placeholder="e.g. Acme Analytics Integration"
                            required
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="app-uris">Redirect URIs</Label>
                          <Input
                            id="app-uris"
                            value={newAppRedirectUris}
                            onChange={(e) => setNewAppRedirectUris(e.target.value)}
                            placeholder="https://app.acme.com/oauth/callback (comma separated)"
                            required
                          />
                          <p className="text-xs text-muted-foreground">Multiple URIs can be separated by commas.</p>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsCreateAppOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit" disabled={createAppMutation.isPending || !newAppName || !newAppRedirectUris}>
                          {createAppMutation.isPending ? 'Registering...' : 'Register App'}
                        </Button>
                      </DialogFooter>
                    </form>
                  ) : (
                    <div>
                      <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-green-600">
                          <CheckCircle2 className="w-5 h-5" /> App Registered Successfully
                        </DialogTitle>
                        <DialogDescription className="text-amber-600 dark:text-amber-500 font-medium pt-2">
                          Please copy this Client Secret now. You will not be able to see it again!
                        </DialogDescription>
                      </DialogHeader>
                      <div className="py-6 space-y-4">
                        <div className="space-y-1">
                          <Label>Client ID</Label>
                          <div className="flex items-center space-x-2">
                            <Input value={generatedAppCreds.client_id} readOnly className="font-mono bg-muted" />
                            <Button size="icon" variant="outline" onClick={() => {
                              navigator.clipboard.writeText(generatedAppCreds.client_id);
                              setCopiedAppId(true);
                              setTimeout(() => setCopiedAppId(false), 2000);
                            }}>
                              {copiedAppId ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                            </Button>
                          </div>
                        </div>
                        <div className="space-y-1">
                          <Label>Client Secret</Label>
                          <div className="flex items-center space-x-2">
                            <Input value={generatedAppCreds.client_secret} readOnly className="font-mono bg-muted" />
                            <Button size="icon" variant="outline" onClick={() => {
                              navigator.clipboard.writeText(generatedAppCreds.client_secret);
                              setCopiedAppSecret(true);
                              setTimeout(() => setCopiedAppSecret(false), 2000);
                            }}>
                              {copiedAppSecret ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                            </Button>
                          </div>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="button" onClick={closeAppModal}>
                          I have copied the credentials
                        </Button>
                      </DialogFooter>
                    </div>
                  )}
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {isLoadingApps ? (
                <div className="text-center py-8 text-muted-foreground">Loading Developer Apps...</div>
              ) : developerApps.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed rounded-lg bg-muted/20">
                  <AppWindow className="w-8 h-8 mx-auto text-muted-foreground mb-3" />
                  <h3 className="text-lg font-medium">No Developer Apps</h3>
                  <p className="text-sm text-muted-foreground mt-1">Register an app to build OAuth integrations.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {developerApps.map((app) => (
                    <div key={app.id} className="p-4 border rounded-lg bg-card">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{app.name}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-muted-foreground">Client ID: </span>
                          <span className="font-mono">{app.client_id}</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-2">
                          <p>Redirect URIs:</p>
                          <ul className="list-disc list-inside">
                            {app.redirect_uris.map(uri => (
                              <li key={uri}>{uri}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data-exchange" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Exchange API</CardTitle>
              <CardDescription>
                Export and import core Hackathon Tracker entities (Hackathons, Projects, Organizations) using the versioned InnovationSchema (V1) in JSON, NDJSON, and CSV formats.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              <div className="space-y-4">
                <h3 className="text-lg font-medium border-b pb-2">Export Data</h3>
                <p className="text-sm text-muted-foreground">
                  Use your generated API keys to fetch workspace data. The export includes all hackathons, projects, and organizations the API key has scopes for.
                </p>
                <div className="bg-secondary/30 p-4 rounded-md border font-mono text-sm overflow-x-auto whitespace-pre">
                  <span className="text-blue-500 font-bold">curl</span> -X GET \<br/>
                  &nbsp;&nbsp;<span>"https://api.hackathontracker.com/api/v1/exchange/export?format=json&amp;include_hackathons=true"</span> \<br/>
                  &nbsp;&nbsp;-H <span className="text-green-500">"X-API-Key: YOUR_API_KEY_HERE"</span>
                </div>
                <div className="flex gap-2 pt-2">
                  <Badge variant="outline">format: json | csv | ndjson</Badge>
                  <Badge variant="outline">include_hackathons: boolean</Badge>
                  <Badge variant="outline">include_projects: boolean</Badge>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-medium border-b pb-2">Import Data</h3>
                <p className="text-sm text-muted-foreground">
                  Import entities into your workspace using the standardized InnovationSchemaV1 format.
                </p>
                <div className="bg-secondary/30 p-4 rounded-md border font-mono text-sm overflow-x-auto whitespace-pre">
                  <span className="text-blue-500 font-bold">curl</span> -X POST \<br/>
                  &nbsp;&nbsp;<span>"https://api.hackathontracker.com/api/v1/exchange/import"</span> \<br/>
                  &nbsp;&nbsp;-H <span className="text-green-500">"X-API-Key: YOUR_API_KEY_HERE"</span> \<br/>
                  &nbsp;&nbsp;-H <span className="text-green-500">"Content-Type: application/json"</span> \<br/>
                  &nbsp;&nbsp;-d <span className="text-amber-500">'{'{"version":"1.0","hackathons":[]}'}'</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
