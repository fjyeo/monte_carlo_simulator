export interface LinePoint {
  x: number;
  y: number;
}

interface LineChartProps {
  data: LinePoint[];
  color?: string;
  height?: number;
}

function scale(value: number, min: number, max: number, targetMin: number, targetMax: number) {
  if (max === min) return (targetMin + targetMax) / 2;
  return targetMin + ((value - min) / (max - min)) * (targetMax - targetMin);
}

export default function LineChart({ data, color = "#1b1b1f", height = 200 }: LineChartProps) {
  if (data.length === 0) {
    return <div className="plot-placeholder">No data</div>;
  }

  const width = 420;
  const padding = 32;

  const xs = data.map((point) => point.x);
  const ys = data.map((point) => point.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const path = data
    .map((point, index) => {
      const x = scale(point.x, minX, maxX, padding, width - padding);
      const y = scale(point.y, minY, maxY, height - padding, padding);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="chart">
      <path d={path} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}
