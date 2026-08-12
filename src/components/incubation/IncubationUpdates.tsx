import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { incubationApi, type ProjectUpdate } from '@/api/incubationApi';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { MessageSquare, Plus, Activity, TrendingUp, Presentation } from 'lucide-react';
import { format } from 'date-fns';

interface IncubationUpdatesProps {
  projectId: string;
  updates: ProjectUpdate[];
}

export function IncubationUpdates({ projectId, updates }: IncubationUpdatesProps) {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [updateType, setUpdateType] = useState<ProjectUpdate['update_type']>('progress_report');

  const createUpdate = useMutation({
    mutationFn: (data: Partial<ProjectUpdate>) => incubationApi.createUpdate(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incubation-dashboard', projectId] });
      toast.success('Update posted successfully');
      setIsDialogOpen(false);
      setTitle('');
      setContent('');
    },
    onError: () => toast.error('Failed to post update')
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createUpdate.mutate({ title, content, update_type: updateType });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'investor_update': return <Presentation className="w-5 h-5 text-blue-500" />;
      case 'kpi': return <TrendingUp className="w-5 h-5 text-green-500" />;
      default: return <Activity className="w-5 h-5 text-amber-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary" />
          Project Updates
        </h3>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Post Update
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Post a Project Update</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input value={title} onChange={e => setTitle(e.target.value)} required placeholder="Update title" />
              </div>
              <div className="space-y-2">
                <Label>Update Type</Label>
                <Select value={updateType} onValueChange={(val: any) => setUpdateType(val)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="progress_report">Progress Report</SelectItem>
                    <SelectItem value="investor_update">Investor Update</SelectItem>
                    <SelectItem value="kpi">KPI Update</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Content</Label>
                <Textarea 
                  value={content} 
                  onChange={e => setContent(e.target.value)} 
                  required 
                  placeholder="What's the latest with the project?"
                  className="h-32"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createUpdate.isPending || !title || !content}>
                  {createUpdate.isPending ? 'Posting...' : 'Post Update'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {updates.length === 0 ? (
          <GlassPanel className="p-8 text-center text-muted-foreground">
            No updates posted yet.
          </GlassPanel>
        ) : (
          updates.map(update => (
            <GlassPanel key={update.id} className="p-6 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-1 h-full bg-primary/20 group-hover:bg-primary transition-colors" />
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-secondary p-2 rounded-full">
                    {getTypeIcon(update.update_type)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-lg">{update.title}</h4>
                    <p className="text-xs text-muted-foreground">
                      {format(new Date(update.created_at), 'PPP')} • {update.update_type.replace('_', ' ')}
                    </p>
                  </div>
                </div>
              </div>
              <div className="text-sm whitespace-pre-wrap text-muted-foreground ml-12">
                {update.content}
              </div>
            </GlassPanel>
          ))
        )}
      </div>
    </div>
  );
}
