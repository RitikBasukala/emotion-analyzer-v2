import { motion } from 'framer-motion';
import { History as HistoryIcon, FileText, Mic, Video, Filter } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Card, Button } from '../components/ui';
import { useAnalysisHistory } from '../hooks/useAnalysisHistory';
import { ModalityType, EMOTION_COLORS, EMOTION_ICONS, EmotionType } from '../types';
import { useState } from 'react';

const modalityIcons: Record<ModalityType, React.ElementType> = {
  text: FileText,
  audio: Mic,
  video: Video,
};

const modalityColorClasses: Record<ModalityType, string> = {
  text: 'text-primary-400 bg-primary-500/10',
  audio: 'text-secondary-400 bg-secondary-500/10',
  video: 'text-primary-300 bg-primary-500/10',
};

export function HistoryPage() {
  const [filter, setFilter] = useState<ModalityType | 'all'>('all');
  const { items, total, loading, offset, limit, setOffset, page, totalPages } = useAnalysisHistory({ modality: filter });

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neutral-700 to-neutral-800 flex items-center justify-center">
            <HistoryIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Analysis History</h1>
            <p className="text-neutral-400">View past emotion analyses</p>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-6">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-neutral-500" />
          <span className="text-sm text-neutral-400">Filter:</span>
          {(['all', 'text', 'audio', 'video'] as const).map((mod) => (
            <button
              key={mod}
              onClick={() => { setFilter(mod); setOffset(0); }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                ${filter === mod
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                  : 'bg-neutral-800 text-neutral-400 hover:text-neutral-200'
                }`}
            >
              {mod.charAt(0).toUpperCase() + mod.slice(1)}
            </button>
          ))}
        </div>
      </motion.div>

      <div className="space-y-4">
        {loading ? (
          <Card className="p-8 flex items-center justify-center">
            <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full" />
          </Card>
        ) : items.length === 0 ? (
          <Card className="p-8 text-center">
            <HistoryIcon className="w-12 h-12 text-neutral-600 mx-auto mb-3" />
            <p className="text-neutral-400">No analyses found</p>
            <p className="text-sm text-neutral-500 mt-1">
              Start analyzing emotions to see your history here
            </p>
          </Card>
        ) : (
          items.map((item, i) => {
            const Icon = modalityIcons[item.modality];
            const colorClasses = modalityColorClasses[item.modality];

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Card className="p-4">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl ${colorClasses} flex items-center justify-center`}>
                      <Icon className="w-5 h-5" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-neutral-400 capitalize">{item.modality}</span>
                        <span className="text-neutral-600">•</span>
                        <span className="text-xs text-neutral-500">
                          {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                        </span>
                      </div>
                      {item.input_preview && (
                        <p className="text-sm text-neutral-300 truncate">{item.input_preview}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
                        style={{ backgroundColor: `${EMOTION_COLORS[item.final_emotion as EmotionType]}20` }}
                      >
                        {EMOTION_ICONS[item.final_emotion as EmotionType]}
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-white">{item.final_emotion}</p>
                        <p className="text-xs text-neutral-500">{(item.confidence * 100).toFixed(1)}% conf</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })
        )}
      </div>

      {total > limit && (
        <div className="flex justify-center gap-2 mt-6">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setOffset(Math.max(0, offset - limit))}
          >
            Previous
          </Button>
          <span className="px-4 py-2 text-neutral-400">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setOffset(offset + limit)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
