import Image from 'next/image';
import { clsx } from 'clsx';

interface AvatarProps {
  src: string | null | undefined;
  name: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizes = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-14 w-14 text-lg',
  xl: 'h-20 w-20 text-2xl',
};

const imgSizes = { xs: 24, sm: 32, md: 40, lg: 56, xl: 80 };

export function Avatar({ src, name, size = 'md', className }: AvatarProps) {
  const initials = name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');

  return (
    <div
      className={clsx(
        'relative flex-shrink-0 rounded-full overflow-hidden bg-brand-100 text-brand-700 font-semibold flex items-center justify-center',
        sizes[size],
        className
      )}
    >
      {src ? (
        <Image
          src={src}
          alt={name}
          width={imgSizes[size]}
          height={imgSizes[size]}
          className="object-cover w-full h-full"
        />
      ) : (
        <span>{initials || '?'}</span>
      )}
    </div>
  );
}
