import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { EMOTIONS } from '../../types';

interface EmotionRadarChartProps {
  probabilities: Record<string, number>;
  title?: string;
  color?: string;
  maxItems?: number;
}

export function EmotionRadarChart({ probabilities, title, color = '#8b5cf6', maxItems }: EmotionRadarChartProps) {
  const data = (maxItems
    ? Object.entries(probabilities)
      .map(([emotion, value]) => ({
        emotion,
        value: value * 100,
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, maxItems)
    : EMOTIONS.map((emotion) => ({
      emotion,
      value: (probabilities[emotion] ?? 0) * 100,
    })));

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="#3f3f46" />
            <PolarAngleAxis dataKey="emotion" tick={{ fill: '#a1a1aa', fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#71717a', fontSize: 10 }} />
            <Radar
              dataKey="value"
              stroke={color}
              fill={color}
              fillOpacity={0.35}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                background: '#18181b',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probability']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
