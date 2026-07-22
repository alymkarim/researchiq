import {
  ArrowDown,
  Atom,
  BrainCircuit,
  Upload,
} from "lucide-react";

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
      <div className="hero-copy">
        <span className="eyebrow">Classified research facility</span>

        <h1>
          Turn dense papers into
          <span>suspiciously useful insights.</span>
        </h1>

        <p>
          Upload research papers, interrogate the evidence, compare methods
          and extract the useful bits without personally fighting all 87 pages.
        </p>

        <div className="hero-actions">
          <button
            type="button"
            className="primary-button"
            onClick={onUploadClick}
          >
            <Upload size={18} />
            Add a specimen
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={onConsoleClick}
          >
            Enter research console
            <ArrowDown size={18} />
          </button>
        </div>

        <div className="hero-stats">
          <article>
            <strong>{documentCount}</strong>
            <span>Papers secured</span>
          </article>

          <article>
            <strong>4</strong>
            <span>Lab machines</span>
          </article>

          <article>
            <strong>0</strong>
            <span>Brain cells harmed</span>
          </article>
        </div>
      </div>

      <div className="hero-machine" aria-hidden="true">
        <div className="machine-top">
          <span className="machine-label">RIQ-9000</span>

          <div className="signal-lights">
            <span />
            <span />
            <span />
          </div>
        </div>

        <div className="machine-screen">
          <div className="screen-grid" />
          <Atom className="screen-atom" size={88} strokeWidth={1.8} />
          <strong>SYSTEM READY</strong>
          <small>Feed me PDFs. I have questions.</small>
        </div>

        <div className="machine-controls">
          <div className="dial">
            <span />
          </div>

          <div className="meter">
            <span>COGNITIVE LOAD</span>
            <div>
              <i style={{ width: "72%" }} />
            </div>
          </div>

          <div className="machine-button">
            <BrainCircuit size={24} />
          </div>
        </div>

        <span className="floating-badge badge-one">
          <BrainCircuit size={16} />
          AI assisted
        </span>

        <span className="floating-badge badge-two">
          Evidence first
        </span>
      </div>
    </section>
  );
}
