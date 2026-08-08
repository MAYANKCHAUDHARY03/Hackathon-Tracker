import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { applicationApi, ApplicationForm } from '@/api/applicationApi';
import { PublicFormRenderer } from '@/components/forms/PublicFormRenderer';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export default function ApplyPage() {
  const { formId } = useParams<{ formId: string }>();
  const navigate = useNavigate();
  const [form, setForm] = useState<ApplicationForm | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitted, setIsSubmitted] = useState(false);

  useEffect(() => {
    if (formId) {
      applicationApi.getForm(formId)
        .then(setForm)
        .catch(err => {
          console.error(err);
          toast.error("Form not found or you do not have access");
        })
        .finally(() => setIsLoading(false));
    }
  }, [formId]);

  const handleSubmit = async (data: Record<string, any>) => {
    if (!formId) return;
    try {
      await applicationApi.submitApplication(formId, { data_json: data });
      setIsSubmitted(true);
    } catch (error) {
      throw error; // Let PublicFormRenderer catch and show toast
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!form) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-background text-center p-4">
        <h1 className="text-2xl font-bold mb-2">Form Not Found</h1>
        <p className="text-muted-foreground mb-6">The application form you are looking for does not exist or has been removed.</p>
        <Button onClick={() => navigate('/')}>Return Home</Button>
      </div>
    );
  }

  if (isSubmitted) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
        <div className="max-w-md w-full bg-card rounded-lg shadow-lg border p-8 text-center space-y-4">
          <div className="flex justify-center">
            <CheckCircle2 className="h-16 w-16 text-green-500" />
          </div>
          <h2 className="text-2xl font-bold">Application Submitted!</h2>
          <p className="text-muted-foreground">
            Thank you for applying. We have received your submission and will review it shortly.
          </p>
          <Button className="mt-4" variant="outline" onClick={() => window.location.reload()}>
            Submit Another Response
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center">
          <div className="h-12 w-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="font-bold text-xl">H</span>
          </div>
          <p className="text-sm font-medium text-muted-foreground tracking-wider uppercase">Hackathon OS Application</p>
        </div>
        <PublicFormRenderer form={form} onSubmit={handleSubmit} />
      </div>
    </div>
  );
}
