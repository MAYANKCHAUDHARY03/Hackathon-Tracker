import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Loader2 } from 'lucide-react';
import { searchApi } from '@/api/searchApi';
import type { SearchResultItem } from '@/api/searchApi';
import { useWorkspaceStore } from '@/store/workspaceStore';

export function SearchModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const { activeWorkspaceId } = useWorkspaceStore();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    const fetchResults = async () => {
      if (query.trim().length < 2 || !activeWorkspaceId) {
        setResults([]);
        return;
      }
      setLoading(true);
      try {
        const response = await searchApi.search(activeWorkspaceId, query);
        setResults(response.results);
      } catch (error) {
        console.error('Search failed', error);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(fetchResults, 300);
    return () => clearTimeout(debounce);
  }, [query, activeWorkspaceId]);

  if (!isOpen) return null;

  const handleSelect = (url: string) => {
    navigate(url);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-background/80 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="relative w-full max-w-2xl bg-card border border-border rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[60vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center px-4 py-3 border-b border-border">
          <Search className="h-5 w-5 text-muted-foreground mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none outline-none text-foreground text-lg placeholder:text-muted-foreground"
            placeholder="Ask anything, e.g. 'Find projects using computer vision for healthcare'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {loading && <Loader2 className="h-5 w-5 text-muted-foreground animate-spin mr-2" />}
          <button onClick={onClose} className="p-1 rounded-md hover:bg-muted text-muted-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>
        
        {query.length >= 2 && (
          <div className="overflow-y-auto p-2">
            {results.length > 0 ? (
              <div className="flex flex-col gap-1">
                {results.map((item) => (
                  <button
                    key={item.id}
                    className="flex flex-col items-start p-3 text-left rounded-lg hover:bg-muted/50 transition-colors"
                    onClick={() => handleSelect(item.url)}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium text-foreground">{item.title}</span>
                      <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full uppercase tracking-wider">{item.type}</span>
                    </div>
                    {item.description && (
                      <span className="text-sm text-muted-foreground mt-1 line-clamp-1">{item.description}</span>
                    )}
                    {item.graph_context && Object.keys(item.graph_context).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {Object.entries(item.graph_context).map(([type, names]) => 
                          names.map((name, idx) => (
                            <span key={`${type}-${idx}`} className="text-[10px] px-1.5 py-0.5 bg-muted text-muted-foreground rounded border border-border">
                              {type}: {name}
                            </span>
                          ))
                        )}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                {!loading && "No results found."}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
