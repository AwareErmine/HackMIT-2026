import { z } from "zod";

const fishSchema = z.object({
  id: z.string().min(1),
  volume: z.number().min(0).max(100),
});

const fishiesResponseSchema = z.object({
  fishies: z.array(fishSchema),
});

export type BackendFish = z.infer<typeof fishSchema>;

const localDevelopmentHosts = new Set(["localhost", "127.0.0.1"]);
const defaultBackendHost = localDevelopmentHosts.has(window.location.hostname)
  ? "joyce.local"
  : window.location.hostname;

export const BACKEND_URL = (
  import.meta.env.VITE_BACKEND_URL ?? `http://${defaultBackendHost}:5005`
).replace(/\/$/, "");

async function requireOk(response: Response): Promise<Response> {
  if (!response.ok) {
    throw new Error(`Backend request failed with HTTP ${response.status}`);
  }
  return response;
}

export async function getFishies(signal?: AbortSignal): Promise<BackendFish[]> {
  const response = await requireOk(
    await fetch(`${BACKEND_URL}/fishies`, { signal }),
  );
  return fishiesResponseSchema.parse(await response.json()).fishies;
}

export async function putFishVolume(id: string, volume: number): Promise<void> {
  await requireOk(
    await fetch(`${BACKEND_URL}/fishies`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, volume }),
    }),
  );
}
