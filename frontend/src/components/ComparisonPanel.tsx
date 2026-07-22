import {
  FlaskRound,
  GitCompareArrows,
  LoaderCircle,
  Scale,
  Sparkles,
} from "lucide-react";
import type { ComparisonResult, DocumentItem } from "../types";

interface ComparisonPanelProps {
  documents: DocumentItem[];
  selectedIds: number[];
  comparing: boolean;
  result: ComparisonResult | null;
  onCompare: () => Promise<void>;
}

function renderValue(value: unknown) {
  if (Array.isArray(value)) {
    return (
      <ul>
        {value.map((item, index) => {
          if (typeof item === "string" || typeof item === "number") {
            return <li key={`${index}-${item}`}>{item}</li>;
          }

          if (item && typeof item === "object") {
            const objectItem = item as Record<string, unknown>;

            const label =
              objectItem.title ??
              objectItem.filename ??
              objectItem.name ??
              objectItem.paper_title ??
              `Paper ${index + 1}`;

            return <li key={`${index}-${String(label)}`}>{String(label)}</li>;
          }

          return <li key={index}>Paper {index + 1}</li>;
        })}
      </ul>
    );
  }

  if (value && typeof value === "object") {
    return (
      <div>
        {Object.entries(value as Record<string, unknown>).map(
          ([key, nestedValue]) => (
            <div key={key}>
              <strong>{key.replace(/_/g, " ")}:</strong>{" "}
              {String(nestedValue)}
            </div>
          ),
        )}
      </div>
    );
  }

  if (value == null || value === "") return null;

  return <p>{String(value)}</p>;
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

  const visibleEntries = result
    ? Object.entries(result).filter(
        ([, value]) => value != null && value !== "" && value !== false,
      )
    : [];

  return (
    <section className="lab-panel comparison-panel" id="comparison">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Comparison reactor</span>
          <h2>Cross-Paper Experiment</h2>
        </div>
        <span className="panel-number">05</span>
      </div>

      <div className="reactor-layout">
        <div className="reactor-selection">
          <div className="reactor-core">
            <FlaskRound size={46} />
            <span>{selected.length}/2+</span>
          </div>

          <div>
            <h3>Select at least two specimens</h3>
            <p>
              Use the round selectors in the Paper Vault, then activate the
              comparison reactor.
            </p>
          </div>

          <div className="selected-specimens">
            {selected.length === 0 ? (
              <span className="specimen-placeholder">
                Awaiting specimens...
              </span>
            ) : (
              selected.map((document) => (
                <span key={document.id}>
                  #{document.id} {document.title || document.filename}
                </span>
              ))
            )}
          </div>

          <button
            className="primary-button full-width"
            onClick={onCompare}
            disabled={selected.length < 2 || comparing}
          >
            {comparing ? (
              <>
                <LoaderCircle className="spin" size={19} />
                Reactor warming up...
              </>
            ) : (
              <>
                <GitCompareArrows size={19} />
                Compare specimens
              </>
            )}
          </button>
        </div>

        <div className="comparison-output">
          {!result ? (
            <div className="reactor-empty">
              <Scale size={37} />
              <strong>No comparison generated.</strong>
              <span>
                Pick two or more papers. Scientific drama will appear here.
              </span>
            </div>
          ) : (
            <>
              <div className="comparison-result-title">
                <Sparkles size={19} />
                Reactor output
              </div>

              {visibleEntries.map(([key, value]) => (
                <article key={key}>
                  <h4>{key.replace(/_/g, " ")}</h4>
                  {renderValue(value)}
                </article>
              ))}
            </>
          )}
        </div>
      </div>
    </section>
  );
}