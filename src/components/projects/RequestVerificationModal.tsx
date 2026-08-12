import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { BadgeCheck } from 'lucide-react';
import { toast } from 'sonner';
import { verificationApi, type VerificationCreate } from '@/api/verificationApi';

interface RequestVerificationModalProps {
  workspaceId: string;
  projectId: string;
}

export function RequestVerificationModal({ workspaceId, projectId }: RequestVerificationModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [achievementType, setAchievementType] = useState('');
  const [achievementDetail, setAchievementDetail] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: VerificationCreate) => verificationApi.requestVerification(workspaceId, data),
    onSuccess: () => {
      toast.success('Verification request submitted successfully!');
      setIsOpen(false);
      setAchievementType('');
      setAchievementDetail('');
      setSourceUrl('');
      // Optionally invalidate queries if we show verifications in the project view later
      queryClient.invalidateQueries({ queryKey: ['governance-verifications', workspaceId] });
    },
    onError: () => {
      toast.error('Failed to submit verification request.');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!achievementType || !achievementDetail) return;
    
    mutation.mutate({
      entity_type: 'project',
      entity_id: projectId,
      achievement_type: achievementType,
      achievement_detail: achievementDetail,
      source: sourceUrl || undefined
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <BadgeCheck className="w-4 h-4 text-primary" /> Request Verification
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Request Trust Verification</DialogTitle>
            <DialogDescription>
              Submit an achievement or claim to be verified by workspace administrators or organizational validators.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="type">Achievement Type</Label>
              <Input 
                id="type" 
                placeholder="e.g. Launched Beta, 1000 Users, Patent Pending" 
                value={achievementType}
                onChange={e => setAchievementType(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="detail">Details / Claim</Label>
              <Textarea 
                id="detail" 
                placeholder="Provide specific details about your claim..." 
                value={achievementDetail}
                onChange={e => setAchievementDetail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source">Source / Evidence URL (Optional)</Label>
              <Input 
                id="source" 
                type="url"
                placeholder="https://news.ycombinator.com/..." 
                value={sourceUrl}
                onChange={e => setSourceUrl(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={() => setIsOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={mutation.isPending || !achievementType || !achievementDetail}>
              {mutation.isPending ? 'Submitting...' : 'Submit Request'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
