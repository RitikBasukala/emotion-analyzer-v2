import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={hover ? { y: -4, transition: { duration: 0.2 } } : undefined}
      className={`
        bg-neutral-900/80 backdrop-blur-xl
        border border-neutral-800
        rounded-2xl shadow-xl
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}
