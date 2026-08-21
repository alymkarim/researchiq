import { useEffect, useState } from "react";
import { LoaderCircle, MessageSquarePlus, StickyNote, Trash2 } from "lucide-react";
import { createNote, getNotes, deleteNote, createAnnotation, getAnnotations, deleteAnnotation } from "../api";
import type { Note, Annotation } from "../types";

interface CollaborationPanelProps {
  documentId: number;
}

type CollabTab = "notes" | "annotations";

export function CollaborationPanel({ documentId }: CollaborationPanelProps) {
  const [activeTab, setActiveTab] = useState<CollabTab>("notes");
  const [loading, setLoading] = useState(false);

  const [notes, setNotes] = useState<Note[]>([]);
  const [newNote, setNewNote] = useState("");
  const [notePage, setNotePage] = useState("");

  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [newHighlight, setNewHighlight] = useState("");
  const [newComment, setNewComment] = useState("");
  const [annotationPage, setAnnotationPage] = useState("");

  useEffect(() => {
    loadData();
  }, [documentId, activeTab]);

  async function loadData() {
    setLoading(true);
    try {
      if (activeTab === "notes") {
        const data = await getNotes(documentId);
        setNotes(data as unknown as Note[]);
      } else {
        const data = await getAnnotations(documentId);
        setAnnotations(data as unknown as Annotation[]);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  async function handleAddNote() {
    if (!newNote.trim()) return;
    try {
      await createNote(
        documentId,
        newNote.trim(),
        notePage ? parseInt(notePage) : undefined,
      );
      setNewNote("");
      setNotePage("");
      await loadData();
    } catch {
      // ignore
    }
  }

  async function handleDeleteNote(id: number) {
    try {
      await deleteNote(id);
      await loadData();
    } catch {
      // ignore
    }
  }

  async function handleAddAnnotation() {
    if (!newHighlight.trim() || !annotationPage.trim()) return;
    try {
      await createAnnotation(
        documentId,
        parseInt(annotationPage),
        newHighlight.trim(),
        newComment.trim() || undefined,
      );
      setNewHighlight("");
      setNewComment("");
      setAnnotationPage("");
      await loadData();
    } catch {
      // ignore
    }
  }

  async function handleDeleteAnnotation(id: number) {
    try {
      await deleteAnnotation(id);
      await loadData();
    } catch {
      // ignore
    }
  }

  return (
    <section className="collab-panel">
      <div className="collab-header">
        <MessageSquarePlus size={18} />
        <span>Collaboration</span>
      </div>

      <nav className="collab-tabs">
        <button
          className={activeTab === "notes" ? "active" : ""}
          onClick={() => setActiveTab("notes")}
        >
          <StickyNote size={14} />
          Notes ({notes.length})
        </button>
        <button
          className={activeTab === "annotations" ? "active" : ""}
          onClick={() => setActiveTab("annotations")}
        >
          <MessageSquarePlus size={14} />
          Annotations ({annotations.length})
        </button>
      </nav>

      <div className="collab-content">
        {loading && (
          <div className="collab-loading">
            <LoaderCircle className="spin" size={24} />
          </div>
        )}

        {!loading && activeTab === "notes" && (
          <div className="notes-section">
            <div className="note-form">
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add a note..."
                rows={3}
              />
              <div className="note-form-row">
                <input
                  type="number"
                  value={notePage}
                  onChange={(e) => setNotePage(e.target.value)}
                  placeholder="Page #"
                  min="1"
                />
                <button onClick={handleAddNote} disabled={!newNote.trim()}>
                  Add Note
                </button>
              </div>
            </div>

            <div className="notes-list">
              {notes.map((note) => (
                <div key={note.id} className="note-card">
                  <p>{note.content}</p>
                  <div className="note-meta">
                    {note.page_number && <span>Page {note.page_number}</span>}
                    <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    <button onClick={() => handleDeleteNote(note.id)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
              {notes.length === 0 && <p className="collab-empty">No notes yet</p>}
            </div>
          </div>
        )}

        {!loading && activeTab === "annotations" && (
          <div className="annotations-section">
            <div className="annotation-form">
              <input
                value={newHighlight}
                onChange={(e) => setNewHighlight(e.target.value)}
                placeholder="Text to highlight..."
              />
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Comment (optional)"
                rows={2}
              />
              <div className="annotation-form-row">
                <input
                  type="number"
                  value={annotationPage}
                  onChange={(e) => setAnnotationPage(e.target.value)}
                  placeholder="Page #"
                  min="1"
                />
                <button onClick={handleAddAnnotation} disabled={!newHighlight.trim() || !annotationPage.trim()}>
                  Add Annotation
                </button>
              </div>
            </div>

            <div className="annotations-list">
              {annotations.map((ann) => (
                <div key={ann.id} className="annotation-card">
                  <div className="annotation-highlight" style={{ borderLeftColor: ann.color }}>
                    &ldquo;{ann.highlight_text}&rdquo;
                  </div>
                  {ann.comment && <p className="annotation-comment">{ann.comment}</p>}
                  <div className="annotation-meta">
                    <span>Page {ann.page_number}</span>
                    <span>{new Date(ann.created_at).toLocaleDateString()}</span>
                    <button onClick={() => handleDeleteAnnotation(ann.id)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
              {annotations.length === 0 && <p className="collab-empty">No annotations yet</p>}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
