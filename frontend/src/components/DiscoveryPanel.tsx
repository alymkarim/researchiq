import { FormEvent, useState } from "react";
import { ExternalLink, LoaderCircle, Search, Globe } from "lucide-react";
import { discoverPapers } from "../api";
import type { DiscoveredPaper } from "../types";

export function DiscoveryPanel() {
  const [query, setQuery] = useState("");
  const [papers, setPapers] = useState<DiscoveredPaper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setSearched(true);

    try {
      const result = await discoverPapers(query.trim());
      setPapers(result.papers as unknown as DiscoveredPaper[]);
    } catch {
      setPapers([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="discovery-panel">
      <div className="discovery-header">
        <Globe size={18} />
        <span>Paper Discovery</span>
        <span className="discovery-source">Semantic Scholar & arXiv</span>
      </div>

      <form className="discovery-search" onSubmit={handleSearch}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for papers..."
        />
        <button type="submit" disabled={!query.trim() || loading}>
          {loading ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Search size={16} />
          )}
          Search
        </button>
      </form>

      <div className="discovery-results">
        {loading && (
          <div className="discovery-loading">
            <LoaderCircle className="spin" size={24} />
            <p>Searching external databases...</p>
          </div>
        )}

        {!loading && searched && papers.length === 0 && (
          <div className="discovery-empty">
            <p>No papers found. Try a different search term.</p>
          </div>
        )}

        {papers.map((paper, i) => (
          <article key={i} className="discovery-card">
            <h4>{paper.title}</h4>
            <p className="discovery-authors">{paper.authors}</p>
            {paper.abstract && (
              <p className="discovery-abstract">
                {paper.abstract.length > 200
                  ? paper.abstract.slice(0, 200) + "..."
                  : paper.abstract}
              </p>
            )}
            <div className="discovery-meta">
              {paper.year && <span>Year: {paper.year}</span>}
              {paper.citation_count != null && (
                <span>Citations: {paper.citation_count}</span>
              )}
              <span className="discovery-badge">{paper.source}</span>
            </div>
            {paper.url && (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="discovery-link"
              >
                <ExternalLink size={14} />
                View Paper
              </a>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
