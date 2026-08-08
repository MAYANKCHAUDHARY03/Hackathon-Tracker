import { apiClient } from '../lib/api-client';

export interface OpportunityMatch {
    target_id: string;
    target_type: string;
    target_name: string;
    score: number;
    reasons: string[];
    evidence: string[];
    limitations: string[];
}

export interface OpportunityMatchResponse {
    matches: OpportunityMatch[];
}

export const opportunityApi = {
    getMatches: async (
        workspaceId: string,
        entityId: string,
        entityType: string,
        targetType: string
    ): Promise<OpportunityMatchResponse> => {
        const queryParams = new URLSearchParams({
            workspace_id: workspaceId,
            entity_id: entityId,
            entity_type: entityType,
            target_type: targetType
        }).toString();
        
        return await apiClient.get<OpportunityMatchResponse>(`/opportunities/match?${queryParams}`);
    }
};
