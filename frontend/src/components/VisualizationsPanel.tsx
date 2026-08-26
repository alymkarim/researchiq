import { useEffect, useState } from "react";
import { BarChart3, LoaderCircle, Network, Clock } from "lucide-react";
import { getWordCloud, getKeywordNetwork, getMethodologyTimeline } from "../api";
import type { WordCloudItem, NetworkNode, NetworkEdge, TimelineStep } from "../types";

interface VisualizationsPanelProps {
  documentId: number;
  hasAnalysis?: boolean;
}

type VizTab = "wordcloud" | "network" | "timeline";

export function VisualizationsPanel({ documentId, hasAnalysis = false }: VisualizationsPanelProps) {
  const [activeTab, setActiveTab] = useState<VizTab>("wordcloud");
  const [loading, setLoading] = useState(false);

  const [wordCloud, setWordCloud] = useState<WordCloudItem[]>([]);
  const [network, setNetwork] = useState<{ nodes: NetworkNode[]; edges: NetworkEdge[] } | null>(null);
  const [timeline, setTimeline] = useState<TimelineStep[]>([]);

  if (!hasAnalysis && activeTab === "timeline") {
    return (
      <section className="viz-panel">
        <div className="viz-header">
          <BarChart3 size={18} />
          <span>Visualizations</span>
        </div>
        <div className="feature-locked">
          <div className="feature-locked-icon">
            <BarChart3 size={40} />
          </div>
          <h3>Paper analysis required</h3>
          <p>To see methodology timeline, analyse the paper first.</p>
          <div className="feature-locked-steps">
            <span>1. Select a paper from the vault</span>
            <span>2. Click the <strong>Analyse</strong> button</span>
            <span>3. Wait for analysis to complete</span>
          </div>
        </div>
      </section>
    );
  }

  useEffect(() => {
    loadData();
  }, [documentId, activeTab]);

  async function loadData() {
    setLoading(true);
    try {
      if (activeTab === "wordcloud") {
        const data = await getWordCloud(documentId);
        setWordCloud(data);
      } else if (activeTab === "network") {
        const data = await getKeywordNetwork(documentId);
        setNetwork(data as unknown as { nodes: NetworkNode[]; edges: NetworkEdge[] });
      } else {
        const data = await getMethodologyTimeline(documentId);
        setTimeline(data);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  const maxValue = wordCloud.length > 0 ? wordCloud[0].value : 1;

  return (
    <section className="viz-panel">
      <div className="viz-header">
        <BarChart3 size={18} />
        <span>Visualizations</span>
      </div>

      <nav className="viz-tabs">
        <button
          className={activeTab === "wordcloud" ? "active" : ""}
          onClick={() => setActiveTab("wordcloud")}
        >
          <BarChart3 size={14} />
          Word Cloud
        </button>
        <button
          className={activeTab === "network" ? "active" : ""}
          onClick={() => setActiveTab("network")}
        >
          <Network size={14} />
          Keywords
        </button>
        <button
          className={activeTab === "timeline" ? "active" : ""}
          onClick={() => setActiveTab("timeline")}
        >
          <Clock size={14} />
          Timeline
        </button>
      </nav>

      <div className="viz-content">
        {loading && (
          <div className="viz-loading">
            <LoaderCircle className="spin" size={24} />
          </div>
        )}

        {!loading && activeTab === "wordcloud" && (
          <div className="wordcloud">
            {wordCloud.map((item) => (
              <span
                key={item.text}
                className="wordcloud-word"
                style={{
                  fontSize: `${Math.max(12, Math.round(40 * (item.value / maxValue)))}px`,
                  opacity: 0.5 + 0.5 * (item.value / maxValue),
                }}
              >
                {item.text}
              </span>
            ))}
            {wordCloud.length === 0 && <p className="viz-empty">No data available</p>}
          </div>
        )}

        {!loading && activeTab === "network" && network && (
          <div className="keyword-network">
            <div className="network-nodes">
              {network.nodes.map((node) => (
                <span key={node.id} className="network-node" style={{
                  fontSize: `${Math.max(11, Math.round(11 + node.size * 0.5))}px`,
                }}>
                  {node.label}
                </span>
              ))}
            </div>
            {network.edges.length > 0 && (
              <div className="network-edges">
                <p className="network-edges-label">Connections:</p>
                {network.edges.slice(0, 10).map((edge, i) => (
                  <span key={i} className="network-edge">
                    {edge.source} — {edge.target} ({edge.weight})
                  </span>
                ))}
              </div>
            )}
            {network.nodes.length === 0 && <p className="viz-empty">No data available</p>}
          </div>
        )}

        {!loading && activeTab === "timeline" && (
          <div className="methodology-timeline">
            {timeline.map((step) => (
              <div key={step.step} className="timeline-step">
                <span className="timeline-number">{step.step}</span>
                <p>{step.description}</p>
              </div>
            ))}
            {timeline.length === 0 && <p className="viz-empty">No methodology data available</p>}
          </div>
        )}
      </div>
    </section>
  );
}
