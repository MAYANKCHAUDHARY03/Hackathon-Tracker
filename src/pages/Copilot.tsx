import React, { useState } from 'react';
import { Bot, Send, ShieldCheck, Sparkles, ChevronDown, ChevronRight, CheckCircle2 } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { copilotApi } from '@/api/copilotApi';
import type { CopilotResponse } from '@/api/copilotApi';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: CopilotResponse;
}

const Copilot = () => {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedEvidence, setExpandedEvidence] = useState<Record<string, boolean>>({});

  const handleSend = async () => {
    if (!query.trim() || !activeWorkspaceId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString() + '_user',
      role: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await copilotApi.ask(activeWorkspaceId, userMessage.content);
      
      const assistantMessage: ChatMessage = {
        id: Date.now().toString() + '_assistant',
        role: 'assistant',
        content: response.answer,
        response: response
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to query copilot:", error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '_error',
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please try again."
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleEvidence = (id: string) => {
    setExpandedEvidence(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  if (!activeWorkspaceId) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] text-center">
        <Bot className="h-12 w-12 text-muted-foreground mb-4" />
        <h2 className="text-xl font-semibold">AI Copilot Unavailable</h2>
        <p className="text-muted-foreground mt-2">Please select a workspace to use the Innovation Copilot.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">AI Innovation Copilot</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about projects, teams, and data in this workspace.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-full">
          <ShieldCheck className="h-4 w-4 text-emerald-500" />
          <span>Queries trusted workspace data only</span>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
              <Bot className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-lg font-medium">How can I help you today?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl mt-4">
              {[
                "Find projects related to healthcare",
                "What are the top skills used in recent hackathons?",
                "Which teams are looking for members?",
                "Summarize the latest submissions"
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(suggestion)}
                  className="p-3 text-sm text-left border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex w-full gap-4",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="h-5 w-5 text-primary" />
                </div>
              )}
              
              <div 
                className={cn(
                  "max-w-[80%] rounded-2xl px-5 py-4",
                  msg.role === 'user' 
                    ? "bg-primary text-primary-foreground rounded-tr-sm" 
                    : "bg-white border shadow-sm rounded-tl-sm"
                )}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
                
                {/* Copilot Metadata */}
                {msg.response && (
                  <div className="mt-4 pt-4 border-t border-border/50 space-y-4">
                    
                    {/* Confidence & Entities */}
                    <div className="flex flex-wrap items-center gap-3">
                      <div className="flex items-center gap-1.5 text-xs font-medium px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Confidence: {(msg.response.confidence * 100).toFixed(0)}%
                      </div>
                      
                      {msg.response.source_entities.map((entity) => (
                        <div key={entity.id} className="text-xs font-medium px-2 py-1 bg-secondary text-secondary-foreground rounded-md border">
                          {entity.type}: {entity.name}
                        </div>
                      ))}
                    </div>

                    {/* Evidence Toggle */}
                    {msg.response.evidence.length > 0 && (
                      <div className="text-sm">
                        <button 
                          onClick={() => toggleEvidence(msg.id)}
                          className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors font-medium"
                        >
                          {expandedEvidence[msg.id] ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                          View Evidence ({msg.response.evidence.length})
                        </button>
                        
                        {expandedEvidence[msg.id] && (
                          <ul className="mt-2 pl-6 space-y-1 text-muted-foreground list-disc marker:text-primary/50">
                            {msg.response.evidence.map((ev, idx) => (
                              <li key={idx}>{ev}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}

                    {/* Recommended Action */}
                    {msg.response.recommended_action && (
                      <div className="mt-2">
                        <Button variant="outline" size="sm" className="gap-2" onClick={() => setQuery(msg.response!.recommended_action!)}>
                          <Sparkles className="h-3.5 w-3.5" />
                          {msg.response.recommended_action}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start gap-4">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
              <Bot className="h-5 w-5 text-primary animate-pulse" />
            </div>
            <div className="bg-white border shadow-sm rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-2">
              <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="pt-4 border-t mt-auto">
        <div className="relative flex items-center">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about projects, skills, or teams..."
            className="w-full min-h-[60px] max-h-[200px] resize-none rounded-xl border border-input bg-background px-4 py-3 pr-14 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            rows={1}
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!query.trim() || loading}
            className="absolute right-2 bottom-2 h-10 w-10 rounded-lg"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-center text-muted-foreground mt-3">
          AI Copilot answers using only trusted data from your workspace. It does not invent information.
        </p>
      </div>
    </div>
  );
};

export default Copilot;
