import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { incubationApi, type ProjectFunding } from '@/api/incubationApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Coins, Plus, Calendar } from 'lucide-react';
import { format } from 'date-fns';

interface FundingTimelineProps {
  projectId: string;
  fundingRounds: ProjectFunding[];
}

export function FundingTimeline({ projectId, fundingRounds }: FundingTimelineProps) {
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [roundType, setRoundType] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const createFunding = useMutation({
    mutationFn: (data: Partial<ProjectFunding>) => incubationApi.createFundingRound(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incubation-dashboard', projectId] });
      toast.success('Funding round added');
      setIsDialogOpen(false);
      setAmount('');
    },
    onError: () => toast.error('Failed to add funding round')
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createFunding.mutate({
      round_type: roundType,
      amount: parseFloat(amount),
      currency,
      date: new Date(date).toISOString()
    });
  };

  const totalFunding = fundingRounds.reduce((acc, round) => acc + round.amount, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold flex items-center gap-2">
          <Coins className="w-4 h-4 text-primary" />
          Funding Timeline
        </h3>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="ghost" className="h-8 px-2">
              <Plus className="w-4 h-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[400px]">
            <DialogHeader>
              <DialogTitle>Add Funding Round</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Round Type</Label>
                <Select value={roundType} onValueChange={setRoundType} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Pre-seed">Pre-seed</SelectItem>
                    <SelectItem value="Seed">Seed</SelectItem>
                    <SelectItem value="Series A">Series A</SelectItem>
                    <SelectItem value="Grant">Grant</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Amount</Label>
                  <Input type="number" step="1000" min="0" value={amount} onChange={e => setAmount(e.target.value)} required />
                </div>
                <div className="space-y-2">
                  <Label>Currency</Label>
                  <Input value={currency} onChange={e => setCurrency(e.target.value)} required />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Date</Label>
                <Input type="date" value={date} onChange={e => setDate(e.target.value)} required />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createFunding.isPending || !amount || !roundType}>
                  {createFunding.isPending ? 'Saving...' : 'Add Round'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-secondary/30 p-4 rounded-lg flex items-center justify-between mb-6">
        <span className="text-sm font-medium">Total Raised</span>
        <span className="text-xl font-bold tracking-tight text-primary">
          ${totalFunding.toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </span>
      </div>

      <div className="relative border-l border-border/50 ml-3 space-y-6">
        {fundingRounds.length === 0 ? (
          <p className="text-sm text-muted-foreground pl-4">No funding recorded.</p>
        ) : (
          fundingRounds.map((round, idx) => (
            <div key={round.id || idx} className="relative pl-6">
              <div className="absolute -left-1.5 top-1.5 w-3 h-3 bg-primary rounded-full ring-4 ring-background" />
              <div>
                <h4 className="text-sm font-bold">{round.round_type}</h4>
                <div className="text-lg font-semibold text-foreground/90 mt-1">
                  {round.currency === 'USD' ? '$' : ''}{round.amount.toLocaleString()} {round.currency !== 'USD' && round.currency}
                </div>
                <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                  <Calendar className="w-3 h-3" />
                  {format(new Date(round.date || round.created_at), 'PP')}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
