import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { type KanbanColumn as KanbanColumnType, type KanbanTask } from '@/api/kanbanApi';
import { KanbanTaskCard } from './KanbanTaskCard';

interface KanbanColumnProps {
  column: KanbanColumnType;
  onTaskClick?: (task: KanbanTask) => void;
  onAddTask?: (columnId: string) => void;
}

export function KanbanColumn({ column, onTaskClick, onAddTask }: KanbanColumnProps) {
  const { setNodeRef, attributes, listeners, transform, transition, isDragging } = useSortable({
    id: column.id,
    data: {
      type: 'Column',
      column,
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
      className={`flex flex-col bg-muted/50 rounded-xl w-80 shrink-0 ${
        isDragging ? 'opacity-30 border-2 border-primary' : ''
      }`}
    >
      {/* Column Header */}
      <div 
        {...attributes}
        {...listeners}
        className="p-4 flex items-center justify-between cursor-grab font-semibold text-sm border-b border-border"
      >
        <span>{column.name}</span>
        <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
          {column.tasks.length}
        </span>
      </div>

      {/* Task List */}
      <div className="p-3 flex-1 overflow-y-auto flex flex-col gap-3 min-h-[150px]">
        <SortableContext items={column.tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
          {column.tasks.map(task => (
            <KanbanTaskCard key={task.id} task={task} onClick={onTaskClick} />
          ))}
        </SortableContext>
      </div>

      {/* Add Task Button */}
      {onAddTask && (
        <div className="p-3 pt-0">
          <button
            onClick={() => onAddTask(column.id)}
            className="w-full py-2 text-sm text-muted-foreground hover:bg-muted rounded-md flex items-center justify-center transition-colors"
          >
            + Add Task
          </button>
        </div>
      )}
    </div>
  );
}
