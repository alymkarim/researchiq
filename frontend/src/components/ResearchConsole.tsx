import { FormEvent, useEffect, useRef, useState } from "react";
import {
  FileSearch,
  LoaderCircle,
  Search,
  Sparkles,
} from "lucide-react";
import type { SearchResult } from "../types";

interface ResearchConsoleProps {
  selectedCount: number;
  searching: boolean;
  results: SearchResult[];
  onSearch: (query: string) => Promise<void>;
}

const SUGGESTED_QUERIES = [
  "What machine-learning methods were used?",
  "What are the main limitations?",
  "How large was the dataset?",
  "What future work was proposed?",
];

export function ResearchConsole({
  selectedCount,
  searching,
  results,
  onSearch,
}: ResearchConsoleProps) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (
        event.key === "/" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey
      ) {
        const target = event.target as HTMLElement;
        if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;
        event.preventDefault();
        inputRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!query.trim() || searching) return;
    await onSearch(query.trim());
  }

  function handleSuggestionClick(suggestion: string) {
    setQuery(suggestion);
    inputRef.current?.focus();
  }

  return (
    <section className="research-console" id="console">
      <div className="console-header">
        <div>
          <span className="console-kicker">Search</span>
          <h2>Research Console</h2>
        </div>
        <span className="console-count">
          {selectedCount
            ? `${selectedCount} paper${selectedCount === 1 ? "" : "s"} selected`
            : "All papers"}
        </span>
      </div>

      <form className="console-search" onSubmit={submit}>
        <div className="console-input-wrapper">
          <Search size={18} className="console-input-icon" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search across your papers..."
            aria-label="Search research papers"
            className="console-input"
          />
          <kbd className="console-kbd">/</kbd>
        </div>
        <button
          className="console-submit"
          disabled={!query.trim() || searching}
        >
          {searching ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Sparkles size={16} />
          )}
          Search
        </button>
      </form>

      <div className="console-results">
        {results.length === 0 ? (
          <div className="console-empty">
            <div className="console-empty-icon">
              <FileSearch size={32} />
            </div>
            <h3>No results yet</h3>
            <p>
              Search methods, datasets, findings, or anything inside your papers.
            </p>
            <div className="console-suggestions">
              {SUGGESTED_QUERIES.map((suggestion) => (
                <button
                  key={suggestion}
                  className="console-suggestion"
                  onClick={() => handleSuggestionClick(suggestion)}
                  type="button"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            <div className="console-results-header">
              <span className="console-results-label">Results</span>
              <span className="console-results-count">
                {results.length} match{results.length !== 1 ? "es" : ""}
              </span>
            </div>
            <div className="console-results-list">
              {results.map((result, index) => (
                <article
                  className="console-result-card"
                  key={`${index}-${result.text}`}
                >
                  <div className="console-result-score">
                    <span className="score-value">
                      {typeof result.score === "number"
                        ? `${Math.round(result.score * 100)}%`
                        : `#${index + 1}`}
                    </span>
                    <span className="score-label">match</span>
                  </div>
                  <div className="console-result-body">
                    <span className="console-result-source">
                      {result.document_title ||
                        result.filename ||
                        `Document ${result.document_id || ""}`}
                      {result.page ? ` · Page ${result.page}` : ""}
                    </span>
                    <p className="console-result-text">
                      {result.text ??
                        result.snippet ??
                        "Relevant passage returned without preview text."}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
