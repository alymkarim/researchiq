import { useEffect, useState } from "react";
import { FileText, Sparkles } from "lucide-react";
import { getRecommendations } from "../api";

interface Recommendation {
  document_id: number;
  title: string;
  similarity: number;
}

interface RecommendationsProps {
  documentId: number;
  onSelectDocument: (id: number) => void;
}

export function Recommendations({
  documentId,
  onSelectDocument,
}: RecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchRecommendations() {
      setLoading(true);
      try {
        const result = await getRecommendations(documentId);
        setRecommendations(result.recommendations || []);
      } catch {
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, [documentId]);

  if (loading) {
    return (
      <div className="recommendations-section">
        <div className="recommendations-loading">Loading recommendations...</div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="recommendations-section">
        <div className="recommendations-empty">
          <Sparkles size={20} />
          <p>No similar papers found in your vault.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-section">
      <h3 className="recommendations-title">
        <Sparkles size={16} /> Related Papers
      </h3>
      <div className="recommendations-list">
        {recommendations.map((rec) => (
          <button
            key={rec.document_id}
            className="recommendation-card"
            onClick={() => onSelectDocument(rec.document_id)}
          >
            <div className="recommendation-icon">
              <FileText size={16} />
            </div>
            <div className="recommendation-content">
              <span className="recommendation-title">{rec.title}</span>
              <span className="recommendation-score">
                {Math.round(rec.similarity * 100)}% similar
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
