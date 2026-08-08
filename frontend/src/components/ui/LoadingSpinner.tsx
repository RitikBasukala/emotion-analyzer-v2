import { motion } from 'framer-motion';

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full"
      />
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center gap-4"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-3 border-primary-500 border-t-transparent rounded-full"
        />
        <p className="text-neutral-400">Loading...</p>
      </motion.div>
    </div>
  );
}
