export interface BookmarkTag {
    id: number;
    name: string;
}

export interface BookmarkCreateRequest {
    url: string;
    title: string;
    description?: string | null;
    folder_id?: number | null;
    tag_ids?: number[] | null;
}

export interface BookmarkUpdateRequest {
    url?: string | null;
    title?: string | null;
    description?: string | null;
    folder_id?: number | null;
    tag_ids?: number[] | null;
}

export interface BookmarkResponse {
    id: number;
    url: string;
    title: string;
    description: string | null;
    folder_id: number | null;
    tags: BookmarkTag[];
    created_at: string;
    updated_at: string;
}

export interface BookmarkListResponse {
    items: BookmarkResponse[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
}
