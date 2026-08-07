import { useState } from 'react'
import { MessageSquarePlus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { feedbackApi, type FeedbackType } from '@/api/feedbackApi'
import { toast } from 'sonner'
import { useLocation } from 'react-router-dom'

export function FeedbackWidget() {
  const [open, setOpen] = useState(false)
  const [type, setType] = useState<FeedbackType>('Bug')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const location = useLocation()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim()) {
      toast.error('Please enter a description')
      return
    }

    setIsSubmitting(true)
    try {
      await feedbackApi.createFeedback({
        type,
        description,
        url: window.location.origin + location.pathname
      })
      toast.success('Feedback submitted successfully!')
      setOpen(false)
      setDescription('')
    } catch (error) {
      toast.error('Failed to submit feedback')
      console.error(error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          className="fixed bottom-6 right-6 rounded-full shadow-lg h-14 w-14 p-0 z-50 flex items-center justify-center bg-primary text-primary-foreground hover:bg-primary/90 transition-transform hover:scale-105"
          title="Submit Feedback"
        >
          <MessageSquarePlus className="h-6 w-6" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Submit Feedback</DialogTitle>
          <DialogDescription>
            Help us improve the platform. What kind of feedback do you have?
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label htmlFor="type">Feedback Type</Label>
            <Select value={type} onValueChange={(v) => setType(v as FeedbackType)}>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Bug">Bug (Breaks existing behavior)</SelectItem>
                <SelectItem value="Friction">Friction (Confusing or slow)</SelectItem>
                <SelectItem value="Request">Request (New capability/feature)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Details</Label>
            <Textarea
              id="description"
              placeholder="Please describe the issue or your idea in detail..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[100px] resize-none"
            />
          </div>
          <div className="flex justify-end pt-4">
            <Button type="button" variant="outline" className="mr-2" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
