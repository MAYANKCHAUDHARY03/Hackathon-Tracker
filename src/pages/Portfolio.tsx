import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { portfolioApi } from '@/api/portfolioApi';
import type { UserPortfolio } from '@/api/portfolioApi';
import { Briefcase, Calendar, Link as LinkIcon, User, LayoutGrid } from 'lucide-react';
import { format } from 'date-fns';
import { useAuthStore } from '@/store/authStore';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CrossPortfolioView } from '@/components/portfolio/CrossPortfolioView';

export default function Portfolio() {
  const { userId } = useParams<{ userId: string }>();
  const currentUser = useAuthStore(s => s.user);
  const isOwner = currentUser?.id === userId;
  
  const [portfolio, setPortfolio] = useState<UserPortfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;

    const fetchPortfolio = async () => {
      try {
        const response = await portfolioApi.getUserPortfolio(userId);
        setPortfolio(response);
      } catch (error) {
        console.error('Failed to load portfolio', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [userId]);

  if (loading || !portfolio) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Portfolio</h1>
          <p className="text-muted-foreground mt-2">Loading user profile...</p>
        </div>
        <div className="h-64 bg-card border border-border rounded-xl animate-pulse"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      <div className="flex items-center gap-6 p-8 glass-panel rounded-2xl">
        <div className="h-24 w-24 rounded-full bg-primary/20 flex items-center justify-center border-4 border-background">
          <User className="h-10 w-10 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">{portfolio.full_name}</h1>
          <p className="text-muted-foreground mt-2 max-w-2xl">
            {portfolio.bio || "This user hasn't added a bio yet."}
          </p>
        </div>
      </div>

      <Tabs defaultValue="projects" className="space-y-6">
        <TabsList>
          <TabsTrigger value="projects">Personal Projects</TabsTrigger>
          {isOwner && <TabsTrigger value="cross-portfolios">Cross-Hackathon Portfolios</TabsTrigger>}
        </TabsList>
        
        <TabsContent value="projects">
          <div>
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-primary" />
              Projects & Contributions
            </h2>
            
            {portfolio.items.length === 0 ? (
              <div className="text-center p-12 glass-panel rounded-xl">
                <p className="text-muted-foreground italic">No portfolio items found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {portfolio.items.map((item) => (
                  <div key={item.id} className="p-6 glass-panel rounded-xl hover-lift">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-bold">{item.name}</h3>
                          <span className="text-xs px-2 py-1 rounded-full bg-secondary/50 capitalize border border-border/50">
                            {item.type}
                          </span>
                        </div>
                        {item.description && (
                          <p className="text-muted-foreground text-sm mt-2">{item.description}</p>
                        )}
                      </div>
                      <div className="text-right text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center justify-end gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{format(new Date(item.date), 'MMM yyyy')}</span>
                        </div>
                        {item.url && (
                          <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-end gap-1 text-primary hover:underline">
                            <LinkIcon className="h-4 w-4" />
                            <span>View Project</span>
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
        
        {isOwner && (
          <TabsContent value="cross-portfolios">
            <CrossPortfolioView />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
