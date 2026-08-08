import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Textarea } from "@/components/ui/textarea";
import { ApplicationForm, FormField } from '@/api/applicationApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2 } from 'lucide-react';

interface PublicFormRendererProps {
  form: ApplicationForm;
  onSubmit: (data: Record<string, any>) => Promise<void>;
}

export function PublicFormRenderer({ form, onSubmit }: PublicFormRendererProps) {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (fieldId: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    const missingFields = form.schema_json.fields.filter(
      field => field.required && (formData[field.id] === undefined || formData[field.id] === '')
    );
    
    if (missingFields.length > 0) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setIsSubmitting(true);
      await onSubmit(formData);
    } catch (error) {
      console.error(error);
      toast.error('Failed to submit form');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderField = (field: FormField) => {
    switch (field.type) {
      case 'text':
        return (
          <Input 
            required={field.required}
            value={formData[field.id] || ''}
            onChange={(e) => handleInputChange(field.id, e.target.value)}
          />
        );
      case 'textarea':
        return (
          <Textarea 
            required={field.required}
            value={formData[field.id] || ''}
            onChange={(e) => handleInputChange(field.id, e.target.value)}
          />
        );
      case 'select':
        return (
          <Select 
            required={field.required}
            value={formData[field.id]}
            onValueChange={(val) => handleInputChange(field.id, val)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select an option" />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((opt, i) => (
                <SelectItem key={i} value={opt}>{opt}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      case 'radio':
        return (
          <RadioGroup 
            required={field.required}
            value={formData[field.id]}
            onValueChange={(val) => handleInputChange(field.id, val)}
          >
            {field.options?.map((opt, i) => (
              <div key={i} className="flex items-center space-x-2">
                <RadioGroupItem value={opt} id={`${field.id}-${i}`} />
                <Label htmlFor={`${field.id}-${i}`}>{opt}</Label>
              </div>
            ))}
          </RadioGroup>
        );
      case 'checkbox':
        return (
          <div className="space-y-2">
            {field.options?.map((opt, i) => (
              <div key={i} className="flex items-center space-x-2">
                <Checkbox 
                  id={`${field.id}-${i}`} 
                  checked={(formData[field.id] || []).includes(opt)}
                  onCheckedChange={(checked) => {
                    const current = formData[field.id] || [];
                    if (checked) {
                      handleInputChange(field.id, [...current, opt]);
                    } else {
                      handleInputChange(field.id, current.filter((v: string) => v !== opt));
                    }
                  }}
                />
                <Label htmlFor={`${field.id}-${i}`}>{opt}</Label>
              </div>
            ))}
          </div>
        );
      case 'file':
        return (
          <Input 
            type="file" 
            required={field.required}
            onChange={(e) => {
              // Usually handled with presigned URLs or FormData, for simplicity we store filename
              const file = e.target.files?.[0];
              if (file) handleInputChange(field.id, file.name);
            }}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-md">
      <CardHeader>
        <CardTitle className="text-2xl">{form.title}</CardTitle>
        {form.description && <CardDescription>{form.description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <form id="application-form" onSubmit={handleSubmit} className="space-y-6">
          {form.schema_json.fields.map((field) => (
            <div key={field.id} className="space-y-2">
              <Label className="text-base font-semibold">
                {field.label} {field.required && <span className="text-destructive">*</span>}
              </Label>
              {field.description && (
                <p className="text-sm text-muted-foreground">{field.description}</p>
              )}
              {renderField(field)}
            </div>
          ))}
        </form>
      </CardContent>
      <CardFooter className="bg-muted/30 flex justify-end p-6 border-t">
        <Button 
          type="submit" 
          form="application-form" 
          disabled={isSubmitting || form.schema_json.fields.length === 0}
        >
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Submit Application
        </Button>
      </CardFooter>
    </Card>
  );
}
