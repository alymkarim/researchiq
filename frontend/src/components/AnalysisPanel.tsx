import {
  BrainCircuit,
  CheckCircle2,
  Lightbulb,
  Microscope,
  TriangleAlert,
} from "lucide-react";
import type { Analysis, DocumentItem } from "../types";

interface AnalysisPanelProps {
  document?: DocumentItem;
  analysis?: Analysis | null;
}

function toList(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String);
  if (typeof value === "string") {
    return value
      .split(/\n|,|;/)
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return [];
}

export function AnalysisPanel({
  document,
  analysis,
}: AnalysisPanelProps) {
  const keywords = toList(analysis?.keywords);
  const strengths = toList(analysis?.strengths);
  const limitations = toList(analysis?.limitations);

  return (
    <section className="lab-panel analysis-panel">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Analysis chamber</span>
          <h2>Paper Diagnostics</h2>
        </div>
        <span className="panel-number">04</span>
      </div>

      {!document || !analysis ? (
        <div className="empty-state analysis-empty">
          <Microscope size={42} />
          <strong>No specimen under the microscope.</strong>
          <span>
            Press Analyse on a paper to produce an unnecessarily official lab
            report.
          </span>
        </div>
      ) : (
        <div className="analysis-content">
          <div className="analysis-title">
            <span>
              <BrainCircuit size={18} />
              ACTIVE SPECIMEN
            </span>
            <h3>{document.title || document.filename}</h3>
          </div>

          <article className="analysis-block summary-block">
            <span className="analysis-icon">
              <Lightbulb size={20} />
            </span>
            <div>
              <h4>Executive summary</h4>
              <p>
                {analysis.summary ||
                  analysis.findings ||
                  "The analysis completed, but the backend did not return a summary field."}
              </p>
            </div>
          </article>

          {analysis.methodology && (
            <article className="analysis-block">
              <span className="analysis-icon">
                <Microscope size={20} />
              </span>
              <div>
                <h4>Methodology</h4>
                <p>{analysis.methodology}</p>
              </div>
            </article>
          )}

          {keywords.length > 0 && (
            <div className="keyword-cloud">
              {keywords.map((keyword) => (
                <span key={keyword}>{keyword}</span>
              ))}
            </div>
          )}

          <div className="analysis-columns">
            <article>
              <h4>
                <CheckCircle2 size={18} />
                Strengths
              </h4>
              {strengths.length ? (
                <ul>
                  {strengths.map((strength) => (
                    <li key={strength}>{strength}</li>
                  ))}
                </ul>
              ) : (
                <p>No structured strengths returned.</p>
              )}
            </article>

            <article>
              <h4>
                <TriangleAlert size={18} />
                Limitations
              </h4>
              {limitations.length ? (
                <ul>
                  {limitations.map((limitation) => (
                    <li key={limitation}>{limitation}</li>
                  ))}
                </ul>
              ) : (
                <p>No structured limitations returned.</p>
              )}
            </article>
          </div>
        </div>
      )}
    </section>
  );
}
