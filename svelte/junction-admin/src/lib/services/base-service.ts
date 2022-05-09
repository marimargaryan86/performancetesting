import type { AxiosInstance } from "axios";
import axios from "axios";

export default abstract class BaseService {
  protected readonly client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({ baseURL, withCredentials: true });
  }
}
