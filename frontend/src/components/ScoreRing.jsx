// Animated circular progress meter for a 0–100 score, colour-coded by band.
import { useEffect, useState } from "react";
import { animate, motion } from "framer-motion";
import { scoreBand } from "@/lib/utils";

export default function ScoreRing({ score = 0, size = 160, stroke = 12, label }) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const band = scoreBand(score);
  const [display, setDisplay] = useState(0);

  // Count the number up alongside the ring animation
  useEffect(() => {
    const controls = animate(0, score, { duration: 1.2, ease: "easeOut", onUpdate: (v) => setDisplay(Math.round(v)) });
    return () => controls.stop();
  }, [score]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90" role="img" aria-label={`${label || "Score"}: ${score} out of 100`}>
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth={stroke} className="stroke-muted" />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={band.color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference * (1 - score / 100) }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold tabular-nums" style={{ color: band.color }}>{display}</span>
          <span className="text-xs text-muted-foreground">out of 100</span>
        </div>
      </div>
      {label && <p className="mt-3 text-sm font-semibold">{label}</p>}
      <p className={`text-xs font-medium ${band.text}`}>{band.label}</p>
    </div>
  );
}
