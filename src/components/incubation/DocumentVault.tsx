import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { incubationApi, type ProjectDocument } from '@/api/incubationApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { FileText, Plus, ExternalLink, Link } from 'lucide-react';
import { format } from 'date-fns';

interface DocumentVaultProps {
  projectId: string;
  documents: ProjectDocument[];
}

export function DocumentVault({ projectId, documents }: DocumentVaultProps) {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState<ProjectDocument['document_type']>('other');
  const [url, setUrl] = useState('');

  const addDocument = useMutation({
    mutationFn: (data: Partial<ProjectDocument>) => incubationApi.createDocument(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incubation-dashboard', projectId] });
      toast.success('Document added');
      setIsDialogOpen(false);
      setTitle('');
      setUrl('');
    },
    onError: () => toast.error('Failed to add document')
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addDocument.mutate({
      title,
      document_type: docType,
      url
    });
  };

  const getDocIcon = (type: string) => {
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          Document Vault
        </h3>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="ghost" className="h-8 px-2">
              <Plus className="w-4 h-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[400px]">
            <DialogHeader>
              <DialogTitle>Add Document Link</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input value={title} onChange={e => setTitle(e.target.value)} required placeholder="e.g. Q3 Pitch Deck" />
              </div>
              <div className="space-y-2">
                <Label>Document Type</Label>
                <Select value={docType} onValueChange={(val: any) => setDocType(val)} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="business_plan">Business Plan</SelectItem>
                    <SelectItem value="pitch_deck">Pitch Deck</SelectItem>
                    <SelectItem value="legal">Legal Document</SelectItem>
                    <SelectItem value="financial">Financial Report</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>URL</Label>
                <div className="flex gap-2 items-center">
                  <Link className="w-4 h-4 text-muted-foreground" />
                  <Input type="url" value={url} onChange={e => setUrl(e.target.value)} required placeholder="https://..." className="flex-1" />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={addDocument.isPending || !title || !url}>
                  {addDocument.isPending ? 'Saving...' : 'Add Link'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-2">
        {documents.length === 0 ? (
          <p className="text-sm text-muted-foreground pl-1">No documents uploaded.</p>
        ) : (
          documents.map(doc => (
            <div key={doc.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 hover:bg-secondary/20 transition-colors">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="p-2 rounded bg-secondary/50 shrink-0 text-muted-foreground">
                  {getDocIcon(doc.document_type)}
                </div>
                <div className="truncate">
                  <h4 className="text-sm font-medium truncate">{doc.title}</h4>
                  <p className="text-xs text-muted-foreground">
                    {doc.document_type.replace('_', ' ')} • {format(new Date(doc.created_at), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>
              <Button size="sm" variant="ghost" className="shrink-0" asChild>
                <a href={doc.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 text-muted-foreground" />
                </a>
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
