'use client';

import React, { useState, useMemo } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from '@dnd-kit/core';
import { arrayMove, SortableContext } from '@dnd-kit/sortable';
import { KanbanColumn } from './KanbanColumn';
import { KanbanCard } from './KanbanCard';
import { KanbanBoard as KanbanBoardType, KanbanColumn as KanbanColumnType, KanbanCard as KanbanCardType } from '@/lib/types/kanban';
import { Button } from '@/components/ui/Button';
import { Plus, Settings } from 'lucide-react';
import { CardEditor } from './CardEditor';

interface KanbanBoardProps {
  initialBoard?: KanbanBoardType;
  onBoardChange?: (board: KanbanBoardType) => void;
}

export function KanbanBoard({ initialBoard, onBoardChange }: KanbanBoardProps) {
  const [board, setBoard] = useState<KanbanBoardType>(
    initialBoard || {
      id: 'board-1',
      title: 'Project Board',
      userId: 'user-1',
      createdAt: new Date(),
      updatedAt: new Date(),
      columns: [
        { id: 'todo', title: 'To Do', position: 0, boardId: 'board-1', createdAt: new Date(), updatedAt: new Date() },
        { id: 'in-progress', title: 'In Progress', position: 1, boardId: 'board-1', createdAt: new Date(), updatedAt: new Date() },
        { id: 'review', title: 'Review', position: 2, boardId: 'board-1', createdAt: new Date(), updatedAt: new Date() },
        { id: 'done', title: 'Done', position: 3, boardId: 'board-1', createdAt: new Date(), updatedAt: new Date() },
      ],
      cards: [
        {
          id: 'card-1',
          title: 'Implement drag and drop',
          description: 'Add drag and drop functionality to Kanban board',
          columnId: 'todo',
          position: 0,
          priority: 'high',
          assignee: 'John Doe',
          dueDate: new Date(Date.now() + 86400000 * 3), // 3 days from now
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: 'card-2',
          title: 'Design UI components',
          description: 'Create reusable UI components for the project',
          columnId: 'in-progress',
          position: 0,
          priority: 'medium',
          assignee: 'Jane Smith',
          dueDate: new Date(Date.now() + 86400000 * 2), // 2 days from now
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: 'card-3',
          title: 'Set up database',
          description: 'Configure SQLite database with proper schema',
          columnId: 'done',
          position: 0,
          priority: 'low',
          assignee: 'Bob Johnson',
          dueDate: new Date(Date.now() - 86400000), // 1 day ago
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
    }
  );

  const [activeCard, setActiveCard] = useState<KanbanCardType | null>(null);
  const [editingCard, setEditingCard] = useState<KanbanCardType | null>(null);
  const [isAddingColumn, setIsAddingColumn] = useState(false);
  const [newColumnTitle, setNewColumnTitle] = useState('');

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const columns = useMemo(() => {
    return [...board.columns].sort((a, b) => a.position - b.position);
  }, [board.columns]);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const card = board.cards.find(c => c.id === active.id);
    if (card) {
      setActiveCard(card);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCard(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // If dragging a card
    const activeCard = board.cards.find(c => c.id === activeId);
    if (activeCard) {
      // Check if dropped on a column
      const overColumn = board.columns.find(c => c.id === overId);
      if (overColumn) {
        // Move card to new column
        const targetColumnCards = board.cards
          .filter(card => card.columnId === overColumn.id)
          .sort((a, b) => a.position - b.position);
        
        // Determine position in new column (add to end)
        const newPosition = targetColumnCards.length;
        
        const updatedCards = board.cards.map(card =>
          card.id === activeId 
            ? { ...card, columnId: overColumn.id, position: newPosition }
            : card
        );
        const updatedBoard = { ...board, cards: updatedCards };
        setBoard(updatedBoard);
        onBoardChange?.(updatedBoard);
        return;
      }

      // Check if dropped on another card
      const overCard = board.cards.find(c => c.id === overId);
      if (overCard) {
        // Both cards should be in the same column for reordering
        if (activeCard.columnId !== overCard.columnId) {
          // Moving to a different column
          const targetColumnCards = board.cards
            .filter(card => card.columnId === overCard.columnId)
            .sort((a, b) => a.position - b.position);
          
          const overCardIndex = targetColumnCards.findIndex(c => c.id === overId);
          const newPosition = overCardIndex;
          
          // Update positions for cards in target column
          const updatedCards = board.cards.map(card => {
            if (card.columnId === overCard.columnId && card.id !== activeId) {
              if (card.position >= newPosition) {
                return { ...card, position: card.position + 1 };
              }
            }
            return card;
          });
          
          // Add the active card with new position
          const finalCards = updatedCards.map(card =>
            card.id === activeId
              ? { ...card, columnId: overCard.columnId, position: newPosition }
              : card
          );
          
          const updatedBoard = { ...board, cards: finalCards };
          setBoard(updatedBoard);
          onBoardChange?.(updatedBoard);
        } else {
          // Reordering within the same column
          const columnCards = board.cards
            .filter(card => card.columnId === activeCard.columnId)
            .sort((a, b) => a.position - b.position);
          
          const oldIndex = columnCards.findIndex(c => c.id === activeId);
          const newIndex = columnCards.findIndex(c => c.id === overId);
          
          if (oldIndex !== newIndex) {
            const reorderedCards = arrayMove(columnCards, oldIndex, newIndex);
            
            // Update positions
            const positionMap = new Map<string, number>();
            reorderedCards.forEach((card, index) => {
              positionMap.set(card.id, index);
            });
            
            const updatedCards = board.cards.map(card => 
              positionMap.has(card.id) 
                ? { ...card, position: positionMap.get(card.id)! }
                : card
            );
            
            const updatedBoard = { ...board, cards: updatedCards };
            setBoard(updatedBoard);
            onBoardChange?.(updatedBoard);
          }
        }
        return;
      }
    }

    // If dragging a column
    const activeColumn = board.columns.find(c => c.id === activeId);
    if (activeColumn) {
      const oldIndex = columns.findIndex(c => c.id === activeId);
      const newIndex = columns.findIndex(c => c.id === overId);
      
      if (oldIndex !== newIndex) {
        const updatedColumns = arrayMove(columns, oldIndex, newIndex).map((col, idx) => ({
          ...col,
          position: idx,
        }));
        const updatedBoard = { ...board, columns: updatedColumns };
        setBoard(updatedBoard);
        onBoardChange?.(updatedBoard);
      }
    }
  };

  const handleCardClick = (card: KanbanCardType) => {
    setEditingCard(card);
  };

  const handleCardDelete = (cardId: string) => {
    const updatedCards = board.cards.filter(card => card.id !== cardId);
    const updatedBoard = { ...board, cards: updatedCards };
    setBoard(updatedBoard);
    onBoardChange?.(updatedBoard);
  };

  const handleCardEdit = (card: KanbanCardType) => {
    setEditingCard(card);
  };

  const handleCardSave = (updatedCard: KanbanCardType) => {
    const updatedCards = board.cards.map(card =>
      card.id === updatedCard.id ? updatedCard : card
    );
    const updatedBoard = { ...board, cards: updatedCards };
    setBoard(updatedBoard);
    onBoardChange?.(updatedBoard);
    setEditingCard(null);
  };

  const handleColumnRename = (columnId: string, newTitle: string) => {
    const updatedColumns = board.columns.map(column =>
      column.id === columnId ? { ...column, title: newTitle } : column
    );
    const updatedBoard = { ...board, columns: updatedColumns };
    setBoard(updatedBoard);
    onBoardChange?.(updatedBoard);
  };

  const handleAddColumn = () => {
    if (newColumnTitle.trim()) {
      const newColumn: KanbanColumnType = {
        id: `column-${Date.now()}`,
        title: newColumnTitle.trim(),
        position: board.columns.length,
        boardId: board.id,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      const updatedColumns = [...board.columns, newColumn];
      const updatedBoard = { ...board, columns: updatedColumns };
      setBoard(updatedBoard);
      onBoardChange?.(updatedBoard);
      setNewColumnTitle('');
      setIsAddingColumn(false);
    }
  };

  const handleAddCard = (columnId: string) => {
    const newCard: KanbanCardType = {
      id: `card-${Date.now()}`,
      title: 'New Card',
      description: '',
      columnId,
      position: board.cards.filter(c => c.columnId === columnId).length,
      priority: 'medium',
      assignee: '',
      dueDate: new Date(Date.now() + 86400000 * 7), // 7 days from now
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    const updatedCards = [...board.cards, newCard];
    const updatedBoard = { ...board, cards: updatedCards };
    setBoard(updatedBoard);
    onBoardChange?.(updatedBoard);
    setEditingCard(newCard);
  };

  const columnIds = columns.map(col => col.id);

  return (
    <div className="flex flex-col h-full">
      {/* Board Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-light dark:border-border-dark">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {board.title}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {board.cards.length} cards across {board.columns.length} columns
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button onClick={() => setIsAddingColumn(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Column
          </Button>
        </div>
      </div>

      {/* Add Column Form */}
      {isAddingColumn && (
        <div className="p-4 border-b border-border-light dark:border-border-dark">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newColumnTitle}
              onChange={(e) => setNewColumnTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAddColumn();
                if (e.key === 'Escape') {
                  setIsAddingColumn(false);
                  setNewColumnTitle('');
                }
              }}
              placeholder="Enter column title..."
              className="flex-1 px-3 py-2 border border-border-light dark:border-border-dark rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
              autoFocus
            />
            <Button onClick={handleAddColumn}>Add</Button>
            <Button
              variant="ghost"
              onClick={() => {
                setIsAddingColumn(false);
                setNewColumnTitle('');
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Board Content */}
      <div className="flex-1 overflow-x-auto p-4">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-4 h-full">
            <SortableContext items={columnIds}>
              {columns.map((column) => (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  cards={board.cards}
                  onCardClick={handleCardClick}
                  onCardDelete={handleCardDelete}
                  onCardEdit={handleCardEdit}
                  onColumnRename={handleColumnRename}
                  onAddCard={handleAddCard}
                />
              ))}
            </SortableContext>
          </div>

          <DragOverlay>
            {activeCard && (
              <div className="opacity-80">
                <KanbanCard card={activeCard} />
              </div>
            )}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Card Editor Modal */}
      {editingCard && (
        <CardEditor
          card={editingCard}
          onSave={handleCardSave}
          onCancel={() => setEditingCard(null)}
        />
      )}
    </div>
  );
}