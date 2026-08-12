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
const Marketplace = lazy(() => import('@/pages/Marketplace'))
const Intelligence = lazy(() => import('@/pages/Intelligence'))
const Copilot = lazy(() => import('@/pages/Copilot'))

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
            <Placeholder title="Hackathons" />
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
        path: 'teams',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Placeholder title="Team Database" />
          </Suspense>
        ),
      },
      {
        path: 'projects',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Placeholder title="Project Database" />
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
        path: 'vault',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Placeholder title="API Vault" />
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
        path: 'graph',
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
    ],
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
