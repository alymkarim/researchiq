import {
  ArrowDown,
  Atom,
  BookOpenCheck,
  BrainCircuit,
  FlaskConical,
  Sparkles,
  Upload,
} from "lucide-react";

interface HeroProps {
  documentCount: number;
  onUploadClick: () => void;
}

export function Hero({ documentCount, onUploadClick }: HeroProps) {
  return (
    <section className="hero" id="top">
      <div className="hero-copy">
        <span className="eyebrow">
          <Sparkles size={15} />
          Classified research facility
        </span>

        <h1>
          Turn dense papers into
          <span> suspiciously useful insights.</span>
        </h1>

        <p>
          Upload research papers, interrogate the evidence, compare methods and
          extract the useful bits without personally fighting all 87 pages.
        </p>

        <div className="hero-actions">
          <button className="primary-button" onClick={onUploadClick}>
            <Upload size={19} />
            Add a specimen
          </button>

          <a className="secondary-button" href="#console">
            Enter research console
            <ArrowDown size={18} />
          </a>
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

      <div className="hero-machine" aria-label="ResearchIQ status console">
        <div className="machine-top">
          <span className="machine-label">RIQ-9000</span>
          <div className="signal-lights" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        </div>

        <div className="machine-screen">
          <div className="screen-grid" />
          <Atom className="screen-atom" size={76} />
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

          <button
            className="machine-button"
            onClick={onUploadClick}
            aria-label="Upload papers"
          >
            <FlaskConical size={24} />
          </button>
        </div>

        <div className="floating-badge badge-one">
          <BrainCircuit size={18} />
          AI assisted
        </div>

        <div className="floating-badge badge-two">
          <BookOpenCheck size={18} />
          Evidence first
        </div>
      </div>
    </section>
  );
}
