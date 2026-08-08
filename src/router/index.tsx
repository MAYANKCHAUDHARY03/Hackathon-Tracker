import { lazy, Suspense } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
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
const Enterprise = lazy(() => import('@/pages/Enterprise'))
const ApplyPage = lazy(() => import('@/pages/ApplyPage'))
const GraphExplorer = lazy(() => import('@/pages/GraphExplorer'))
const Opportunities = lazy(() => import('@/pages/Opportunities'))

// Loading fallback
const PageLoader = () => (
  <div className="flex h-[50vh] items-center justify-center">
    <div className="h-8 w-8 animate-pulse rounded-full bg-primary/50" />
  </div>
)

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
    errorElement: <div className="p-8 text-destructive">An error occurred in the layout.</div>,
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
        path: 'enterprise',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Enterprise />
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
        path: 'users/:userId/portfolio',
        element: (
          <Suspense fallback={<PageLoader />}>
            <Portfolio />
          </Suspense>
        ),
      },
    ],
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
