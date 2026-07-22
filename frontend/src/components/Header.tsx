import {
  Atom,
  FlaskConical,
  Github,
  RadioTower,
} from "lucide-react";

interface HeaderProps {
  online: boolean;
}

export function Header({ online }: HeaderProps) {
  return (
    <header className="site-header">
      <a href="#top" className="brand" aria-label="ResearchIQ Lab home">
        <span className="brand-mark">
          <FlaskConical size={26} strokeWidth={2.8} />
        </span>
        <span>
          <strong>RESEARCHIQ</strong>
          <small>Experimental Paper Laboratory</small>
        </span>
      </a>

      <nav className="header-nav" aria-label="Primary navigation">
        <a href="#vault">Paper Vault</a>
        <a href="#console">Research Console</a>
        <a href="#comparison">Comparison Reactor</a>
      </nav>

      <div className="header-actions">
        <span className={`status-chip ${online ? "online" : "offline"}`}>
          <RadioTower size={14} />
          {online ? "System online" : "Backend offline"}
        </span>
        <a
          className="icon-button"
          href="https://github.com/"
          target="_blank"
          rel="noreferrer"
          aria-label="Open GitHub"
        >
          <Github size={19} />
        </a>
      </div>

      <Atom className="header-atom" aria-hidden="true" />
    </header>
  );
}
