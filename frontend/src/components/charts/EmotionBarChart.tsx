import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { EMOTION_COLORS, EmotionType } from '../../types';

interface EmotionBarChartProps {
  probabilities: Record<string, number>;
  title?: string;
  horizontal?: boolean;
  maxItems?: number;
}

export function EmotionBarChart({ probabilities, title, horizontal = false, maxItems }: EmotionBarChartProps) {
  const data = Object.entries(probabilities)
    .map(([emotion, value]) => ({
      name: emotion,
      value: value * 100,
      color: EMOTION_COLORS[emotion as EmotionType] || '#a1a1aa',
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, maxItems ?? undefined);

  if (horizontal) {
    return (
      <div className="w-full">
        {title && (
          <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
        )}
        <div className="space-y-3">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-3">
              <div className="w-20 text-sm text-neutral-400">{item.name}</div>
              <div className="flex-1 h-6 bg-neutral-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.value}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                />
              </div>
              <div className="w-16 text-sm text-right text-neutral-300">
                {item.value.toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      )}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: '#a1a1aa' }} />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#a1a1aa' }}
              width={80}
            />
            <Tooltip
              contentStyle={{
                background: '#18181b',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probability']}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
