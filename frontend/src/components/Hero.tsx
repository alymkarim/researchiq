import { ArrowUpRight, FileSearch, Upload } from "lucide-react";

interface HeroProps {
  documentCount: number;
  onUploadClick: () => void;
  onConsoleClick: () => void;
}

export function Hero({
  documentCount,
  onUploadClick,
  onConsoleClick,
}: HeroProps) {
  return (
    <section className="hero">
      <div className="hero-content">
        <span className="hero-badge">
          AI-powered research platform
        </span>

        <h1 className="hero-title">
          Turn dense papers into
          <span className="hero-gradient"> useful insights.</span>
        </h1>

        <p className="hero-subtitle">
          Upload research papers, interrogate the evidence, compare methods
          and extract the useful bits — without fighting through 87 pages.
        </p>

        <div className="hero-actions">
          <button
            type="button"
            className="hero-btn hero-btn-primary"
            onClick={onUploadClick}
          >
            <Upload size={18} />
            Upload Paper
          </button>

          <button
            type="button"
            className="hero-btn hero-btn-secondary"
            onClick={onConsoleClick}
          >
            <FileSearch size={18} />
            Search Collection
            <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="hero-doc-count">
          <span className="hero-doc-count-number">
            {documentCount}
          </span>
          <span className="hero-doc-count-label">
            papers in collection
          </span>
        </div>
      </div>
    </section>
  );
}
