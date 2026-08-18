import React, { useState, useEffect } from 'react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { Shield, Lock, Users, Globe, Award, Briefcase, Key } from 'lucide-react';

interface VerifiedSkill {
  id: string;
  skill_name: string;
  verification_level: string;
  evidence_trail: any[];
}

interface PortableIdentity {
  visibility_projects: string;
  visibility_achievements: string;
  visibility_skills: string;
  selective_sharing_workspaces: string[];
  total_projects: number;
  total_achievements: number;
  skills: VerifiedSkill[];
}

export default function PortableIdentityPage() {
  const [data, setData] = useState<PortableIdentity | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get<PortableIdentity>('/users/me/portable-identity');
        setData(response);
      } catch (err) {
        console.error('Failed to load portable identity', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const updateVisibility = async (field: keyof PortableIdentity, value: string) => {
    if (!data) return;
    setSaving(true);
    try {
      const response = await apiClient.patch<PortableIdentity>('/users/me/portable-identity', {
        [field]: value
      });
      setData(response);
    } catch (error) {
      console.error('Failed to update visibility', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading && !data) {
    return <div className="p-8 text-center animate-pulse">Loading Identity Passport...</div>;
  }

  if (!data) return <div className="p-8 text-center text-red-500">Failed to load portable identity data.</div>;

  const visibilityOptions = [
    { value: 'private', label: 'Private', icon: Lock },
    { value: 'connection_only', label: 'Connections Only', icon: Users },
    { value: 'selective_sharing', label: 'Selective Sharing', icon: Shield },
    { value: 'public', label: 'Public', icon: Globe },
  ];

  const renderVisibilitySelect = (field: keyof PortableIdentity, currentValue: string) => (
    <select
      className="ml-auto bg-secondary text-sm rounded border-border p-1"
      value={currentValue}
      onChange={(e) => updateVisibility(field, e.target.value)}
      disabled={saving}
    >
      {visibilityOptions.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">
      <div className="flex justify-between items-center border-b border-border/50 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Key className="h-6 w-6 text-primary" /> Portable Innovation Identity
          </h1>
          <p className="text-muted-foreground mt-1">Carry your verified achievements across the entire ecosystem.</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <GlassPanel className="p-6 md:col-span-2 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" /> Privacy & Visibility
          </h2>
          <p className="text-sm text-muted-foreground">Control who can see your verified innovation history. Nothing is public by default.</p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-secondary/10 rounded border border-border">
              <div className="flex items-center gap-3">
                <Briefcase className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h3 className="font-medium">Projects & Portfolio</h3>
                  <p className="text-xs text-muted-foreground">Visibility of your {data.total_projects} projects</p>
                </div>
              </div>
              {renderVisibilitySelect('visibility_projects', data.visibility_projects)}
            </div>

            <div className="flex items-center justify-between p-3 bg-secondary/10 rounded border border-border">
              <div className="flex items-center gap-3">
                <Award className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h3 className="font-medium">Verified Achievements</h3>
                  <p className="text-xs text-muted-foreground">Visibility of your {data.total_achievements} awards & ranks</p>
                </div>
              </div>
              {renderVisibilitySelect('visibility_achievements', data.visibility_achievements)}
            </div>

            <div className="flex items-center justify-between p-3 bg-secondary/10 rounded border border-border">
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h3 className="font-medium">Verified Skills</h3>
                  <p className="text-xs text-muted-foreground">Visibility of your {data.skills.length} verified skills</p>
                </div>
              </div>
              {renderVisibilitySelect('visibility_skills', data.visibility_skills)}
            </div>
          </div>
        </GlassPanel>

        <div className="space-y-6">
          <GlassPanel className="p-6 flex flex-col justify-center items-center text-center">
            <span className="text-4xl font-bold">{data.total_projects}</span>
            <span className="text-sm text-muted-foreground mt-1">Verified Projects</span>
          </GlassPanel>
          <GlassPanel className="p-6 flex flex-col justify-center items-center text-center">
            <span className="text-4xl font-bold">{data.total_achievements}</span>
            <span className="text-sm text-muted-foreground mt-1">Verified Achievements</span>
          </GlassPanel>
        </div>
      </div>

      <GlassPanel className="p-6 space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Award className="h-5 w-5 text-primary" /> Verified Skills
        </h2>
        {data.skills.length === 0 ? (
          <p className="text-sm text-muted-foreground">No verified skills yet. Participate in hackathons to earn them!</p>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {data.skills.map(skill => (
              <div key={skill.id} className="p-4 border border-border rounded bg-secondary/10 flex flex-col justify-between">
                <div>
                  <div className="font-medium text-lg">{skill.skill_name}</div>
                  <div className="text-sm mt-1 flex items-center gap-1 font-semibold text-primary">
                    <Shield className="h-4 w-4" />
                    {skill.verification_level}
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-border/50 text-xs text-muted-foreground">
                  <div className="font-semibold mb-2">Evidence Trail</div>
                  {skill.evidence_trail && skill.evidence_trail.length > 0 ? (
                    <ul className="space-y-2">
                      {skill.evidence_trail.map((ev: any, idx: number) => (
                        <li key={idx} className="flex gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1 shrink-0" />
                          <span>
                            {ev.type === 'submission' && `Project submitted to ${ev.source}`}
                            {ev.type === 'award' && `Won ${ev.award_name} at ${ev.source}`}
                            {ev.type === 'org_verification' && `Verified by ${ev.source}`}
                            {!['submission', 'award', 'org_verification'].includes(ev.type) && JSON.stringify(ev)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="italic">No evidence attached.</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassPanel>
    </div>
  );
}
