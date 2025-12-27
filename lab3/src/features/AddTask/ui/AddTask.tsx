import React, { useState } from 'react';
import { Button } from '@shared/ui/Button/Button';
import { Input } from '@shared/ui/Input/Input';

interface AddTaskProps {
    onAdd: (text: string) => void;
}

export const AddTask: React.FC<AddTaskProps> = ({ onAdd }) => {
    const [value, setValue] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (value.trim()) {
            onAdd(value);
            setValue('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex gap-3 mb-8">
            <Input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Что планируете сделать?"
                autoFocus
            />
            <Button type="submit" className="w-14 h-[50px]">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
            </Button>
        </form>
    );
};
