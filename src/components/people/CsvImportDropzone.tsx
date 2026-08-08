import { useState, useRef } from "react";
import { UploadCloud, FileType, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { peopleApi } from "@/api/people";
import type { CsvImportResult } from "@/api/people";
import { toast } from "sonner";

interface CsvImportDropzoneProps {
  workspaceId: string;
  hackathonId: string;
  onImportComplete: () => void;
  onCancel: () => void;
}

export function CsvImportDropzone({ workspaceId, hackathonId, onImportComplete, onCancel }: CsvImportDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<CsvImportResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
      } else {
        toast.error("Please upload a .csv file");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    try {
      const res = await peopleApi.importPeopleCsv(workspaceId, hackathonId, file);
      setResult(res);
      toast.success(`Imported ${res.successful} people successfully`);
      if (res.successful > 0) {
        onImportComplete();
      }
    } catch (error: any) {
      toast.error(error.data?.detail || "Failed to import CSV");
    } finally {
      setIsUploading(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-green-500">
          <CheckCircle2 className="h-5 w-5" />
          <h3 className="font-semibold">Import Complete</h3>
        </div>
        <div className="space-y-2 text-sm">
          <p>Total Processed: {result.total_processed}</p>
          <p>Successful: {result.successful}</p>
          <p>Failed: {result.failed}</p>
          {result.errors.length > 0 && (
            <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md max-h-40 overflow-y-auto">
              <p className="font-semibold mb-2">Errors:</p>
              <ul className="list-disc pl-4 space-y-1">
                {result.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="pt-4 flex justify-end">
          <Button onClick={onCancel}>Close</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div 
        className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer ${isDragging ? 'border-primary bg-primary/5' : 'border-border/50 hover:border-primary/50'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          accept=".csv" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
        />
        
        {file ? (
          <>
            <FileType className="h-10 w-10 text-primary mb-4" />
            <p className="font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </>
        ) : (
          <>
            <UploadCloud className="h-10 w-10 text-muted-foreground mb-4" />
            <p className="font-medium mb-1">Drag and drop your CSV here</p>
            <p className="text-sm text-muted-foreground">or click to browse</p>
            <div className="mt-4 text-xs text-muted-foreground bg-secondary/50 p-3 rounded text-left max-w-sm">
              <p className="font-semibold mb-1">Required Headers:</p>
              <p className="font-mono bg-background px-1 py-0.5 rounded inline-block">email, full_name, role</p>
              <p className="mt-2 font-semibold mb-1">Optional Headers:</p>
              <p className="font-mono bg-background px-1 py-0.5 rounded inline-block">organisation, designation, expertise_areas</p>
              <p className="mt-2 italic">* role must be "mentor" or "judge"</p>
            </div>
          </>
        )}
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onCancel}>Cancel</Button>
        <Button onClick={handleUpload} disabled={!file || isUploading}>
          {isUploading ? "Importing..." : "Import CSV"}
        </Button>
      </div>
    </div>
  );
}
