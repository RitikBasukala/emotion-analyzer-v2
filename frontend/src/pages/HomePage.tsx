import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FileText, Mic, Video, ArrowRight, Radar, Layers, Waves } from 'lucide-react';
import { EMOTIONS, EMOTION_COLORS, EMOTION_ICONS, EmotionType } from '../types';

const modalities = [
  {
    title: 'Text',
    description: 'Detect emotion from written language with a transformer-based classifier.',
    icon: FileText,
    href: '/text',
    gradient: 'from-primary-500 to-primary-600',
  },
  {
    title: 'Audio',
    description: 'Transcribe speech and analyze both linguistic content and vocal tone.',
    icon: Mic,
    href: '/audio',
    gradient: 'from-secondary-500 to-secondary-600',
  },
  {
    title: 'Video',
    description: 'Combine facial expression, voice, and speech content into one prediction.',
    icon: Video,
    href: '/video',
    gradient: 'from-primary-500 to-secondary-500',
  },
];

export function HomePage() {
  return (
    <div className="min-h-screen bg-neutral-950 bg-grid-pattern">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-20"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl
              bg-gradient-to-br from-primary-500 to-secondary-500 mb-6"
          >
            <Waves className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-5xl font-bold text-white mb-4">
            <span className="bg-gradient-to-r from-primary-400 via-primary-300 to-secondary-400 bg-clip-text text-transparent">
              Multimodal
            </span>{' '}
            Emotion Recognition
          </h1>
          <p className="text-lg text-neutral-400 max-w-2xl mx-auto mb-8">
            Analyze emotion from text, audio, and video independently, then watch
            an explainable fusion cockpit blend the signals in real time.
            No sign-up required.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-600
                hover:bg-primary-700 text-white font-medium transition-colors"
            >
              <Radar size={18} />
              Open Fusion Cockpit
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/text"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border-2
                border-neutral-700 hover:bg-neutral-800 text-neutral-200 font-medium transition-colors"
            >
              Try Text Analysis
            </Link>
          </div>
        </motion.div>

        {/* Modality Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          {modalities.map((modality, i) => (
            <motion.div
              key={modality.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.1 }}
            >
              <Link to={modality.href}>
                <div className="p-6 h-full rounded-2xl border border-neutral-800 bg-neutral-900/80
                  hover:border-neutral-700 transition-colors">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${modality.gradient}
                    flex items-center justify-center mb-4`}>
                    <modality.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{modality.title}</h3>
                  <p className="text-neutral-400 text-sm mb-4">{modality.description}</p>
                  <div className="flex items-center gap-1 text-sm text-primary-400">
                    Analyze now <ArrowRight size={14} />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Emotion Palette */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-8 mb-20"
        >
          <div className="flex items-center gap-2 mb-6">
            <Layers className="text-primary-400" size={20} />
            <h2 className="text-xl font-semibold text-white">Seven Standard Emotion Labels</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {EMOTIONS.map((emotion: EmotionType) => (
              <div
                key={emotion}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm border"
                style={{
                  backgroundColor: `${EMOTION_COLORS[emotion]}15`,
                  borderColor: `${EMOTION_COLORS[emotion]}40`,
                }}
              >
                <span>{EMOTION_ICONS[emotion]}</span>
                <span style={{ color: EMOTION_COLORS[emotion] }}>{emotion}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* How it works */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {[
            { step: 1, title: 'Analyze each modality', text: 'Run text, audio, or video through dedicated models.' },
            { step: 2, title: 'Three fusion tiers', text: 'Early (raw features), mid (gated projection), and late (soft voting) tiers all vote.' },
            { step: 3, title: 'Explainable final decision', text: 'The cockpit shows exactly how each modality contributed and whether it agreed.' },
          ].map((item) => (
            <div key={item.step}>
              <div className="w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center
                text-primary-400 font-bold mb-3">{item.step}</div>
              <h3 className="text-white font-medium mb-2">{item.title}</h3>
              <p className="text-neutral-400 text-sm">{item.text}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
