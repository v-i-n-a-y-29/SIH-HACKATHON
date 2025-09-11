// Centralized API helper for backend integration
// Uses Vite env var VITE_API_BASE; falls back to localhost

export const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE || 'http://127.0.0.1:8000';

type QueryParams = Record<string, string | number | boolean | undefined | null>;

export function buildUrl(path: string, params?: QueryParams): string {
	const url = new URL(path.startsWith('http') ? path : `${API_BASE_URL}${path}`);
	if (params) {
		Object.entries(params).forEach(([key, value]) => {
			if (value !== undefined && value !== null) {
				url.searchParams.set(key, String(value));
			}
		});
	}
	return url.toString();
}

export async function getJson<T>(path: string, params?: QueryParams, init?: RequestInit): Promise<T> {
	const res = await fetch(buildUrl(path, params), {
		method: 'GET',
		headers: { 'Accept': 'application/json', ...(init?.headers || {}) },
		...init,
	});
	if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
	return res.json();
}

export async function postJson<T>(path: string, params?: QueryParams, body?: any, init?: RequestInit): Promise<T> {
	const res = await fetch(buildUrl(path, params), {
		method: 'POST',
		headers: { 'Accept': 'application/json', 'Content-Type': 'application/json', ...(init?.headers || {}) },
		body: body !== undefined ? JSON.stringify(body) : undefined,
		...init,
	});
	if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
	return res.json();
}

export async function postFormData<T>(path: string, params: QueryParams | undefined, formData: FormData, init?: RequestInit): Promise<T> {
	const res = await fetch(buildUrl(path, params), {
		method: 'POST',
		body: formData,
		headers: { 'Accept': 'application/json', ...(init?.headers || {}) },
		...init,
	});
	if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
	return res.json();
}

export function imageUrl(path: string, params?: QueryParams): string {
	return buildUrl(path, params);
}


