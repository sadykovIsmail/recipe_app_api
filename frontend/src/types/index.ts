// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
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

// ── Recipe ────────────────────────────────────────────────────────────────────

export interface Tag {
  id: number;
  name: string;
}

export interface Ingredient {
  id: number;
  name: string;
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
