'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { 
  Card as CardType, 
  getPriorityColor, 
  getPriorityLabel, 
  formatDueDate,
  isCardOverdue 
} from '@/lib/types/kanban';
import { 
  GripVertical, 
  MoreVertical, 
  Calendar, 
  User, 
  Tag,
  AlertCircle,
  Clock
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu';

export interface KanbanCardProps {
  card: CardType;
  isDragging?: boolean;
  onClick?: (card: CardType) => void;
  onEdit?: (card: CardType) => void;
  onDelete?: (cardId: string) => void;
  onMove?: (cardId: string, columnId: string) => void;
  showDetails?: boolean;
  className?: string;
}

export function KanbanCard({
  card,
  isDragging = false,
  onClick,
  onEdit,
  onDelete,
  onMove,
  showDetails = true,
  className,
}: KanbanCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  const priorityColor = getPriorityColor(card.priority || 'medium');
  const priorityLabel = getPriorityLabel(card.priority || 'medium');
  const isOverdue = card.dueDate ? isCardOverdue(card) : false;
  const dueDateText = card.dueDate ? formatDueDate(card.dueDate) : null;
  
  const handleEdit = () => {
    onEdit?.(card);
  };
  
  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this card?')) {
      onDelete?.(card.id);
    }
  };
  
  return (
    <Card
      className={cn(
        'relative p-4 transition-all duration-200 cursor-grab active:cursor-grabbing',
        'hover:shadow-md hover:border-primary/50',
        isDragging && 'opacity-50 rotate-1 shadow-lg',
        isOverdue && 'border-error/50 bg-error/5',
        className
      )}
      onClick={() => onClick?.(card)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Drag handle */}
      <div className="absolute left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <GripVertical className="h-4 w-4 text-gray-400" />
      </div>
      
      {/* Card header */}
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-900 dark:text-gray-100 pr-6">
          {card.title}
        </h3>
        
        {(isHovered || showDetails) && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 -mt-1 -mr-1"
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleEdit}>
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDelete} className="text-error">
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
      
      {/* Card description */}
      {showDetails && card.description && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {card.description}
        </p>
      )}
      
      {/* Card metadata */}
      {showDetails && (
        <div className="flex flex-wrap items-center gap-2 mt-3">
          {/* Priority badge */}
          {card.priority && card.priority !== 'medium' && (
            <span
              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
              style={{
                backgroundColor: `${priorityColor}20`,
                color: priorityColor,
              }}
            >
              <AlertCircle className="h-3 w-3 mr-1" />
              {priorityLabel}
            </span>
          )}
          
          {/* Due date */}
          {card.dueDate && (
            <span
              className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                isOverdue
                  ? 'bg-error/10 text-error'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              )}
            >
              <Calendar className="h-3 w-3 mr-1" />
              {dueDateText}
            </span>
          )}
          
          {/* Assignee */}
          {card.assignee && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              <User className="h-3 w-3 mr-1" />
              {card.assignee}
            </span>
          )}
          
          {/* Tags */}
          {card.tags && card.tags.length > 0 && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              <Tag className="h-3 w-3 mr-1" />
              {card.tags.length} tag{card.tags.length !== 1 ? 's' : ''}
            </span>
          )}
          
          {/* Created time */}
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 ml-auto">
            <Clock className="h-3 w-3 mr-1" />
            {new Date(card.createdAt).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })}
          </span>
        </div>
      )}
      
      {/* Overdue indicator */}
      {isOverdue && (
        <div className="absolute top-0 right-0 w-3 h-3">
          <div className="absolute inset-0 bg-error rounded-full animate-ping" />
          <div className="absolute inset-0 bg-error rounded-full" />
        </div>
      )}
    </Card>
  );
}