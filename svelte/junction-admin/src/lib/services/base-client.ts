import axios from 'axios';
import type { AxiosInstance } from 'axios';

export default abstract class BaseClient {
	protected readonly client: AxiosInstance;

	constructor(baseURL: string) {
		this.client = axios.create({ baseURL, withCredentials: true });
	}
}
