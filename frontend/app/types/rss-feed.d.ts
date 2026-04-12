export interface RSSFeedCreateRequest {
  url: string;
  title: string;
  description?: string | null;
}

export interface RSSFeedUpdateRequest {
  url?: string | null;
  title?: string | null;
  description?: string | null;
}

export interface RSSFeedResponse {
  id: number;
  url: string;
  title: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface RSSFeedListResponse {
  items: RSSFeedResponse[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface RSSFeedExecuteResponse {
  feed_id: number;
  title: string;
  webhook_url: string;
  delivered: boolean;
}

export interface SettingsWebhookResponse {
  webhook_url: string;
}

export interface SettingsWebhookPingResponse {
  pong: boolean;
}
