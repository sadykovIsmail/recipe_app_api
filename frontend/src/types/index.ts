// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  name: string;
}

export interface JWTTokens {
  access: string;
  refresh: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name: string;
}

// ── Social ────────────────────────────────────────────────────────────────────

export interface UserProfile {
  id: number;
  email: string;
  name: string;
  bio: string;
  avatar: string | null;
  website: string;
  location: string;
  followers_count: number;
  following_count: number;
  recipes_count: number;
  is_following: boolean;
}

export interface Follow {
  id: number;
  follower: number;
  following: number;
  created_at: string;
}

export interface Notification {
  id: number;
  kind: 'new_follower' | 'recipe_like' | 'recipe_comment';
  actor: {
    id: number;
    name: string;
    avatar: string | null;
  };
  recipe: {
    id: number;
    title: string;
  } | null;
  is_read: boolean;
  created_at: string;
}

export interface UnreadCount {
  unread_count: number;
}

// ── Recipe ────────────────────────────────────────────────────────────────────

export interface Tag {
  id: number;
  name: string;
}

export interface Ingredient {
  id: number;
  name: string;
}

export interface RecipeAuthor {
  id: number;
  name: string;
  email: string;
  avatar: string | null;
}

export interface Recipe {
  id: number;
  title: string;
  time_minutes: number;
  price: string;
  link: string;
  tags: Tag[];
  ingredients: Ingredient[];
  image: string | null;
  author: RecipeAuthor | null;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
}

export interface RecipeDetail extends Recipe {
  description: string;
}

export interface RecipePayload {
  title: string;
  description?: string;
  time_minutes: number;
  price: string;
  link?: string;
  tags?: { name: string }[];
  ingredients?: { name: string }[];
}

export interface RecipeComment {
  id: number;
  text: string;
  user: {
    id: number;
    name: string;
    avatar: string | null;
  };
  created_at: string;
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── API errors ────────────────────────────────────────────────────────────────

export interface ApiError {
  detail?: string;
  [field: string]: string | string[] | undefined;
}
