import { FormEvent, useState } from "react";
import {
  Bot,
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

export function ResearchConsole({
  selectedCount,
  searching,
  results,
  onSearch,
}: ResearchConsoleProps) {
  const [query, setQuery] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!query.trim() || searching) return;
    await onSearch(query.trim());
  }

  return (
    <section className="lab-panel console-panel" id="console">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Search-o-matic</span>
          <h2>Research Console</h2>
        </div>
        <span className="panel-number">03</span>
      </div>

      <div className="console-screen">
        <div className="console-status">
          <span>
            <i />
            {selectedCount
              ? `${selectedCount} paper${selectedCount === 1 ? "" : "s"} connected`
              : "All papers connected"}
          </span>
          <span>READY FOR INTERROGATION</span>
        </div>

        <div className="console-welcome">
          <span className="bot-orb">
            <Bot size={28} />
          </span>
          <div>
            <strong>Ask the evidence, not the vibes.</strong>
            <p>
              Search methods, datasets, findings, limitations or anything else
              hidden inside the selected papers.
            </p>
          </div>
        </div>

        <form className="search-form" onSubmit={submit}>
          <Search size={19} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="e.g. What machine-learning methods were used?"
            aria-label="Search research papers"
          />
          <button disabled={!query.trim() || searching}>
            {searching ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <Sparkles size={18} />
            )}
            Run query
          </button>
        </form>
      </div>

      <div className="results-area">
        <div className="results-heading">
          <span>Laboratory findings</span>
          <span>{results.length} matches</span>
        </div>

        {results.length === 0 ? (
          <div className="empty-results">
            <FileSearch size={30} />
            <strong>No experiment has been run yet.</strong>
            <span>Your future citations are waiting patiently.</span>
          </div>
        ) : (
          <div className="search-results">
            {results.map((result, index) => (
              <article className="result-card" key={`${index}-${result.text}`}>
                <div className="result-score">
                  <strong>
                    {typeof result.score === "number"
                      ? `${Math.round(result.score * 100)}%`
                      : `#${index + 1}`}
                  </strong>
                  <span>match</span>
                </div>

                <div>
                  <span className="result-source">
                    {result.document_title ||
                      result.filename ||
                      `Document ${result.document_id || ""}`}
                    {result.page ? ` · Page ${result.page}` : ""}
                  </span>
                  <p>
                    {result.text ??
                      result.snippet ??
                      "Relevant passage returned without preview text."}
                  </p>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
