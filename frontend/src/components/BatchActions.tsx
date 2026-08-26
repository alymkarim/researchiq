import { useState } from "react";
import { Layers, LoaderCircle, Play } from "lucide-react";
import { batchAnalyse } from "../api";

interface BatchActionsProps {
  selectedIds: number[];
  onComplete?: () => void;
}

export function BatchActions({ selectedIds, onComplete }: BatchActionsProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    total: number;
    successful: number;
    failed: number;
  } | null>(null);

  async function handleBatchAnalyse() {
    if (selectedIds.length === 0) return;

    setLoading(true);
    setResult(null);

    try {
      const data = await batchAnalyse(selectedIds);
      setResult({
        total: data.total,
        successful: data.successful,
        failed: data.failed,
      });
      onComplete?.();
    } catch {
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  if (selectedIds.length === 0) return null;

  return (
    <div className="batch-actions">
      <div className="batch-info">
        <Layers size={16} />
        <span>{selectedIds.length} papers selected</span>
      </div>

      <button
        className="batch-btn"
        onClick={handleBatchAnalyse}
        disabled={loading}
      >
        {loading ? (
          <>
            <LoaderCircle className="spin" size={16} />
            Analysing {selectedIds.length} papers...
          </>
        ) : (
          <>
            <Play size={16} />
            Batch Analyse
          </>
        )}
      </button>

      {result && (
        <div className="batch-result">
          <span className="batch-success">{result.successful} succeeded</span>
          {result.failed > 0 && (
            <span className="batch-failed">{result.failed} failed</span>
          )}
        </div>
      )}
    </div>
  );
}
