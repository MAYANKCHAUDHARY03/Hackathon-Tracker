import { lazy, Suspense } from 'react'
import { createBrowserRouter, RouterProvider, useRouteError } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'

const Dashboard = lazy(() => import('@/pages/Dashboard'))
const Placeholder = lazy(() => import('@/pages/Placeholder'))
const AcceptInvitation = lazy(() => import('@/pages/AcceptInvitation'))
const Settings = lazy(() => import('@/pages/Settings'))
const Kanban = lazy(() => import('@/pages/Kanban'))
const Hackathons = lazy(() => import('@/pages/Hackathons'))
const HackathonDetails = lazy(() => import('@/pages/HackathonDetails'))
const SubmissionWorkspace = lazy(() => import('@/pages/SubmissionWorkspace'))
const Calendar = lazy(() => import('@/pages/Calendar'))
const Notifications = lazy(() => import('@/pages/Notifications'))
const Analytics = lazy(() => import('@/pages/Workspace/Analytics'))
const Portfolio = lazy(() => import('@/pages/Portfolio'))
const OrgPortfolio = lazy(() => import('@/pages/OrgPortfolio'))
const ProjectDetails = lazy(() => import('@/pages/ProjectDetails'))
const WorkspacePortfolio = lazy(() => import('@/pages/WorkspacePortfolio'))
const ApplyPage = lazy(() => import('@/pages/ApplyPage'))
const GraphExplorer = lazy(() => import('@/pages/GraphExplorer'))
const Opportunities = lazy(() => import('@/pages/Opportunities'))
const Marketplace = lazy(() => import('../pages/Marketplace'))
const ChallengeExchange = lazy(() => import('../pages/ChallengeExchange'))
const Intelligence = lazy(() => import('@/pages/Intelligence'))
const Copilot = lazy(() => import('@/pages/Copilot'))
const Forecasting = lazy(() => import('@/pages/Forecasting'))
const ImpactMeasurement = lazy(() => import('@/pages/ImpactMeasurement'))
const Observatory = lazy(() => import('@/pages/Observatory'))
const Federation = lazy(() => import('@/pages/Federation'))
const Vault = lazy(() => import('@/pages/Vault'))
const Governance = lazy(() => import('@/pages/Governance'))
const InnovationGraph = lazy(() => import('@/pages/InnovationGraph'))
const Automation = lazy(() => import('@/pages/Automation'))
const Incubation = lazy(() => import('@/pages/Incubation'))
const DeveloperPortal = lazy(() => import('@/pages/DeveloperPortal'))
const HubIntegration = lazy(() => import('@/pages/HubIntegration'))
const Teams = lazy(() => import('@/pages/Teams'))
const Projects = lazy(() => import('@/pages/Projects'))

// Loading fallback
const PageLoader = () => (
  <div className="flex h-[50vh] items-center justify-center">
    <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
  </div>
)

const RootErrorBoundary = () => {
  const error = useRouteError() as any;
  console.error(error);
  return (
    <div className="p-8 text-destructive">
      <h1 className="text-2xl font-bold">An error occurred in the layout.</h1>
      <pre className="mt-4 p-4 bg-secondary/50 rounded overflow-auto text-sm">
        {error?.message || error?.statusText || String(error)}
      </pre>
      <pre className="mt-4 p-4 bg-secondary/50 rounded overflow-auto text-xs">
        {error?.stack}
      </pre>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/apply/:formId',
    element: (
      <Suspense fallback={<PageLoader />}>
        <ApplyPage />
      </Suspense>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    errorElement: <RootErrorBoundary />,
    children: [
      {
        path: 'invitations/:token/accept',
        element: (
          <Suspense fallback={<PageLoader />}>
            <AcceptInvitation />
          </Suspense>
        ),
      },
      {
        index: true,
        element: (
          <Suspense fallback={<PageLoader />}>
            <Dashboard />
          </Suspense>
        ),
      },
      {
        path: 'hackathons',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Hackathons />
          </Suspense>
        ),
      },
      {
        path: 'hackathons/:id',
        element: (
          <Suspense fallback={<PageLoader />}>
            <HackathonDetails />
          </Suspense>
        ),
      },
      {
        path: 'hackathons/:id/rounds/:roundId/teams/:teamId/submission',
        element: (
          <Suspense fallback={<PageLoader />}>
            <SubmissionWorkspace />
          </Suspense>
        ),
      },
      {
        path: 'calendar',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Calendar />
          </Suspense>
        ),
      },
      {
        path: 'kanban',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Kanban />
          </Suspense>
        ),
      },
      {
        path: 'analytics',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Analytics />
          </Suspense>
        ),
      },
      {
        path: 'challenge-exchange',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ChallengeExchange />
          </Suspense>
        ),
      },
      {
        path: 'intelligence',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Intelligence />
          </Suspense>
        ),
      },
      {
        path: 'copilot',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Copilot />
          </Suspense>
        ),
      },
      {
        path: 'forecasting',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Forecasting />
          </Suspense>
        ),
      },
      {
        path: 'impact',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ImpactMeasurement />
          </Suspense>
        ),
      },
      {
        path: 'observatory',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Observatory />
          </Suspense>
        ),
      },
      {
        path: 'teams',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Teams />
          </Suspense>
        ),
      },
      {
        path: 'projects',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Projects />
          </Suspense>
        ),
      },
      {
        path: 'projects/:id',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ProjectDetails />
          </Suspense>
        ),
      },
      {
        path: 'graph',
        element: (
          <Suspense fallback={<PageLoader />}>
            <InnovationGraph />
          </Suspense>
        ),
      },
      {
        path: 'vault',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Vault />
          </Suspense>
        ),
      },
      {
        path: 'governance',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Governance />
          </Suspense>
        ),
      },
      {
        path: 'notifications',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Notifications />
          </Suspense>
        ),
      },
      {
        path: 'incubation',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Incubation />
          </Suspense>
        ),
      },
      {
        path: 'federation',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Federation />
          </Suspense>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Settings />
          </Suspense>
        ),
      },
      {
        path: 'portfolio',
        element: (
          <Suspense fallback={<PageLoader />}>
            <WorkspacePortfolio />
          </Suspense>
        ),
      },
      {
        path: 'knowledge-graph',
        element: (
          <Suspense fallback={<PageLoader />}>
            <GraphExplorer />
          </Suspense>
        ),
      },
      {
        path: 'opportunities',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Opportunities />
          </Suspense>
        ),
      },
      {
        path: 'marketplace',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Marketplace />
          </Suspense>
        ),
      },
      {
        path: 'users/:userId/portfolio',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Portfolio />
          </Suspense>
        ),
      },
      {
        path: 'organizations/:orgId/portfolio',
        element: (
          <Suspense fallback={<PageLoader />}>
            <OrgPortfolio />
          </Suspense>
        ),
      },
      {
        path: 'automation',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Automation />
          </Suspense>
        ),
      },
      {
        path: 'developer',
        element: (
          <Suspense fallback={<PageLoader />}>
            <DeveloperPortal />
          </Suspense>
        ),
      },
      {
        path: 'integrations',
        element: (
          <Suspense fallback={<PageLoader />}>
            <HubIntegration />
          </Suspense>
        ),
      },
    ],
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
