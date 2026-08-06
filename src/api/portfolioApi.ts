import { apiClient as api } from "@/lib/api-client";

export interface PortfolioItem {
  id: string;
  name: string;
  description?: string;
  type: string;
  url?: string;
  date: string;
}

export interface UserPortfolio {
  user_id: string;
  full_name: string;
  bio?: string;
  items: PortfolioItem[];
}

export const portfolioApi = {
  getUserPortfolio: (userId: string) =>
    api.get<UserPortfolio>(`/users/${userId}/portfolio`),
};
