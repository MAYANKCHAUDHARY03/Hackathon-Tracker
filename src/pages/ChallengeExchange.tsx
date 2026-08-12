import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { challengeExchangeApi } from '@/api/challengeExchangeApi';
import type { Challenge, Problem } from '@/api/challengeExchangeApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Target, Heart } from 'lucide-react';
import { toast } from 'sonner';

export default function ChallengeExchange() {
  const { activeWorkspaceId } = useWorkspaceStore();
  
  const [activeTab, setActiveTab] = useState('challenges');
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Track interest locally
  const [interestedIds, setInterestedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!activeWorkspaceId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'challenges') {
          const res = await challengeExchangeApi.browseChallenges(activeWorkspaceId, { search_term: searchTerm });
          setChallenges(res.challenges);
        } else {
          const res = await challengeExchangeApi.listProblems(activeWorkspaceId);
          setProblems(res.problems);
        }
      } catch (err) {
        console.error('Error fetching exchange data', err);
      } finally {
        setLoading(false);
      }
    };

    const delayDebounce = setTimeout(() => {
      fetchData();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [activeWorkspaceId, activeTab, searchTerm]);

  const handleExpressInterest = async (challengeId: string) => {
    if (!activeWorkspaceId) return;
    try {
      await challengeExchangeApi.expressInterest(activeWorkspaceId, challengeId);
      setInterestedIds(prev => new Set(prev).add(challengeId));
      toast.success("Interest Registered", {
        description: "Your interest in this challenge has been added to the Innovation Graph.",
      });
    } catch (err) {
      console.error(err);
      toast.error("Error", {
        description: "Failed to register interest.",
      });
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Challenge Exchange</h1>
          <p className="text-muted-foreground mt-1">
            Discover problems to solve and challenges looking for teams.
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="challenges">Active Challenges</TabsTrigger>
          <TabsTrigger value="problems">Open Problems</TabsTrigger>
        </TabsList>

        <TabsContent value="challenges" className="space-y-6">
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input 
              type="text" 
              placeholder="Search challenges..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
          ) : challenges.length === 0 ? (
            <div className="text-center py-12 border rounded-lg border-dashed">
              <h3 className="text-lg font-medium">No challenges found</h3>
              <p className="text-muted-foreground">Try adjusting your search criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {challenges.map(challenge => (
                <Card key={challenge.id} className="flex flex-col">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <Badge variant="outline" className="mb-2">{challenge.domain || 'General'}</Badge>
                      <Badge variant="secondary" className="mb-2">{challenge.difficulty || 'Medium'}</Badge>
                    </div>
                    <CardTitle className="text-xl">{challenge.title}</CardTitle>
                    <CardDescription className="line-clamp-2 mt-2">{challenge.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex-grow">
                    {challenge.problem && (
                      <div className="mt-4 p-3 bg-muted rounded-md text-sm">
                        <span className="font-semibold flex items-center text-primary mb-1">
                          <Target className="w-4 h-4 mr-1" />
                          Solves Problem:
                        </span>
                        {challenge.problem.name}
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">{challenge.submission_count} submissions</span>
                    <Button 
                      variant={interestedIds.has(challenge.id) ? "secondary" : "default"}
                      onClick={() => handleExpressInterest(challenge.id)}
                      disabled={interestedIds.has(challenge.id)}
                    >
                      <Heart className={`w-4 h-4 mr-2 ${interestedIds.has(challenge.id) ? 'fill-current' : ''}`} />
                      {interestedIds.has(challenge.id) ? 'Interested' : 'Express Interest'}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="problems" className="space-y-6">
          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
          ) : problems.length === 0 ? (
            <div className="text-center py-12 border rounded-lg border-dashed">
              <h3 className="text-lg font-medium">No problems found</h3>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {problems.map(problem => (
                <Card key={problem.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <Badge>{problem.domain}</Badge>
                      <Badge variant="outline">{problem.status}</Badge>
                    </div>
                    <CardTitle className="mt-2">{problem.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{problem.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
