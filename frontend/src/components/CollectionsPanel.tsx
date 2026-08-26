import { useEffect, useState } from "react";
import { Folder, FolderPlus, LoaderCircle, Plus, Trash2, X } from "lucide-react";
import { getCollections, createCollection, deleteCollection, addDocumentToCollection } from "../api";

interface Collection {
  id: number;
  name: string;
  description: string | null;
  color: string;
  document_count: number;
}

interface CollectionsPanelProps {
  selectedIds?: number[];
  onSelectCollection?: (id: number) => void;
}

export function CollectionsPanel({ selectedIds = [], onSelectCollection }: CollectionsPanelProps) {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);
  const [addingTo, setAddingTo] = useState<number | null>(null);

  useEffect(() => {
    loadCollections();
  }, []);

  async function loadCollections() {
    setLoading(true);
    try {
      const data = await getCollections();
      setCollections(data as unknown as Collection[]);
    } catch {
      setCollections([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      await createCollection(newName.trim(), newDesc.trim() || undefined);
      setNewName("");
      setNewDesc("");
      setShowForm(false);
      await loadCollections();
    } catch {
      // ignore
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteCollection(id);
      await loadCollections();
    } catch {
      // ignore
    }
  }

  async function handleAddToCollection(collectionId: number) {
    if (selectedIds.length === 0) return;
    setAddingTo(collectionId);
    try {
      for (const docId of selectedIds) {
        await addDocumentToCollection(collectionId, docId);
      }
      await loadCollections();
    } catch {
      // ignore
    } finally {
      setAddingTo(null);
    }
  }

  return (
    <section className="collections-panel">
      <div className="collections-header">
        <Folder size={18} />
        <span>Collections</span>
        <button className="collections-add-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? <X size={16} /> : <FolderPlus size={16} />}
        </button>
      </div>

      {showForm && (
        <div className="collections-form">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Collection name"
          />
          <input
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            placeholder="Description (optional)"
          />
          <button onClick={handleCreate} disabled={!newName.trim() || creating}>
            {creating ? <LoaderCircle className="spin" size={14} /> : "Create"}
          </button>
        </div>
      )}

      {selectedIds.length > 0 && collections.length > 0 && (
        <div className="collections-add-section">
          <span className="collections-add-label">
            Add {selectedIds.length} paper{selectedIds.length !== 1 ? "s" : ""} to:
          </span>
          {collections.map((col) => (
            <button
              key={col.id}
              className="collections-add-to-btn"
              onClick={() => handleAddToCollection(col.id)}
              disabled={addingTo === col.id}
            >
              {addingTo === col.id ? (
                <LoaderCircle className="spin" size={12} />
              ) : (
                <Plus size={12} />
              )}
              {col.name}
            </button>
          ))}
        </div>
      )}

      <div className="collections-list">
        {loading && (
          <div className="collections-loading">
            <LoaderCircle className="spin" size={20} />
          </div>
        )}

        {!loading && collections.length === 0 && (
          <p className="collections-empty">No collections yet</p>
        )}

        {collections.map((col) => (
          <div
            key={col.id}
            className="collection-card"
            onClick={() => onSelectCollection?.(col.id)}
          >
            <div className="collection-icon" style={{ background: col.color }}>
              <Folder size={16} />
            </div>
            <div className="collection-info">
              <span className="collection-name">{col.name}</span>
              <span className="collection-count">{col.document_count} papers</span>
            </div>
            <button
              className="collection-delete"
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(col.id);
              }}
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
