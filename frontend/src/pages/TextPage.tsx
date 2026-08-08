import { motion } from 'framer-motion';
import { FileText } from 'lucide-react';
import { useTextAnalysis, TextInputPanel, TextResultsPanel, TextEmptyState } from '../features/text';

export function TextPage() {
  const { text, setText, loading, result, error, analyze } = useTextAnalysis();

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Text Emotion Analysis</h1>
            <p className="text-neutral-400">Analyze emotions in written text</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
          <TextInputPanel text={text} onTextChange={setText} onSubmit={analyze} loading={loading} error={error} />
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
          {result ? <TextResultsPanel result={result} /> : <TextEmptyState />}
        </motion.div>
      </div>
    </div>
  );
}
