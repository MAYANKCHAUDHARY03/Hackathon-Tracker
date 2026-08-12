import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, Users, Rocket, BarChart2, Plus, Edit } from 'lucide-react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { impactApi } from '@/api/impactApi';
import type { FunnelMetrics, CustomMetric, ProjectImpact } from '@/api/impactApi';
import { projectsApi } from "@/api/projectsApi";
import type { Project } from "@/types";

export default function ImpactMeasurement() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const [funnelMetrics, setFunnelMetrics] = useState<FunnelMetrics | null>(null);
  const [customMetrics, setCustomMetrics] = useState<CustomMetric[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectImpacts, setProjectImpacts] = useState<ProjectImpact[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [isMetricModalOpen, setIsMetricModalOpen] = useState(false);
  const [newMetric, setNewMetric] = useState({ name: '', description: '', unit: '' });
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [selectedStage, setSelectedStage] = useState<string>('Participation');
  const [jobsCreated, setJobsCreated] = useState<number>(0);
  const [fundingRaised, setFundingRaised] = useState<number>(0);
  const [revenueGenerated, setRevenueGenerated] = useState<number>(0);

  useEffect(() => {
    if (activeWorkspaceId) {
      loadData();
    }
  }, [activeWorkspaceId]);

  const loadData = async () => {
    if (!activeWorkspaceId) return;
    try {
      setLoading(true);
      const [funnelRes, metricRes, projRes, impactRes] = await Promise.all([
        impactApi.getFunnelMetrics(activeWorkspaceId),
        impactApi.getCustomMetrics(activeWorkspaceId),
        projectsApi.getProjects(activeWorkspaceId),
        impactApi.getProjectImpacts(activeWorkspaceId)
      ]);
      setFunnelMetrics(funnelRes);
      setCustomMetrics(metricRes);
      setProjects(projRes);
      setProjectImpacts(impactRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMetric = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId) return;
    try {
      await impactApi.createCustomMetric(activeWorkspaceId, newMetric);
      setNewMetric({ name: '', description: '', unit: '' });
      setIsMetricModalOpen(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateProjectImpact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspaceId || !selectedProject) return;
    try {
      await impactApi.updateProjectImpact(activeWorkspaceId, selectedProject, {
        stage: selectedStage,
        jobs_created: jobsCreated,
        funding_raised: fundingRaised,
        revenue_generated: revenueGenerated,
      });
      setSelectedProject('');
      setJobsCreated(0);
      setFundingRaised(0);
      setRevenueGenerated(0);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-400">Loading impact data...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Impact & Funnel Tracking</h1>
        <p className="text-gray-400">Track long-term ROI, project progression, and custom success metrics.</p>
      </div>

      {/* Funnel Metrics Cards */}
      {funnelMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Users className="text-blue-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Participation</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.participation}</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <BarChart2 className="text-indigo-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Projects</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.projects}</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Rocket className="text-purple-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Prototypes</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.prototypes}</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-yellow-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Pilots</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.pilots}</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-green-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Deployments</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.deployments}</p>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Rocket className="text-orange-400 h-5 w-5" />
              <h3 className="text-gray-400 text-sm font-medium">Startups</h3>
            </div>
            <p className="text-2xl font-bold text-white">{funnelMetrics.startups}</p>
          </div>
        </div>
      )}

      {/* Update Project Impact */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Update Project Funnel Stage</h2>
        <form onSubmit={handleUpdateProjectImpact} className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">Project</label>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
              required
            >
              <option value="">Select Project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-300 mb-1">Funnel Stage</label>
            <select
              value={selectedStage}
              onChange={(e) => setSelectedStage(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
            >
              <option value="Participation">Participation</option>
              <option value="Project">Project</option>
              <option value="Prototype">Prototype</option>
              <option value="Pilot">Pilot</option>
              <option value="Deployment">Deployment</option>
              <option value="Startup">Startup</option>
            </select>
          </div>
          <div className="w-24">
            <label className="block text-sm font-medium text-gray-300 mb-1">Jobs</label>
            <input
              type="number"
              value={jobsCreated}
              onChange={(e) => setJobsCreated(Number(e.target.value))}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
            />
          </div>
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium">
            Update
          </button>
        </form>
      </div>

      {/* Custom Metrics */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Custom Impact Metrics</h2>
          <button
            onClick={() => setIsMetricModalOpen(true)}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Metric
          </button>
        </div>

        {customMetrics.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No custom metrics defined yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customMetrics.map(metric => (
              <div key={metric.id} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white">{metric.name}</h3>
                {metric.description && <p className="text-sm text-gray-400 mt-1">{metric.description}</p>}
                <p className="text-xs text-blue-400 mt-2 font-medium">Unit: {metric.unit}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal for creating custom metric */}
      {isMetricModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 max-w-md w-full border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">New Custom Metric</h2>
            <form onSubmit={handleCreateMetric} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  value={newMetric.name}
                  onChange={(e) => setNewMetric({...newMetric, name: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                <input
                  type="text"
                  value={newMetric.description}
                  onChange={(e) => setNewMetric({...newMetric, description: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Unit (e.g. $, hours, kg CO2)</label>
                <input
                  type="text"
                  value={newMetric.unit}
                  onChange={(e) => setNewMetric({...newMetric, unit: e.target.value})}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white"
                  required
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsMetricModalOpen(false)}
                  className="px-4 py-2 text-gray-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                >
                  Create Metric
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
