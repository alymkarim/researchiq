import { useEffect, useMemo, useState } from "react";
import {
  analyseDocument,
  comparePapers,
  deleteDocument,
  getDocuments,
  searchPapers,
  uploadDocuments,
} from "./api";

import { AnalysisPanel } from "./components/AnalysisPanel";
import { ComparisonPanel } from "./components/ComparisonPanel";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { PaperVault } from "./components/PaperVault";
import { ResearchConsole } from "./components/ResearchConsole";
import { SystemStatus } from "./components/SystemStatus";
import { Toast } from "./components/Toast";
import { UploadPanel } from "./components/UploadPanel";

import type {
  Analysis,
  ComparisonResult,
  DocumentItem,
  SearchResult,
} from "./types";

export type WorkspaceTab =
  | "overview"
  | "search"
  | "analysis"
  | "comparison";

interface ToastState {
  message: string;
  type: "success" | "error";
}

export default function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [analysingId, setAnalysingId] = useState<number | null>(
    null,
  );

  const [activeDocumentId, setActiveDocumentId] = useState<
    number | null
  >(null);

  const [activeAnalysis, setActiveAnalysis] =
    useState<Analysis | null>(null);

  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>(
    [],
  );

  const [comparing, setComparing] = useState(false);

  const [comparison, setComparison] =
    useState<ComparisonResult | null>(null);

  const [toast, setToast] = useState<ToastState | null>(null);
  const [online, setOnline] = useState(true);

  const [activeTab, setActiveTab] =
    useState<WorkspaceTab>("overview");

  const activeDocument = useMemo(
    () =>
      documents.find(
        (document) => document.id === activeDocumentId,
      ),
    [documents, activeDocumentId],
  );

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function loadDocuments() {
    setLoading(true);

    try {
      const data = await getDocuments();

      setDocuments(data.items);
      setOnline(true);
    } catch (error) {
      setOnline(false);
      showError(error);
    } finally {
      setLoading(false);
    }
  }

  function showError(error: unknown) {
    setToast({
      type: "error",
      message:
        error instanceof Error
          ? error.message
          : "The laboratory experienced an unexplained wobble.",
    });
  }

  function openWorkspace(tab: WorkspaceTab) {
    setActiveTab(tab);

    requestAnimationFrame(() => {
      document.getElementById("workspace")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function scrollToUpload() {
    requestAnimationFrame(() => {
      document.getElementById("upload")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function scrollToPaperVault() {
    requestAnimationFrame(() => {
      document.getElementById("paper-vault")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function scrollToResearchConsole() {
  setActiveTab("search");

  requestAnimationFrame(() => {
    document.getElementById("console")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
}

  function toggleDocument(id: number) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((value) => value !== id)
        : [...current, id],
    );
  }

  async function handleUpload(files: File[]) {
    setUploading(true);

    try {
      const created = await uploadDocuments(files);

      setDocuments((current) => [...created, ...current]);
      setOnline(true);

      setToast({
        type: "success",
        message: `${created.length} specimen${
          created.length === 1 ? "" : "s"
        } safely contained.`,
      });
    } catch (error) {
      showError(error);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: number) {
    const target = documents.find(
      (document) => document.id === id,
    );

    const confirmed = window.confirm(
      `Incinerate "${
        target?.title || target?.filename || "this paper"
      }"?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteDocument(id);

      setDocuments((current) =>
        current.filter((document) => document.id !== id),
      );

      setSelectedIds((current) =>
        current.filter((selectedId) => selectedId !== id),
      );

      if (activeDocumentId === id) {
        setActiveDocumentId(null);
        setActiveAnalysis(null);
      }

      setToast({
        type: "success",
        message: "Specimen successfully incinerated.",
      });
    } catch (error) {
      showError(error);
    }
  }

  async function handleAnalyse(id: number) {
    setAnalysingId(id);
    openWorkspace("analysis");

    try {
      const analysis = await analyseDocument(id);

      setActiveDocumentId(id);
      setActiveAnalysis(analysis);

      setDocuments((current) =>
        current.map((document) =>
          document.id === id
            ? {
                ...document,
                analysis,
              }
            : document,
        ),
      );

      setToast({
        type: "success",
        message:
          analysis.analysis_mode === "llm"
            ? "LLM analysis complete. The paper has confessed."
            : "Local analysis complete. The LLM was unavailable.",
      });
    } catch (error) {
      showError(error);
    } finally {
      setAnalysingId(null);
    }
  }

  async function handleSearch(query: string) {
    setSearching(true);
    setActiveTab("search");

    try {
      const results = await searchPapers(
        query,
        selectedIds,
      );

      setSearchResults(results);
    } catch (error) {
      showError(error);
    } finally {
      setSearching(false);
    }
  }

  async function handleCompare() {
    if (selectedIds.length < 2) {
      setToast({
        type: "error",
        message:
          "Select at least two papers before comparing them.",
      });

      return;
    }

    setComparing(true);
    setActiveTab("comparison");

    try {
      const result = await comparePapers(selectedIds);

      setComparison(result);

      setToast({
        type: "success",
        message:
          "Comparison reactor completed without exploding.",
      });
    } catch (error) {
      showError(error);
    } finally {
      setComparing(false);
    }
  }

  return (
    <div className="app-shell">
      <Header
        online={online}
        activeTab={activeTab}
        onNavigate={openWorkspace}
        onPaperVaultClick={scrollToPaperVault}
      />

      <main className="app-main">
        <Hero
          documentCount={documents.length}
          onUploadClick={scrollToUpload}
          onConsoleClick={() => openWorkspace("search")}
        />

        <div className="status-row">
          <SystemStatus />

          <span>
            {selectedIds.length} selected · {documents.length} in
            the vault
          </span>
        </div>

        <section
          className="research-workspace"
          id="workspace"
        >
          <aside className="workspace-sidebar">
            <div
              id="upload"
              className="scroll-anchor"
            >
              <UploadPanel
                busy={uploading}
                onUpload={handleUpload}
              />
            </div>

            <div
              id="paper-vault"
              className="scroll-anchor"
            >
              <PaperVault
                documents={documents}
                loading={loading}
                selectedIds={selectedIds}
                analysingId={analysingId}
                onToggle={toggleDocument}
                onAnalyse={handleAnalyse}
                onDelete={handleDelete}
              />
            </div>
          </aside>

          <section className="workspace-content">
            <nav
              className="workspace-tabs"
              aria-label="Research tools"
            >
              {(
                [
                  ["overview", "Overview"],
                  ["search", "Search"],
                  ["analysis", "Analysis"],
                  [
                    "comparison",
                    `Compare (${selectedIds.length})`,
                  ],
                ] as const
              ).map(([tab, label]) => (
                <button
                  key={tab}
                  type="button"
                  className={`workspace-tab ${
                    activeTab === tab ? "active" : ""
                  }`}
                  onClick={() => setActiveTab(tab)}
                >
                  {label}
                </button>
              ))}
            </nav>

            <div className="workspace-panel">
              {activeTab === "overview" && (
                <section className="workspace-overview">
                  <div className="overview-heading">
                    <span className="eyebrow">
                      Research workspace
                    </span>

                    <h2>
                      One workspace. No laboratory hiking
                      required.
                    </h2>

                    <p>
                      Upload and select papers from the library,
                      then switch between search, structured
                      analysis and comparison.
                    </p>
                  </div>

                  <div className="overview-cards">
                    <button
                      type="button"
                      className="overview-card"
                      onClick={() => setActiveTab("search")}
                    >
                      <strong>Search papers</strong>

                      <span>
                        Find relevant passages across the selected
                        documents.
                      </span>
                    </button>

                    <button
                      type="button"
                      className="overview-card"
                      onClick={() => setActiveTab("analysis")}
                    >
                      <strong>Analyse a paper</strong>

                      <span>
                        Extract its summary, methods, findings,
                        strengths and limitations.
                      </span>
                    </button>

                    <button
                      type="button"
                      className="overview-card"
                      onClick={() =>
                        setActiveTab("comparison")
                      }
                    >
                      <strong>Compare papers</strong>

                      <span>
                        Compare two or more selected papers in one
                        view.
                      </span>
                    </button>
                  </div>

                  <div className="workflow-note">
                    <strong>Workflow</strong>

                    <span>
                      Upload → select → analyse, search or compare.
                    </span>
                  </div>
                </section>
              )}

              {activeTab === "search" && (
                <ResearchConsole
                  selectedCount={selectedIds.length}
                  searching={searching}
                  results={searchResults}
                  onSearch={handleSearch}
                />
              )}

              {activeTab === "analysis" && (
                <AnalysisPanel
                  document={activeDocument}
                  analysis={
                    activeAnalysis ||
                    activeDocument?.analysis
                  }
                />
              )}

              {activeTab === "comparison" && (
                <ComparisonPanel
                  documents={documents}
                  selectedIds={selectedIds}
                  comparing={comparing}
                  result={comparison}
                  onCompare={handleCompare}
                />
              )}
            </div>
          </section>
        </section>
      </main>

      <footer>
        <span>
          RESEARCHIQ LAB · BUILT FOR CURIOUS HUMANS
        </span>

        <span>
          AI can assist. Evidence still has to do the heavy
          lifting.
        </span>
      </footer>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}