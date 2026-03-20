'use client';

import React, { useState } from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { KanbanColumn as KanbanColumnType, KanbanCard as KanbanCardType } from '@/lib/types/kanban';
import { KanbanCard } from './KanbanCard';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Pencil, Plus, X, Check as CheckIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KanbanColumnProps {
  column: KanbanColumnType;
  cards: KanbanCardType[];
  onCardClick?: (card: KanbanCardType) => void;
  onCardDelete?: (cardId: string) => void;
  onCardEdit?: (card: KanbanCardType) => void;
  onCardMove?: (cardId: string, fromColumnId: string, toColumnId: string) => void;
  onColumnRename?: (columnId: string, newTitle: string) => void;
  onColumnDelete?: (columnId: string) => void;
  onAddCard?: (columnId: string, title: string) => void;
  isOverlay?: boolean;
}

export function KanbanColumn({
  column,
  cards,
  onCardClick,
  onCardDelete,
  onCardEdit,
  onCardMove,
  onColumnRename,
  onColumnDelete,
  onAddCard,
  isOverlay = false,
}: KanbanColumnProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(column.title);
  const [isAddingCard, setIsAddingCard] = useState(false);
  const [newCardTitle, setNewCardTitle] = useState('');

  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
  });

  const handleRenameSubmit = () => {
    if (editTitle.trim() && editTitle !== column.title) {
      onColumnRename?.(column.id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleAddCardSubmit = () => {
    if (newCardTitle.trim()) {
      // In a real implementation, this would call an API
      // For now, we'll just reset the state
      setNewCardTitle('');
      setIsAddingCard(false);
      onAddCard?.(column.id, newCardTitle);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, action: 'rename' | 'addCard') => {
    if (e.key === 'Enter') {
      if (action === 'rename') {
        handleRenameSubmit();
      } else {
        handleAddCardSubmit();
      }
    } else if (e.key === 'Escape') {
      if (action === 'rename') {
        setIsEditing(false);
        setEditTitle(column.title);
      } else {
        setIsAddingCard(false);
        setNewCardTitle('');
      }
    }
  };

  const columnCards = cards.filter(card => card.columnId === column.id);
  const cardIds = columnCards.map(card => card.id);

  return (
    <div
      ref={setNodeRef}
      className={cn(
        'flex flex-col w-80 min-w-80 h-full bg-gray-50 dark:bg-gray-900 rounded-lg border border-border-light dark:border-border-dark',
        isOver && 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700',
        isOverlay && 'opacity-50'
      )}
    >
      {/* Column Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-light dark:border-border-dark">
        <div className="flex items-center gap-2 flex-1">
          {isEditing ? (
            <div className="flex items-center gap-2 flex-1">
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'rename')}
                className="flex-1"
                autoFocus
              />
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRenameSubmit}
                className="h-8 w-8 p-0"
              >
                <CheckIcon className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setIsEditing(false);
                  setEditTitle(column.title);
                }}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {column.title}
              </h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                ({columnCards.length})
              </span>
              <div className="flex gap-1 ml-auto">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                  className="h-8 w-8 p-0"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onColumnDelete?.(column.id)}
                  className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Cards Container */}
      <div className="flex-1 p-2 overflow-y-auto">
        <SortableContext items={cardIds} strategy={verticalListSortingStrategy}>
          <div className="space-y-2">
            {columnCards.map((card) => (
              <KanbanCard
                key={card.id}
                card={card}
                onClick={() => onCardClick?.(card)}
                onDelete={() => onCardDelete?.(card.id)}
                onEdit={() => onCardEdit?.(card)}
              />
            ))}
          </div>
        </SortableContext>

        {/* Add Card Button */}
        {isAddingCard ? (
          <div className="mt-2 p-2 border border-border-light dark:border-border-dark rounded">
            <Input
              value={newCardTitle}
              onChange={(e) => setNewCardTitle(e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, 'addCard')}
              placeholder="Enter card title..."
              className="mb-2"
              autoFocus
            />
            <div className="flex gap-2">
              <Button
                onClick={handleAddCardSubmit}
                className="flex-1"
                size="sm"
              >
                Add Card
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  setIsAddingCard(false);
                  setNewCardTitle('');
                }}
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="ghost"
            onClick={() => setIsAddingCard(true)}
            className="w-full mt-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add a card
          </Button>
        )}
      </div>
    </div>
  );
}

// Helper component for check icon
function Check({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}