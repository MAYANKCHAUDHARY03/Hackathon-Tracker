import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRouter } from '@/router';
import { BootSequence } from '@/components/layout/BootSequence';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BootSequence>
        <AppRouter />
      </BootSequence>
    </QueryClientProvider>
  );
}
