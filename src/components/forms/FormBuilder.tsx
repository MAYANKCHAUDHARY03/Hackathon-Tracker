import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Trash2, Plus, GripVertical } from 'lucide-react';
import { FormField } from '@/api/applicationApi';

interface FormBuilderProps {
  fields: FormField[];
  onChange: (fields: FormField[]) => void;
}

export function FormBuilder({ fields, onChange }: FormBuilderProps) {
  const [draggedItem, setDraggedItem] = useState<number | null>(null);

  const addField = () => {
    const newField: FormField = {
      id: crypto.randomUUID(),
      type: 'text',
      label: 'New Field',
      required: false,
    };
    onChange([...fields, newField]);
  };

  const updateField = (id: string, updates: Partial<FormField>) => {
    onChange(fields.map(f => f.id === id ? { ...f, ...updates } : f));
  };

  const removeField = (id: string) => {
    onChange(fields.filter(f => f.id !== id));
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (index: number) => {
    if (draggedItem === null || draggedItem === index) return;
    
    const newFields = [...fields];
    const item = newFields[draggedItem];
    newFields.splice(draggedItem, 1);
    newFields.splice(index, 0, item);
    
    setDraggedItem(index);
    onChange(newFields);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {fields.map((field, index) => (
          <Card 
            key={field.id}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => { e.preventDefault(); handleDragOver(index); }}
            onDragEnd={handleDragEnd}
            className={`border border-border transition-colors ${draggedItem === index ? 'opacity-50' : 'bg-card'}`}
          >
            <div className="flex items-center gap-2 px-4 py-2 border-b bg-muted/30 cursor-grab">
              <GripVertical className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Field {index + 1}</span>
              <Button 
                variant="ghost" 
                size="icon" 
                className="ml-auto h-8 w-8 text-destructive"
                onClick={() => removeField(field.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            
            <CardContent className="space-y-4 pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Field Label</Label>
                  <Input 
                    value={field.label} 
                    onChange={(e) => updateField(field.id, { label: e.target.value })} 
                    placeholder="e.g. What is your role?"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Field Type</Label>
                  <Select 
                    value={field.type} 
                    onValueChange={(val: any) => updateField(field.id, { type: val })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Short Text</SelectItem>
                      <SelectItem value="textarea">Long Text</SelectItem>
                      <SelectItem value="select">Dropdown (Select)</SelectItem>
                      <SelectItem value="radio">Radio Buttons</SelectItem>
                      <SelectItem value="checkbox">Checkboxes</SelectItem>
                      <SelectItem value="file">File Upload</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Description (Optional)</Label>
                <Input 
                  value={field.description || ''} 
                  onChange={(e) => updateField(field.id, { description: e.target.value })}
                  placeholder="Help text for the user"
                />
              </div>
              
              {(field.type === 'select' || field.type === 'radio' || field.type === 'checkbox') && (
                <div className="space-y-2">
                  <Label>Options (Comma separated)</Label>
                  <Textarea 
                    value={field.options?.join(', ') || ''} 
                    onChange={(e) => updateField(field.id, { 
                      options: e.target.value.split(',').map(s => s.trim()).filter(Boolean) 
                    })}
                    placeholder="Option 1, Option 2, Option 3"
                    className="min-h-[80px]"
                  />
                </div>
              )}
              
              <div className="flex items-center space-x-2 pt-2">
                <Checkbox 
                  id={`required-${field.id}`}
                  checked={field.required}
                  onCheckedChange={(checked) => updateField(field.id, { required: !!checked })}
                />
                <Label htmlFor={`required-${field.id}`}>Required field</Label>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <Button 
        type="button" 
        variant="outline" 
        className="w-full border-dashed"
        onClick={addField}
      >
        <Plus className="mr-2 h-4 w-4" /> Add Field
      </Button>
    </div>
  );
}
