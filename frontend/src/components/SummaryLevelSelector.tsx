import { useState } from "react";
import { LoaderCircle, Zap, BookOpen, Microscope } from "lucide-react";
import { getSummary } from "../api";

interface SummaryLevelSelectorProps {
  documentId: number;
  onSummaryLoaded?: (analysis: Record<string, unknown>) => void;
}

type SummaryLevel = "quick" | "standard" | "deep";

const LEVELS = [
  { value: "quick" as const, label: "Quick", icon: Zap, description: "2-3 sentence summary" },
  { value: "standard" as const, label: "Standard", icon: BookOpen, description: "Structured analysis" },
  { value: "deep" as const, label: "Deep", icon: Microscope, description: "In-depth review" },
];

export function SummaryLevelSelector({ documentId, onSummaryLoaded }: SummaryLevelSelectorProps) {
  const [level, setLevel] = useState<SummaryLevel>("standard");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyse() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await getSummary(documentId, level);
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data.analysis);
        onSummaryLoaded?.(data.analysis || {});
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="summary-level-selector">
      <div className="summary-level-options">
        {LEVELS.map((opt) => (
          <button
            key={opt.value}
            className={`summary-level-btn ${level === opt.value ? "active" : ""}`}
            onClick={() => setLevel(opt.value)}
          >
            <opt.icon size={16} />
            <span className="summary-level-label">{opt.label}</span>
            <span className="summary-level-desc">{opt.description}</span>
          </button>
        ))}
      </div>

      <button
        className="summary-analyse-btn"
        onClick={handleAnalyse}
        disabled={loading}
      >
        {loading ? (
          <>
            <LoaderCircle className="spin" size={16} />
            Analysing...
          </>
        ) : (
          <>
            <Zap size={16} />
            Analyse at {level} level
          </>
        )}
      </button>

      {error && <div className="summary-error">{error}</div>}

      {result && (
        <div className="summary-result">
          {Object.entries(result).map(([key, value]) => {
            if (!value || key === "analysis_mode") return null;
            return (
              <div key={key} className="summary-field">
                <h4>{key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</h4>
                <p>{String(value)}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
