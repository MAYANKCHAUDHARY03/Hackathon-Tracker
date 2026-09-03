import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Label } from '@/components/ui/label';

export const LoginFlow: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [step, setStep] = useState<'login' | 'context'>('login');
  const [targetOrgId, setTargetOrgId] = useState('');
  
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const setToken = useAuthStore((state) => state.setToken);
  const setUser = useAuthStore((state) => state.setUser);
  
  const redirect = searchParams.get('redirect') || '/';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const { access_token } = await apiClient.post<{ access_token: string }>('/auth/login', { email, password });
      setToken(access_token);
      
      const user = await apiClient.get<any>('/users/me');
      setUser(user);
      
      setStep('context');
    } catch (err: any) {
      setError(err.data?.detail || 'Failed to login');
    }
  };

  const handleContinue = () => {
    // If targetOrgId is provided, we might navigate them to the specific org context
    // or just store it. For MVP, we pass it via query param or store if needed, 
    // but the backend evaluates access dynamically based on path parameter anyway.
    if (targetOrgId) {
      // In a fully integrated UI, they'd be taken to the org's dashboard
      navigate(`/organizations/${targetOrgId}`);
    } else {
      navigate(redirect);
    }
  };

  if (step === 'context') {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader>
            <CardTitle className="text-center text-3xl font-extrabold text-gray-900">
              Select Context
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-sm text-gray-500">
              You are logged in. Do you want to access a federated organization or continue to your home workspace?
            </p>
            <div className="space-y-2">
              <Label htmlFor="targetOrg">Federated Target Organization ID (Optional)</Label>
              <input
                id="targetOrg"
                type="text"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Leave blank for home workspace"
                value={targetOrgId}
                onChange={(e) => setTargetOrgId(e.target.value)}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={handleContinue}>
              Continue
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader>
          <CardTitle className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-6" onSubmit={handleLogin}>
            {error && <div className="text-red-500 text-sm text-center">{error}</div>}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <input
                  id="email"
                  type="email"
                  required
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <input
                  id="password"
                  type="password"
                  required
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            <Button type="submit" className="w-full">
              Sign in
            </Button>
            <div className="text-sm text-center">
              <a href={`/register?redirect=${encodeURIComponent(redirect)}`} className="font-medium text-indigo-600 hover:text-indigo-500">
                Don't have an account? Register
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
