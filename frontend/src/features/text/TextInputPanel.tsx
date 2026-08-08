import { motion } from 'framer-motion';
import { FileText, Sparkles } from 'lucide-react';
import { Button, Card } from '../../components/ui';

interface TextInputPanelProps {
  text: string;
  onTextChange: (text: string) => void;
  onSubmit: () => void;
  loading: boolean;
  error: string | null;
}

export function TextInputPanel({ text, onTextChange, onSubmit, loading, error }: TextInputPanelProps) {
  return (
    <Card className="p-6">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <label className="block text-sm font-medium text-neutral-300 mb-2">
          Enter text to analyze
        </label>
        <textarea
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder="Type or paste your text here..."
          className="w-full h-48 bg-neutral-900/50 border border-neutral-700 rounded-lg p-4
            text-white placeholder-neutral-500 resize-none
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <div className="flex items-center justify-between mt-4">
          <span className="text-sm text-neutral-500">{text.length} characters</span>
          <Button type="submit" disabled={!text.trim()} loading={loading} icon={<Sparkles size={18} />}>
            Analyze Emotion
          </Button>
        </div>
      </form>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 rounded-lg bg-secondary-500/10 border border-secondary-500/30
            text-secondary-400 text-sm"
        >
          {error}
        </motion.div>
      )}
    </Card>
  );
}

export function TextEmptyState() {
  return (
    <Card className="p-6 h-full flex flex-col items-center justify-center text-center min-h-[300px]">
      <div className="w-16 h-16 rounded-2xl bg-neutral-800 flex items-center justify-center mb-4">
        <FileText className="w-8 h-8 text-neutral-600" />
      </div>
      <p className="text-neutral-500">
        Enter text and click analyze to see emotion predictions
      </p>
    </Card>
  );
}
