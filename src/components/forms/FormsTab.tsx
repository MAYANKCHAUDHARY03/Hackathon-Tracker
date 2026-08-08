import React, { useState, useEffect } from 'react';
import { applicationApi, ApplicationForm, FormSchema } from '@/api/applicationApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { FormBuilder } from './FormBuilder';
import { SubmissionsTable } from './SubmissionsTable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Copy, Plus, ExternalLink } from 'lucide-react';

interface FormsTabProps {
  hackathonId: string;
}

export function FormsTab({ hackathonId }: FormsTabProps) {
  const [forms, setForms] = useState<ApplicationForm[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newFormTitle, setNewFormTitle] = useState('');
  const [newFormSchema, setNewFormSchema] = useState<FormSchema>({ fields: [] });
  const [selectedForm, setSelectedForm] = useState<ApplicationForm | null>(null);
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    loadForms();
  }, [hackathonId]);

  const loadForms = async () => {
    try {
      const fetched = await applicationApi.listForms(hackathonId);
      setForms(fetched);
    } catch (error) {
      toast.error('Failed to load forms');
    }
  };

  const handleCreateForm = async () => {
    if (!newFormTitle.trim()) {
      toast.error('Title is required');
      return;
    }
    
    try {
      await applicationApi.createForm(hackathonId, {
        title: newFormTitle,
        schema_json: newFormSchema,
        is_published: false
      });
      toast.success('Form created successfully');
      setIsCreateOpen(false);
      setNewFormTitle('');
      setNewFormSchema({ fields: [] });
      loadForms();
    } catch (error) {
      toast.error('Failed to create form');
    }
  };

  const loadSubmissions = async () => {
    try {
      const fetched = await applicationApi.listSubmissions(hackathonId);
      setSubmissions(fetched as any);
    } catch (error) {
      toast.error('Failed to load submissions');
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, [hackathonId]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Application Forms</h2>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4"/> Create Form</Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Application Form</DialogTitle>
            </DialogHeader>
            <div className="space-y-6 py-4">
              <div className="space-y-2">
                <Label>Form Title</Label>
                <Input 
                  value={newFormTitle} 
                  onChange={e => setNewFormTitle(e.target.value)} 
                  placeholder="e.g. Startup Intake Application" 
                />
              </div>
              <div className="space-y-2">
                <Label>Form Fields</Label>
                <div className="border rounded-md p-4 bg-muted/10">
                  <FormBuilder 
                    fields={newFormSchema.fields} 
                    onChange={(fields) => setNewFormSchema({ fields })}
                  />
                </div>
              </div>
              <Button onClick={handleCreateForm} className="w-full">Save Form</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="forms">
        <TabsList>
          <TabsTrigger value="forms">Forms</TabsTrigger>
          <TabsTrigger value="submissions">Submissions</TabsTrigger>
        </TabsList>

        <TabsContent value="forms" className="space-y-4 pt-4">
          {forms.length === 0 ? (
            <div className="text-center p-8 border rounded-lg border-dashed text-muted-foreground">
              No forms created yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {forms.map(form => (
                <div key={form.id} className="border rounded-lg p-4 bg-card flex flex-col justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{form.title}</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      {form.schema_json.fields?.length || 0} fields
                    </p>
                  </div>
                  <div className="flex justify-between items-center mt-4">
                    <div className="flex items-center space-x-2">
                      <Switch 
                        checked={form.is_published} 
                        disabled
                      />
                      <Label className="text-xs">Published</Label>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => {
                      navigator.clipboard.writeText(`${window.location.origin}/apply/${form.id}`);
                      toast.success('Public link copied to clipboard');
                    }}>
                      <Copy className="h-4 w-4 mr-2" /> Link
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="submissions" className="pt-4">
          <SubmissionsTable 
            submissions={submissions}
            formSchema={forms[0]?.schema_json || { fields: [] }} 
            onStatusChange={loadSubmissions}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
