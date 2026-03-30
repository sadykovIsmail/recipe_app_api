import { clsx } from 'clsx';

interface BadgeProps {
  label: string;
  onRemove?: () => void;
  variant?: 'tag' | 'ingredient';
}

export function Badge({ label, onRemove, variant = 'tag' }: BadgeProps) {
  return (
    <span className={clsx(
      'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium',
      variant === 'tag'
        ? 'bg-brand-100 text-brand-800'
        : 'bg-green-100 text-green-800'
    )}>
      {label}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-0.5 hover:text-red-600 transition-colors"
          aria-label={`Remove ${label}`}
        >
          ×
        </button>
      )}
    </span>
  );
}
