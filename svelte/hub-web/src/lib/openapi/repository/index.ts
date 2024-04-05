import { readFile } from "../file-handler";
import { isReference } from "../resolvers/helpers";
import type { JSONObject } from "./types";
import type * as OpenAPI from "../openapi/types";
import * as pathFns from "path";

export default class Repository {
  private readonly rootRef: string;
  private readonly spec: OpenAPI.OpenAPIObject;
  private readonly lib: Record<string, JSONObject> = {};
  private readonly refs: Record<string, unknown> = {};

  constructor(rootRef: string, specification: OpenAPI.OpenAPIObject) {
    this.rootRef = rootRef.startsWith("http")
      ? rootRef
      : pathFns.dirname(rootRef).replaceAll("\\", "/");
    this.spec = specification;
  }

  static resolveLocal<T>(root: JSONObject | object | undefined, ref: string): T {
    let obj = root;
    const parts = ref.replace("#/", "").split("/");

    parts.forEach((part) => {
      if (obj) {
        obj = obj[part.replaceAll("~1", "/") as keyof typeof obj];
      }
    });

    if (!obj) {
      throw new Error(`Broken reference: ${ref}`);
    }

    return obj as T;
  }

  static updateLocalReferences(obj: JSONObject, path: string): void {
    if (obj instanceof Array) {
      obj.forEach((inner) => this.updateLocalReferences(inner, path));

      return;
    }

    if (typeof obj === "object" && obj !== null) {
      if (typeof obj.$ref === "string" && obj.$ref.startsWith("#/")) {
        obj.$ref = `${path}${obj.$ref}`;
      }

      Object.values(obj).forEach((inner) => this.updateLocalReferences(inner, path));

      return;
    }
  }

  async resolve<T>(ref: T | OpenAPI.ReferenceObject): Promise<[resolved: T, ref?: string]> {
    if (!isReference(ref)) {
      return [ref];
    }

    if (ref.$ref.startsWith("#/")) {
      return [Repository.resolveLocal(this.spec, ref.$ref), ref.$ref];
    } else if (ref.$ref.startsWith("http")) {
      throw new Error("Not implemented: HTTP resolver");
    } else {
      const [resource, localRef] = ref.$ref.split("#/") as [string, string | undefined];
      const path = pathFns.resolve(this.rootRef, resource).replaceAll("\\", "/");

      this.lib[path] = this.lib[path] ?? (await readFile(path));

      if (localRef) {
        const obj = Repository.resolveLocal<JSONObject>(this.lib[path], localRef);

        Repository.updateLocalReferences(obj, path);

        return [obj as T, `${path}#/${localRef}`];
      }

      throw new Error(`Broken reference: ${ref.$ref}`);
    }
  }

  getRef<T>(ref: string | undefined): T | undefined {
    if (!ref) {
      return undefined;
    }

    return this.refs[ref] as T | undefined;
  }

  saveRef<T>(obj: T, ref: string | undefined): T {
    if (ref) {
      this.refs[ref] = obj;
    }

    return obj;
  }
}
