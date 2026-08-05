export type ID = string;
export type ISO8601Date = string;

export interface BaseEntity {
  id: ID;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

export interface SoftDeletable {
  deleted_at?: ISO8601Date | null;
}

export interface Workspace extends BaseEntity {
  name: string;
  slug: string;
  settings: Record<string, any>;
}

export interface User extends BaseEntity {
  full_name: string;
  email: string;
  is_active: boolean;
  avatar_url?: string;
  github_handle?: string;
  linkedin_url?: string;
}

export interface Hackathon extends BaseEntity, SoftDeletable {
  workspace_id: ID;
  name: string;
  website_url?: string;
  description?: string;
  start_date: ISO8601Date;
  end_date: ISO8601Date;
  status_id: ID; // FK to Status
  location?: string;
  is_online: boolean;
}

export interface Team extends BaseEntity {
  hackathon_id: ID;
  name: string;
  tagline?: string;
}

export interface Project extends BaseEntity, SoftDeletable {
  team_id: ID;
  name: string;
  description?: string;
  github_repo_url?: string;
  demo_url?: string;
}

export interface Round extends BaseEntity {
  hackathon_id: ID;
  name: string; // e.g., "Abstract Submission", "Finals"
  order: number;
}

export interface RoundProgress extends BaseEntity {
  team_id: ID;
  round_id: ID;
  status_id: ID; // FK to Status (e.g., passed, failed, pending)
  score?: number;
  feedback?: string;
}

export interface Technology extends BaseEntity {
  name: string;
  icon_url?: string;
  color?: string;
}

export interface ProjectTechnology {
  project_id: ID;
  technology_id: ID;
}

export interface SubmissionLink extends BaseEntity {
  project_id: ID;
  title: string;
  url: string;
  type: string; // e.g., 'video', 'slides', 'figma'
}

export interface Deadline extends BaseEntity {
  hackathon_id: ID;
  title: string;
  due_date: ISO8601Date;
  description?: string;
}

export interface Reward extends BaseEntity {
  hackathon_id: ID;
  title: string;
  description?: string;
  value?: number; // e.g., prize money
  currency?: string;
}

export interface Status extends BaseEntity {
  workspace_id: ID;
  entity_type: 'hackathon' | 'team' | 'round_progress' | 'task'; 
  name: string; // e.g., "Planning", "Registered", "Round 1"
  color: string;
  order: number;
}

export interface ApiKey extends BaseEntity {
  workspace_id: ID;
  provider: string;
  key_hint: string; // masked key for display
  // The actual key won't be stored in plain text normally, 
  // but for the vault we might store it securely or only allow updating.
}

// Role-junction tables
export interface TeamMember {
  team_id: ID;
  user_id: ID;
  role: string; // e.g., "Leader", "Developer", "Designer"
}

export interface HackathonMentor {
  hackathon_id: ID;
  user_id: ID;
}

export interface HackathonJudge {
  hackathon_id: ID;
  user_id: ID;
}

// Normalized State Structure Helper
export interface NormalizedState<T> {
  byId: Record<ID, T>;
  allIds: ID[];
}
