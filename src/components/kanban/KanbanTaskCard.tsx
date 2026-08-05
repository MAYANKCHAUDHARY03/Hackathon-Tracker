import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { type KanbanTask } from '@/api/kanbanApi';

interface KanbanTaskCardProps {
  task: KanbanTask;
  onClick?: (task: KanbanTask) => void;
}

export function KanbanTaskCard({ task, onClick }: KanbanTaskCardProps) {
  const { setNodeRef, attributes, listeners, transform, transition, isDragging } = useSortable({
    id: task.id,
    data: {
      type: 'Task',
      task,
    },
  });

  const style = {
    transition,
    transform: CSS.Transform.toString(transform),
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={() => onClick?.(task)}
      className={`p-3 bg-white rounded-md shadow-sm border border-border cursor-grab hover:bg-accent/50 ${
        isDragging ? 'opacity-30 border-primary' : ''
      }`}
    >
      <h4 className="text-sm font-medium text-foreground">{task.title}</h4>
      {task.description && (
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{task.description}</p>
      )}
    </div>
  );
}
