import { useState, useEffect } from "react";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { evaluationsApi } from "@/api/evaluations";
import type { EvaluationTemplate } from "@/api/evaluations";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Button } from "@/components/ui/button";
import { ClipboardList, Plus } from "lucide-react";

interface EvaluationsTabProps {
  hackathonId: string;
}

export function EvaluationsTab({ hackathonId }: EvaluationsTabProps) {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [templates, setTemplates] = useState<EvaluationTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (activeWorkspaceId && hackathonId) {
      loadTemplates();
    }
  }, [activeWorkspaceId, hackathonId]);

  const loadTemplates = async () => {
    if (!activeWorkspaceId) return;
    setIsLoading(true);
    try {
      const res = await evaluationsApi.getTemplates(activeWorkspaceId, hackathonId);
      setTemplates(res);
    } catch (error) {
      console.error("Failed to load evaluation templates", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading templates...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Evaluation Templates</h2>
          <p className="text-sm text-muted-foreground">Define criteria for judging submissions.</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Create Template
        </Button>
      </div>

      {templates.length === 0 ? (
        <GlassPanel className="p-12 text-center flex flex-col items-center justify-center">
          <div className="bg-primary/10 p-4 rounded-full mb-4">
            <ClipboardList className="h-8 w-8 text-primary opacity-80" />
          </div>
          <h3 className="text-lg font-medium">No templates yet</h3>
          <p className="text-muted-foreground max-w-sm mt-1 mb-6">
            Create an evaluation template to define how judges will score the submissions.
          </p>
          <Button>Create your first template</Button>
        </GlassPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map(t => (
            <GlassPanel key={t.id} className="p-5 flex flex-col">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{t.name}</h3>
                {t.description && <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{t.description}</p>}
                
                <div className="mt-4 space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Criteria</p>
                  {t.criteria && t.criteria.length > 0 ? (
                    <ul className="text-sm space-y-1">
                      {t.criteria.map(c => (
                        <li key={c.id} className="flex justify-between items-center">
                          <span>{c.name}</span>
                          <span className="text-muted-foreground">{c.weight}%</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No criteria defined.</p>
                  )}
                </div>
              </div>
              <div className="mt-6 pt-4 border-t flex justify-end gap-2">
                <Button variant="outline" size="sm">Edit</Button>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
