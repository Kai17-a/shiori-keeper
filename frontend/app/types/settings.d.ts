export interface SettingsWebhookCreateRequest {
  webhook_url: string;
}

export interface SettingsWebhookResponse {
  id: number;
  webhook_url: string;
  created_at: string;
  updated_at: string;
}

export interface SettingsWebhookListResponse {
  items: SettingsWebhookResponse[];
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
