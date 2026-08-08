import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Dialog, 
  DialogContent, 
  DialogTitle, 
  DialogDescription
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/lib/api-client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { toast } from 'sonner';
import { Trophy, Lightbulb, Rocket, Building2, ChevronRight, ChevronLeft } from 'lucide-react';
import type { Hackathon } from '@/types';

interface ProgramCreationWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

type TemplateType = 'hackathon' | 'challenge' | 'campaign' | 'incubation' | 'custom';

const TEMPLATES = [
  { id: 'hackathon', title: 'Standard Hackathon', description: 'Traditional time-boxed building event with teams and judges.', icon: Trophy, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { id: 'challenge', title: 'Innovation Challenge', description: 'Longer-term ideation and problem-solving competition.', icon: Lightbulb, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  { id: 'incubation', title: 'Startup Incubation', description: 'Multi-phase program for accelerating early-stage startups.', icon: Rocket, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { id: 'campaign', title: 'Internal Campaign', description: 'Employee-focused ideation and innovation initiatives.', icon: Building2, color: 'text-green-500', bg: 'bg-green-500/10' },
];

export function ProgramCreationWizard({ open, onOpenChange, onSuccess }: ProgramCreationWizardProps) {
  const navigate = useNavigate();
  const { activeWorkspaceId } = useWorkspaceStore();
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    program_type: 'hackathon' as TemplateType,
    start_date: '',
    end_date: '',
    is_online: true,
    location: ''
  });

  const handleNext = () => setStep(s => s + 1);
  const handleBack = () => setStep(s => s - 1);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;

    setIsSubmitting(true);
    try {
      // If we have templates in the backend, we would call /from-template/{templateId}
      // For now, we will create a standard program using the chosen program_type
      const res = await apiClient.post<Hackathon>(`/workspaces/${activeWorkspaceId}/hackathons`, {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: new Date(formData.end_date).toISOString(),
      });
      
      toast.success('Program created successfully!');
      onOpenChange(false);
      onSuccess?.();
      navigate(`/hackathons/${res.id}`);
      
      // Reset
      setStep(1);
      setFormData({
        name: '',
        description: '',
        program_type: 'hackathon',
        start_date: '',
        end_date: '',
        is_online: true,
        location: ''
      });
    } catch (err: any) {
      toast.error(err.message || 'Failed to create program');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] gap-0 p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-border/50 bg-secondary/30">
          <DialogTitle className="text-xl">Create Program</DialogTitle>
          <DialogDescription>
            {step === 1 ? 'Select a program template to get started.' : 'Configure your program details.'}
          </DialogDescription>
        </div>

        <div className="p-6">
          {step === 1 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {TEMPLATES.map(t => {
                const Icon = t.icon;
                const isSelected = formData.program_type === t.id;
                
                return (
                  <div
                    key={t.id}
                    onClick={() => setFormData({ ...formData, program_type: t.id as TemplateType })}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${
                      isSelected 
                        ? 'border-primary bg-primary/5' 
                        : 'border-border/50 hover:border-primary/50 hover:bg-secondary/20'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${t.bg} ${t.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold mb-1">{t.title}</h3>
                    <p className="text-xs text-muted-foreground">{t.description}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <form id="program-form" onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Program Name</Label>
                <Input 
                  id="name" 
                  value={formData.name}
                  onChange={(e: any) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Global Innovation Challenge 2026"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea 
                  id="description" 
                  value={formData.description}
                  onChange={(e: any) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Briefly describe the goals of this program..."
                  className="resize-none"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input 
                    id="start_date" 
                    type="date"
                    value={formData.start_date}
                    onChange={(e: any) => setFormData({ ...formData, start_date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input 
                    id="end_date" 
                    type="date"
                    value={formData.end_date}
                    onChange={(e: any) => setFormData({ ...formData, end_date: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Format</Label>
                <Select 
                  value={formData.is_online ? 'online' : 'hybrid'} 
                  onValueChange={v => setFormData({ ...formData, is_online: v === 'online' })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="online">Online / Virtual</SelectItem>
                    <SelectItem value="hybrid">In-Person / Hybrid</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {!formData.is_online && (
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input 
                    id="location" 
                    value={formData.location}
                    onChange={(e: any) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="e.g., San Francisco, CA"
                    required={!formData.is_online}
                  />
                </div>
              )}
            </form>
          )}
        </div>

        <div className="px-6 py-4 border-t border-border/50 bg-secondary/10 flex justify-between">
          {step === 1 ? (
            <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancel</Button>
          ) : (
            <Button variant="ghost" onClick={handleBack}><ChevronLeft className="w-4 h-4 mr-2" /> Back</Button>
          )}

          {step === 1 ? (
            <Button onClick={handleNext}>Next Step <ChevronRight className="w-4 h-4 ml-2" /></Button>
          ) : (
            <Button type="submit" form="program-form" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Program'}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
