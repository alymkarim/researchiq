import { useState } from "react";
import {
  BookOpen,
  ChevronDown,
  ChevronUp,
  FlaskConical,
  ListChecks,
  Search,
  Sparkles,
  Target,
  TestTube,
} from "lucide-react";
import type { Analysis, DocumentItem } from "../types";
import { CitationExport } from "./CitationExport";

interface AnalysisPanelProps {
  document?: DocumentItem | null;
  analysis?: Analysis | null;
}

function CollapsibleSection({
  title,
  icon,
  children,
  defaultOpen = true,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`analysis-section ${open ? "open" : ""}`}>
      <button
        className="analysis-section-header"
        onClick={() => setOpen(!open)}
      >
        <div className="analysis-section-title">
          {icon}
          <span>{title}</span>
        </div>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {open && <div className="analysis-section-body">{children}</div>}
    </div>
  );
}

export function AnalysisPanel({ document, analysis }: AnalysisPanelProps) {
  if (!document) {
    return (
      <div className="analysis-panel empty">
        <div className="empty-state">
          <div className="empty-state-icon">
            <FlaskConical size={40} />
          </div>
          <h3>No paper selected</h3>
          <p>Select a paper from the vault and click Analyse to see results.</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="analysis-panel empty">
        <div className="empty-state">
          <div className="empty-state-icon">
            <BookOpen size={40} />
          </div>
          <h3>{document.title || document.filename}</h3>
          <p>This paper has not been analysed yet. Click Analyse to begin.</p>
        </div>
      </div>
    );
  }

  const keywords = analysis.keywords
    ?.split(",")
    .map((kw) => kw.trim())
    .filter(Boolean);

  const modeLabel =
    analysis.analysis_mode === "llm" ? "LLM Analysis" : "Heuristic Fallback";
  const modeClass =
    analysis.analysis_mode === "llm" ? "mode-llm" : "mode-heuristic";

  return (
    <article className="analysis-panel">
      <header className="analysis-header">
        <span className="analysis-label">Structured Analysis</span>
        <h2 className="analysis-title">
          {document.title || document.filename}
        </h2>
        <span className={`analysis-mode-badge ${modeClass}`}>{modeLabel}</span>
      </header>

      {analysis.summary && (
        <div className="analysis-summary-card">
          <h3>
            <Sparkles size={16} /> Executive Summary
          </h3>
          <p>{analysis.summary}</p>
        </div>
      )}

      <div className="analysis-sections">
        <CollapsibleSection
          title="Objective"
          icon={<Target size={16} />}
        >
          <p>{analysis.objective}</p>
        </CollapsibleSection>

        <CollapsibleSection
          title="Methodology"
          icon={<FlaskConical size={16} />}
        >
          <p>{analysis.methodology}</p>
        </CollapsibleSection>

        <CollapsibleSection
          title="Dataset or Sample"
          icon={<TestTube size={16} />}
        >
          <p>{analysis.dataset}</p>
        </CollapsibleSection>

        <CollapsibleSection
          title="Main Findings"
          icon={<Search size={16} />}
        >
          <p>{analysis.findings}</p>
        </CollapsibleSection>

        <CollapsibleSection
          title="Strengths"
          icon={<ListChecks size={16} />}
        >
          <ul className="analysis-list">
            {analysis.strengths
              ?.split("\n")
              .filter(Boolean)
              .map((item) => (
                <li key={item}>{item}</li>
              ))}
          </ul>
        </CollapsibleSection>

        <CollapsibleSection
          title="Limitations"
          icon={<ListChecks size={16} />}
        >
          <ul className="analysis-list">
            {analysis.limitations
              ?.split("\n")
              .filter(Boolean)
              .map((item) => (
                <li key={item}>{item}</li>
              ))}
          </ul>
        </CollapsibleSection>
      </div>

      {keywords && keywords.length > 0 && (
        <div className="analysis-keywords">
          <h3>Keywords</h3>
          <div className="keyword-chips">
            {keywords.map((kw) => (
              <span className="keyword-chip" key={kw}>
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      <CitationExport documentId={document.id} />
    </article>
  );
}
