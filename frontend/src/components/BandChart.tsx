export interface BandPoint {
  x: number;
  y: number;
  low: number;
  high: number;
}

interface BandChartProps {
  data: BandPoint[];
  color?: string;
  height?: number;
}

function scale(value: number, min: number, max: number, targetMin: number, targetMax: number) {
  if (max === min) return (targetMin + targetMax) / 2;
  return targetMin + ((value - min) / (max - min)) * (targetMax - targetMin);
}

export default function BandChart({ data, color = "#8a5d2a", height = 200 }: BandChartProps) {
  if (data.length === 0) {
    return <div className="plot-placeholder">No data</div>;
  }

  const width = 420;
  const padding = 32;

  const xs = data.map((point) => point.x);
  const lows = data.map((point) => point.low);
  const highs = data.map((point) => point.high);
  const ys = data.map((point) => point.y);

  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...lows);
  const maxY = Math.max(...highs);

  const bandPath = data
    .map((point, index) => {
      const x = scale(point.x, minX, maxX, padding, width - padding);
      const y = scale(point.low, minY, maxY, height - padding, padding);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .concat(
      data
        .slice()
        .reverse()
        .map((point) => {
          const x = scale(point.x, minX, maxX, padding, width - padding);
          const y = scale(point.high, minY, maxY, height - padding, padding);
          return `L ${x} ${y}`;
        })
    )
    .join(" ");

  const linePath = data
    .map((point, index) => {
      const x = scale(point.x, minX, maxX, padding, width - padding);
      const y = scale(point.y, minY, maxY, height - padding, padding);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="chart">
      <path d={bandPath} fill={`${color}33`} stroke="none" />
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}
