import type { Analysis, DocumentItem } from "../types";

interface AnalysisPanelProps {
  document?: DocumentItem;
  analysis?: Analysis | null;
}

interface FieldProps {
  label: string;
  value?: string | null;
  bullets?: boolean;
}

function AnalysisField({ label, value, bullets = false }: FieldProps) {
  const content = value?.trim();

  if (!content) {
    return null;
  }

  if (bullets) {
    const items = content
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean);

    return (
      <section className="analysis-field">
        <h3>{label}</h3>
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    );
  }

  return (
    <section className="analysis-field">
      <h3>{label}</h3>
      <p>{content}</p>
    </section>
  );
}

export function AnalysisPanel({
  document,
  analysis,
}: AnalysisPanelProps) {
  if (!document) {
    return (
      <div className="empty-tool-state">
        <span className="eyebrow">Paper analysis</span>
        <h2>No paper is open yet</h2>
        <p>
          Choose Analyse beside a paper in the library. Its structured
          findings will appear here.
        </p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="empty-tool-state">
        <span className="eyebrow">Paper analysis</span>
        <h2>{document.title || document.filename}</h2>
        <p>
          This paper has not been analysed yet. Use the Analyse button in
          the paper library.
        </p>
      </div>
    );
  }

  const keywords = analysis.keywords
    ?.split(",")
    .map((keyword) => keyword.trim())
    .filter(Boolean);

  return (
    <article className="analysis-view">
      <header className="analysis-view-header">
        <div>
          <span className="eyebrow">Structured paper analysis</span>
          <h2>{document.title || document.filename}</h2>
        </div>

        <span className={`analysis-mode ${analysis.analysis_mode || "unknown"}`}>
          {analysis.analysis_mode === "llm"
            ? "LLM analysis"
            : "Local fallback"}
        </span>
      </header>

      <AnalysisField label="Executive summary" value={analysis.summary} />

      <div className="analysis-two-column">
        <AnalysisField label="Objective" value={analysis.objective} />
        <AnalysisField label="Methodology" value={analysis.methodology} />
        <AnalysisField label="Dataset or sample" value={analysis.dataset} />
        <AnalysisField label="Main findings" value={analysis.findings} />
      </div>

      <div className="analysis-two-column">
        <AnalysisField
          label="Strengths"
          value={analysis.strengths}
          bullets
        />
        <AnalysisField
          label="Limitations"
          value={analysis.limitations}
          bullets
        />
      </div>

      {keywords && keywords.length > 0 && (
        <section className="analysis-field">
          <h3>Keywords</h3>
          <div className="keyword-list">
            {keywords.map((keyword) => (
              <span key={keyword}>{keyword}</span>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
