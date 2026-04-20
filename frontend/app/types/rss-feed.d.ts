export interface RSSFeedCreateRequest {
  url: string;
  title: string;
  description?: string | null;
  notify_webhook_enabled?: boolean;
}

export interface RSSFeedUpdateRequest {
  url?: string | null;
  title?: string | null;
  description?: string | null;
  notify_webhook_enabled?: boolean | null;
}

export interface RSSFeedResponse {
  id: number;
  url: string;
  title: string;
  description: string | null;
  notify_webhook_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface RSSFeedArticleResponse {
  id: number;
  feed_id: number;
  url: string;
  title: string | null;
  published: string | null;
  created_at: string;
}

export interface RSSFeedArticleListResponse {
  items: RSSFeedArticleResponse[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
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
  message?: string | null;
}

export interface SettingsWebhookResponse {
  webhook_url: string;
}

export interface SettingsWebhookPingResponse {
  pong: boolean;
}

export interface SettingsRssExecutionResponse {
  enabled: boolean;
}

export interface SettingsRssWebhookNotificationResponse {
  enabled: boolean;
}
