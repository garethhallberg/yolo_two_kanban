'use client';

import React, { useState, useMemo, useEffect } from 'react';
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
import { Plus, Settings, Loader2 } from 'lucide-react';
import { CardEditor } from './CardEditor';
import { Header } from '@/components/layout/Header';
import { useKanban } from '@/lib/context/KanbanContext';

interface KanbanBoardProps {
  initialBoard?: KanbanBoardType;
  onBoardChange?: (board: KanbanBoardType) => void;
}

export function KanbanBoard({ initialBoard, onBoardChange }: KanbanBoardProps) {
  const {
    board,
    loading,
    error,
    loadBoard,
    createColumn,
    updateColumn,
    deleteColumn,
    reorderColumn,
    createCard,
    updateCard,
    deleteCard,
    moveCard,
    reorderCard,
  } = useKanban();
  
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
    return board ? [...board.columns].sort((a, b) => a.position - b.position) : [];
  }, [board?.columns]);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    if (board) {
      const card = board.cards.find(c => c.id === active.id);
      if (card) {
        setActiveCard(card);
      }
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCard(null);

    if (!over || !board) return;

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
        
        moveCard(activeId, activeCard.columnId, overColumn.id, newPosition);
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
          
          moveCard(activeId, activeCard.columnId, overCard.columnId, newPosition);
        } else {
          // Reordering within the same column
          const columnCards = board.cards
            .filter(card => card.columnId === activeCard.columnId)
            .sort((a, b) => a.position - b.position);
          
          const oldIndex = columnCards.findIndex(c => c.id === activeId);
          const newIndex = columnCards.findIndex(c => c.id === overId);
          
          if (oldIndex !== newIndex) {
            reorderCard(activeId, newIndex);
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
        reorderColumn(activeId, newIndex);
      }
    }
  };

  const handleCardClick = (card: KanbanCardType) => {
    setEditingCard(card);
  };

  const handleCardDelete = (cardId: string) => {
    deleteCard(cardId);
  };

  const handleCardEdit = (card: KanbanCardType) => {
    setEditingCard(card);
  };

  const handleCardSave = (updatedCard: KanbanCardType) => {
    updateCard(updatedCard.id, updatedCard);
    setEditingCard(null);
  };

  const handleColumnRename = (columnId: string, newTitle: string) => {
    updateColumn(columnId, newTitle);
  };

  const handleColumnDelete = (columnId: string) => {
    if (window.confirm('Are you sure you want to delete this column? All cards in this column will also be deleted.')) {
      deleteColumn(columnId);
    }
  };

  const handleAddColumn = () => {
    if (newColumnTitle.trim() && board) {
      createColumn(newColumnTitle.trim());
      setNewColumnTitle('');
      setIsAddingColumn(false);
    }
  };

  const handleAddCard = (columnId: string, title: string) => {
    if (board) {
      const newCard: Partial<KanbanCardType> = {
        title: title,
        description: '',
        columnId,
        priority: 'medium',
        assignee: '',
        dueDate: new Date(Date.now() + 86400000 * 7), // 7 days from now
      };
      
      createCard(columnId, newCard).then(newCard => {
        if (newCard) {
          // Set the new card for editing
          setEditingCard(newCard);
        }
      });
    }
  };

  const columnIds = columns.map(col => col.id);

  return (
    <div className="flex flex-col h-full">
      {/* Loading state */}
      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-primary" />
            <p className="text-gray-600 dark:text-gray-300">Loading Kanban board...</p>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="bg-red-100 dark:bg-red-900 p-4 rounded-lg">
              <p className="text-red-600 dark:text-red-200">Error: {error}</p>
            </div>
            {error.includes('validate credentials') && (
              <Button onClick={() => window.location.href = '/login'} variant="outline">
                <Loader2 className="h-4 w-4 mr-2" />
                Login
              </Button>
            )}
            {!error.includes('validate credentials') && (
              <Button onClick={loadBoard} variant="outline">
                <Loader2 className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Not authenticated state */}
      {!board && !loading && !error && (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="bg-yellow-100 dark:bg-yellow-900 p-4 rounded-lg">
              <p className="text-yellow-600 dark:text-yellow-200">Please login to view your Kanban board</p>
            </div>
            <Button onClick={() => window.location.href = '/login'} variant="outline">
              Go to Login
            </Button>
          </div>
        </div>
      )}

      {/* Main content - only show when board is loaded */}
      {board && !loading && !error && (
        <>
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

          {/* Header */}
          <Header />

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
                      onColumnDelete={handleColumnDelete}
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
        </>
      )}
    </div>
  );
}