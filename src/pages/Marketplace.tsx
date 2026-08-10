import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '../store/workspaceStore';
import { marketplaceApi } from '../api/marketplaceApi';
import type { MarketplaceProject, MarketplacePartner } from '../api/marketplaceApi';

export const Marketplace: React.FC = () => {
  const { currentWorkspace } = useWorkspaceStore();
  const [activeTab, setActiveTab] = useState<'projects' | 'partners'>('projects');
  
  const [projects, setProjects] = useState<MarketplaceProject[]>([]);
  const [partners, setPartners] = useState<MarketplacePartner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentWorkspace) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'projects') {
          const res = await marketplaceApi.getProjects(currentWorkspace.id);
          setProjects(res.projects);
        } else {
          const res = await marketplaceApi.getPartners(currentWorkspace.id);
          setPartners(res.partners);
        }
      } catch (err) {
        console.error('Error fetching marketplace data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentWorkspace, activeTab]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Innovation Marketplace</h1>
          <p className="mt-1 text-sm text-gray-500">
            Discover projects seeking partners, and partners seeking projects.
          </p>
        </div>
      </div>

      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('projects')}
            className={`whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'projects'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Discover Projects
          </button>
          <button
            onClick={() => setActiveTab('partners')}
            className={`whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'partners'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Discover Partners
          </button>
        </nav>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeTab === 'projects' && projects.length === 0 && (
            <div className="col-span-full py-12 text-center text-gray-500">
              No projects currently seeking partners.
            </div>
          )}
          {activeTab === 'projects' && projects.map(project => (
            <div key={project.id} className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 flex flex-col">
              <div className="px-4 py-5 sm:p-6 flex-grow">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">{project.title}</h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {project.status}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-500 line-clamp-3">
                  {project.description || 'No description available.'}
                </p>
                {project.technologies && project.technologies.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {project.technologies.slice(0, 3).map((tech, idx) => (
                      <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {tech}
                      </span>
                    ))}
                    {project.technologies.length > 3 && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-50 text-gray-500">
                        +{project.technologies.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>
              <div className="bg-gray-50 px-4 py-4 sm:px-6 mt-auto">
                <button
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  onClick={() => alert(`Connection request sent to ${project.title}`)}
                >
                  Request Connection
                </button>
              </div>
            </div>
          ))}

          {activeTab === 'partners' && partners.length === 0 && (
            <div className="col-span-full py-12 text-center text-gray-500">
              No partners currently seeking projects.
            </div>
          )}
          {activeTab === 'partners' && partners.map(partner => (
            <div key={partner.id} className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 flex flex-col">
              <div className="px-4 py-5 sm:p-6 flex-grow">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">{partner.name}</h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {partner.type}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-500 line-clamp-3">
                  {partner.description || 'No description available.'}
                </p>
                {partner.resources_offered && partner.resources_offered.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {partner.resources_offered.map((resource, idx) => (
                      <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        {resource}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="bg-gray-50 px-4 py-4 sm:px-6 mt-auto">
                <button
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  onClick={() => alert(`Connection request sent to ${partner.name}`)}
                >
                  Request Connection
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Marketplace;
