import {
  GitCompareArrows,
  LoaderCircle,
  Search,
  Tag,
  X,
} from "lucide-react";
import type { ComparisonResult, DocumentItem } from "../types";

interface ComparisonPanelProps {
  documents: DocumentItem[];
  selectedIds: number[];
  comparing: boolean;
  result: ComparisonResult | null;
  onCompare: () => Promise<void>;
}

function renderValue(value: unknown): React.ReactNode {
  if (Array.isArray(value)) {
    return (
      <ul className="comparison-list">
        {value.map((item, index) => {
          if (typeof item === "string" || typeof item === "number") {
            return (
              <li key={`${index}-${item}`} className="comparison-list-item">
                {item}
              </li>
            );
          }
          if (item && typeof item === "object") {
            const objectItem = item as Record<string, unknown>;
            const label =
              objectItem.title ??
              objectItem.filename ??
              objectItem.name ??
              objectItem.paper_title ??
              `Paper ${index + 1}`;
            return (
              <li key={`${index}-${String(label)}`} className="comparison-list-item">
                {String(label)}
              </li>
            );
          }
          return (
            <li key={index} className="comparison-list-item">
              Paper {index + 1}
            </li>
          );
        })}
      </ul>
    );
  }

  if (value && typeof value === "object") {
    return (
      <div className="comparison-object">
        {Object.entries(value as Record<string, unknown>).map(
          ([key, nestedValue]) => (
            <div key={key} className="comparison-object-entry">
              <span className="comparison-object-key">
                {key.replace(/_/g, " ")}
              </span>
              <span className="comparison-object-value">
                {String(nestedValue)}
              </span>
            </div>
          ),
        )}
      </div>
    );
  }

  if (value == null || value === "") return null;

  return <p className="comparison-text">{String(value)}</p>;
}

export function ComparisonPanel({
  documents,
  selectedIds,
  comparing,
  result,
  onCompare,
}: ComparisonPanelProps) {
  const selected = documents.filter((document) =>
    selectedIds.includes(document.id),
  );

  const internalKeys = new Set(["keywords", "documents", "papers", "shared_keywords", "similarities"]);

  const visibleEntries = result
    ? Object.entries(result).filter(
        ([key, value]) =>
          !internalKeys.has(key) &&
          value != null &&
          value !== "" &&
          value !== false,
      )
    : [];

  const keywords = (() => {
    const source = result?.keywords ?? result?.shared_keywords;
    if (!source) return [];
    if (typeof source === "string")
      return source.split(",").map((k) => k.trim()).filter(Boolean);
    if (Array.isArray(source)) return source.map(String);
    return [];
  })();

  return (
    <section className="comparison-panel" id="comparison">
      <div className="comparison-header">
        <div>
          <span className="comparison-kicker">Comparison</span>
          <h2>Cross-Paper Analysis</h2>
        </div>
      </div>

      <div className="comparison-selected-papers">
        {selected.length === 0 ? (
          <span className="comparison-empty-hint">
            Select at least two papers to compare
          </span>
        ) : (
          selected.map((document) => (
            <span key={document.id} className="comparison-chip">
              <span className="comparison-chip-text">
                {document.title || document.filename}
              </span>
              <span className="comparison-chip-id">#{document.id}</span>
            </span>
          ))
        )}
      </div>

      <button
        className="comparison-action"
        onClick={onCompare}
        disabled={selected.length < 2 || comparing}
      >
        {comparing ? (
          <>
            <LoaderCircle className="spin" size={16} />
            Analyzing...
          </>
        ) : (
          <>
            <GitCompareArrows size={16} />
            Compare {selected.length} papers
          </>
        )}
      </button>

      <div className="comparison-output">
        {!result ? (
          <div className="comparison-empty">
            <Search size={28} />
            <h3>No comparison yet</h3>
            <p>Select two or more papers and run a comparison.</p>
          </div>
        ) : (
          <div className="comparison-content">
            {keywords.length > 0 && (
              <div className="comparison-keywords">
                <div className="comparison-section-label">
                  <Tag size={14} />
                  Shared Keywords
                </div>
                <div className="comparison-keyword-list">
                  {keywords.map((keyword) => (
                    <span key={keyword} className="comparison-keyword-tag">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {visibleEntries.map(([key, value]) => (
                <div key={key} className="comparison-field">
                  <h4 className="comparison-field-title">
                    {key.replace(/_/g, " ")}
                  </h4>
                  <div className="comparison-field-body">
                    {renderValue(value)}
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </section>
  );
}
