import { useState } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragOverEvent,
  type DragEndEvent,
} from '@dnd-kit/core';
import { SortableContext, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import { type KanbanColumn as KanbanColumnType, type KanbanTask } from '@/api/kanbanApi';
import { KanbanColumn } from './KanbanColumn';
import { KanbanTaskCard } from './KanbanTaskCard';
import { TaskModal } from './TaskModal';
import { useKanban } from '@/hooks/useKanban';

interface KanbanBoardComponentProps {
  projectId: string;
}

export function KanbanBoard({ projectId }: KanbanBoardComponentProps) {
  const { board, isLoading, moveTask, createTask } = useKanban(projectId);
  const [activeColumn, setActiveColumn] = useState<KanbanColumnType | null>(null);
  const [activeTask, setActiveTask] = useState<KanbanTask | null>(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [targetColumnId, setTargetColumnId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor)
  );

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground">Loading board...</div>;
  }

  if (!board) {
    return <div className="p-8 text-center text-muted-foreground">No board found for this project.</div>;
  }

  const columns = board.columns;
  const columnIds = columns.map(c => c.id);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const { type, column, task } = active.data.current ?? {};
    
    if (type === 'Column') {
      setActiveColumn(column);
    } else if (type === 'Task') {
      setActiveTask(task);
    }
  };

  const handleDragOver = (_event: DragOverEvent) => {
    // For moving between columns, implement later
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveColumn(null);
    setActiveTask(null);

    const { active, over } = event;
    if (!over) return;

    const activeData = active.data.current;
    const overData = over.data.current;

    if (!activeData || !overData) return;

    if (activeData.type === 'Task') {
      const activeTask = activeData.task as KanbanTask;
      
      let destColId = '';
      let newPosition = 0;

      if (overData.type === 'Column') {
        const destCol = overData.column as KanbanColumnType;
        destColId = destCol.id;
        // Place at the end of the column
        const maxPos = destCol.tasks.length > 0 ? destCol.tasks[destCol.tasks.length - 1].position : 0;
        newPosition = maxPos + 1000;
      } else if (overData.type === 'Task') {
        const overTask = overData.task as KanbanTask;
        destColId = overTask.column_id;
        
        // Simple fractional ranking: put it right before the overTask
        const destCol = columns.find(c => c.id === destColId);
        if (destCol) {
          const overIndex = destCol.tasks.findIndex(t => t.id === overTask.id);
          const prevTask = overIndex > 0 ? destCol.tasks[overIndex - 1] : null;
          
          if (prevTask) {
            newPosition = (prevTask.position + overTask.position) / 2;
          } else {
            newPosition = overTask.position / 2;
          }
        }
      }

      if (destColId && (activeTask.column_id !== destColId || activeTask.position !== newPosition)) {
        moveTask(activeTask.id, activeTask.column_id, destColId, newPosition);
      }
    }
  };

  return (
    <div className="h-full w-full overflow-x-auto p-6">
      <h2 className="text-2xl font-bold mb-6">{board.name}</h2>
      
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-6 h-[calc(100vh-200px)]">
          <SortableContext items={columnIds} strategy={horizontalListSortingStrategy}>
            {columns.map(column => (
              <KanbanColumn
                key={column.id}
                column={column}
                onAddTask={(colId) => {
                  setTargetColumnId(colId);
                  setIsTaskModalOpen(true);
                }}
                onTaskClick={(task) => console.log('Task clicked', task)}
              />
            ))}
          </SortableContext>
        </div>

        <DragOverlay>
          {activeColumn ? (
            <KanbanColumn column={activeColumn} />
          ) : activeTask ? (
            <KanbanTaskCard task={activeTask} />
          ) : null}
        </DragOverlay>
      </DndContext>

      <TaskModal 
        isOpen={isTaskModalOpen} 
        onClose={() => setIsTaskModalOpen(false)}
        onSubmit={async (title, desc) => {
          if (targetColumnId) {
            await createTask(targetColumnId, title, desc);
          }
        }}
      />
    </div>
  );
}
