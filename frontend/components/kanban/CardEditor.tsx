'use client';

import React, { useState } from 'react';
import { KanbanCard as KanbanCardType, Priority } from '@/lib/types/kanban';
import { 
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
} from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Textarea } from '../ui/Textarea';
import { Calendar, User, Tag, X } from 'lucide-react';
import { format } from 'date-fns';

interface CardEditorProps {
  card: KanbanCardType;
  onSave: (card: KanbanCardType) => void;
  onCancel: () => void;
}

export function CardEditor({ card, onSave, onCancel }: CardEditorProps) {
  const [editedCard, setEditedCard] = useState<KanbanCardType>({ ...card });
  const [dueDateInput, setDueDateInput] = useState(
    card.dueDate ? format(card.dueDate, 'yyyy-MM-dd') : ''
  );
  const [description, setDescription] = useState(card.description || '');

  const handleSave = () => {
    const updatedCard: KanbanCardType = {
      ...editedCard,
      description,
      dueDate: dueDateInput ? new Date(dueDateInput) : undefined,
      updatedAt: new Date(),
    };
    onSave(updatedCard);
  };

  const handlePriorityChange = (priority: Priority) => {
    setEditedCard((prev: KanbanCardType) => ({ ...prev, priority }));
  };

  return (
    <Modal open={true} onOpenChange={(open) => !open && onCancel()}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>Edit Card</ModalTitle>
        </ModalHeader>
        <div className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Title
            </label>
            <Input
              value={editedCard.title}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditedCard((prev: KanbanCardType) => ({ ...prev, title: e.target.value }))}
              placeholder="Enter card title"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <Textarea
              value={description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
              placeholder="Enter card description"
              rows={4}
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Priority
            </label>
            <div className="flex gap-2">
              {(['low', 'medium', 'high'] as Priority[]).map((priority) => (
                <Button
                  key={priority}
                  type="button"
                  variant={editedCard.priority === priority ? 'default' : 'outline'}
                  onClick={() => handlePriorityChange(priority)}
                  className="capitalize"
                >
                  <Tag className="h-4 w-4 mr-2" />
                  {priority}
                </Button>
              ))}
            </div>
          </div>

          {/* Assignee */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Assignee
            </label>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-gray-400" />
              <Input
                value={editedCard.assignee || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditedCard((prev: KanbanCardType) => ({ ...prev, assignee: e.target.value }))}
                placeholder="Assign to..."
              />
            </div>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Due Date
            </label>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-400" />
              <Input
                type="date"
                value={dueDateInput}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDueDateInput(e.target.value)}
              />
              {dueDateInput && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setDueDateInput('')}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="pt-4 border-t border-border-light dark:border-border-dark">
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-500 dark:text-gray-400">
              <div>
                <span className="font-medium">Created:</span>{' '}
                {format(card.createdAt, 'MMM d, yyyy')}
              </div>
              <div>
                <span className="font-medium">Last Updated:</span>{' '}
                {format(card.updatedAt, 'MMM d, yyyy')}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              Save Changes
            </Button>
          </div>
        </div>
      </ModalContent>
    </Modal>
  );
}