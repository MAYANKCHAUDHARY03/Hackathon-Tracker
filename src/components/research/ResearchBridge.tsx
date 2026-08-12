import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { researchApi } from '@/api/researchApi';
import type { ResearchLink, ResearchLinkCreate } from '@/api/researchApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Loader2, ExternalLink, Link as LinkIcon, Trash2, FileText, Database, GitMerge, Building2 } from 'lucide-react';
import { toast } from 'sonner';

interface ResearchBridgeProps {
  projectId: string;
}

export function ResearchBridge({ projectId }: ResearchBridgeProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [links, setLinks] = useState<ResearchLink[]>([]);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState(false);

  const [newTitle, setNewTitle] = useState('');
  const [newType, setNewType] = useState('paper');
  const [newUrl, setNewUrl] = useState('');
  const [newIdentifier, setNewIdentifier] = useState('');

  useEffect(() => {
    if (activeWorkspaceId && projectId) {
      loadLinks();
    }
  }, [activeWorkspaceId, projectId]);

  const loadLinks = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    try {
      const data = await researchApi.getLinks(activeWorkspaceId, projectId);
      setLinks(data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load research links');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLink = async () => {
    if (!activeWorkspaceId) return;
    if (!newTitle.trim()) {
      toast.error('Title is required');
      return;
    }

    setAdding(true);
    try {
      const data: ResearchLinkCreate = {
        project_id: projectId,
        title: newTitle,
        type: newType,
        url: newUrl || undefined,
        identifier: newIdentifier || undefined
      };
      const created = await researchApi.createLink(activeWorkspaceId, data);
      setLinks([...links, created]);
      setNewTitle('');
      setNewUrl('');
      setNewIdentifier('');
      toast.success('Research link added successfully');
    } catch (err) {
      console.error(err);
      toast.error('Failed to add research link');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (linkId: string) => {
    if (!activeWorkspaceId) return;
    try {
      await researchApi.deleteLink(activeWorkspaceId, linkId);
      setLinks(links.filter(l => l.id !== linkId));
      toast.success('Link removed');
    } catch (err) {
      console.error(err);
      toast.error('Failed to remove link');
    }
  };

  const getIconForType = (type: string) => {
    switch(type) {
      case 'paper': return <FileText className="w-4 h-4 mr-2" />;
      case 'dataset': return <Database className="w-4 h-4 mr-2" />;
      case 'repo': return <GitMerge className="w-4 h-4 mr-2" />;
      case 'institution': return <Building2 className="w-4 h-4 mr-2" />;
      default: return <LinkIcon className="w-4 h-4 mr-2" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 bg-muted/50 p-4 rounded-lg">
          <div className="space-y-2">
            <Label>Type</Label>
            <select 
              value={newType} 
              onChange={e => setNewType(e.target.value)}
              className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option value="paper">Research Paper</option>
              <option value="dataset">Dataset</option>
              <option value="repo">Repository</option>
              <option value="patent">Patent</option>
              <option value="institution">Institution</option>
            </select>
          </div>
          <div className="space-y-2 lg:col-span-2">
            <Label>Title *</Label>
            <Input placeholder="E.g. Attention Is All You Need" value={newTitle} onChange={e => setNewTitle(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Identifier</Label>
            <Input placeholder="DOI, URL, etc." value={newUrl || newIdentifier} onChange={e => {
              const val = e.target.value;
              if (val.startsWith('http')) setNewUrl(val);
              else setNewIdentifier(val);
            }} />
          </div>
          <div className="md:col-span-2 lg:col-span-4 flex justify-end">
            <Button onClick={handleAddLink} disabled={adding}>
              {adding && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add Reference
            </Button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center p-6"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
      ) : links.length === 0 ? (
        <div className="text-center p-6 border rounded-lg border-dashed text-muted-foreground">
          No research links found for this project.
        </div>
      ) : (
        <div className="space-y-3">
          {links.map(link => (
            <div key={link.id} className="flex items-center justify-between p-4 border rounded-lg bg-card">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-primary/10 text-primary rounded-full">
                  {getIconForType(link.type)}
                </div>
                <div>
                  <h4 className="font-medium flex items-center">
                    {link.title}
                    {link.url && (
                      <a href={link.url} target="_blank" rel="noopener noreferrer" className="ml-2 text-muted-foreground hover:text-primary">
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </h4>
                  <div className="flex items-center space-x-2 mt-1 text-xs text-muted-foreground">
                    <span className="capitalize">{link.type}</span>
                    {link.identifier && (
                      <>
                        <span>•</span>
                        <span>{link.identifier}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Badge variant={link.provenance === 'AI-inferred' ? 'secondary' : 'outline'}>
                  {link.provenance === 'AI-inferred' ? 'AI Identified' : 'User Provided'}
                </Badge>
                <Button variant="ghost" size="icon" onClick={() => handleDelete(link.id)}>
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
