#!/usr/bin/env bun
import {
  mkdtemp,
  mkdir,
  rm,
  cp,
  readFile,
  writeFile,
  readdir,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dir, "..");
const base = process.env.DOKPLOY_URL || "https://dokploy.hypcat.net";
const site = "https://energy-plus-quest.hypcat.net/";
const applicationId = "pfnvsqxv0r5pqE-Pbr8qi";
const sshHost = process.env.DOKPLOY_SSH_HOST || "infra-admin";
const dryRun = process.argv.includes("--dry-run");
if (process.argv.slice(2).some((arg) => arg !== "--dry-run"))
  throw Error("Usage: bun scripts/deploy-dokploy.mjs [--dry-run]");
await mkdir(join(root, ".tmp-work"), { recursive: true });
const lock = join(root, ".tmp-work/deploy.lock");
try {
  await mkdir(lock);
} catch {
  throw Error(
    "Deployment lock exists. Check the running deployment before removing .tmp-work/deploy.lock.",
  );
}
let staging;
try {
  let key = process.env.DOKPLOY_API_KEY;
  if (!key) {
    const secrets = await readFile(
      process.env.DOKPLOY_SECRETS_FILE ||
        "/home/michael/Github/infra/secrets.local.md",
      "utf8",
    );
    key = secrets
      .match(/^DOKPLOY_API_KEY=(.+)$/m)?.[1]
      ?.trim()
      .replace(/^["']|["']$/g, "");
  }
  if (!key) throw Error("Set DOKPLOY_API_KEY or DOKPLOY_SECRETS_FILE.");
  async function api(route, body) {
    const response = await fetch(`${base}/api/${route}`, {
      method: body ? "POST" : "GET",
      headers: {
        "x-api-key": key,
        ...(body && !(body instanceof FormData)
          ? { "Content-Type": "application/json" }
          : {}),
      },
      body:
        body instanceof FormData
          ? body
          : body
            ? JSON.stringify(body)
            : undefined,
      signal: AbortSignal.timeout(120000),
    });
    if (!response.ok)
      throw Error(
        `Dokploy ${route.split("?")[0]} returned ${response.status}; no automatic retry.`,
      );
    return response.json();
  }
  const schema = await api("settings.getOpenApiDocument");
  for (const [route, method] of [
    ["application.one", "get"],
    ["domain.byApplicationId", "get"],
    ["deployment.all", "get"],
    ["application.update", "post"],
    ["application.deploy", "post"],
  ]) {
    if (!schema.paths[`/${route}`]?.[method])
      throw Error(`Live Dokploy API lacks ${route}.`);
  }
  const app = await api(`application.one?applicationId=${applicationId}`);
  const domains = await api(
    `domain.byApplicationId?applicationId=${applicationId}`,
  );
  if (
    app.name !== "energy-plus-quest" ||
    app.appName !== "app-connect-1080p-application-tsm189" ||
    app.buildType !== "dockerfile" ||
    app.dockerfile !== "Containerfile" ||
    app.serverId !== null ||
    app.buildServerId !== null ||
    !domains.some((domain) => domain.host === new URL(site).hostname)
  )
    throw Error("Application, build configuration, server or domain mismatch.");
  if (!["git", "drop"].includes(app.sourceType))
    throw Error("Unexpected source provider.");
  const before = await api(`deployment.all?applicationId=${applicationId}`);
  if (
    before.some((deployment) =>
      ["running", "queued", "pending"].includes(deployment.status),
    ) ||
    app.applicationStatus === "running"
  )
    throw Error("An application deployment is already active.");
  const queue = await api("deployment.queueList");
  if (JSON.stringify(queue).includes(applicationId))
    throw Error("Application is already queued.");
  await writeFile(
    join(root, ".tmp-work/dokploy-before.json"),
    JSON.stringify(
      {
        applicationId,
        sourceType: app.sourceType,
        autoDeploy: app.autoDeploy,
        dropBuildPath: app.dropBuildPath,
        customGitUrl: app.customGitUrl,
        customGitBranch: app.customGitBranch,
        latestDeploymentId: before[0]?.deploymentId,
      },
      null,
      2,
    ),
    { mode: 0o600 },
  );
  console.log("Building current local files…");
  const build = Bun.spawn(["sh", "scripts/package-static.sh", "--stage-only"], {
    cwd: root,
    stdout: "inherit",
    stderr: "inherit",
  });
  if (await build.exited)
    throw Error("Build failed; production was not changed.");
  staging = await mkdtemp(join(tmpdir(), "energy-deploy-"));
  const reviewDirectories = new Set();
  let includeAllReview = false;
  for (const entry of await readdir(join(root, "dist/assets"))) {
    if (!/\.(js|css)$/.test(entry)) continue;
    const bundle = await readFile(join(root, "dist/assets", entry), "utf8");
    const references = [...bundle.matchAll(/review\/([A-Za-z0-9_-]+)\//g)];
    if (references.length !== [...bundle.matchAll(/review\//g)].length)
      includeAllReview = true;
    for (const match of references) reviewDirectories.add(match[1]);
  }
  await cp(join(root, "dist"), join(staging, "dist"), {
    recursive: true,
    filter: (source) => {
      const prefix = join(root, "dist/review") + "/";
      return (
        !source.startsWith(prefix) ||
        includeAllReview ||
        reviewDirectories.has(source.slice(prefix.length).split("/")[0])
      );
    },
  });
  await cp(join(root, "Containerfile"), join(staging, "Containerfile"));
  const parent = `/etc/dokploy/applications/${app.appName}`;
  async function command(args, stdin) {
    const process = Bun.spawn(args, {
      cwd: root,
      stdout: "inherit",
      stderr: "inherit",
      stdin,
    });
    if (await process.exited)
      throw Error(
        `Deployment transport failed: ${args[0]}. Inspect state before retrying.`,
      );
  }
  await command([
    "ssh",
    "-o",
    "BatchMode=yes",
    sshHost,
    `test -d ${parent}/code && command -v rsync >/dev/null`,
  ]);
  if (dryRun) {
    console.log(
      "Dry run passed: correct Dokploy application/domain, no active deployment, local build and SSH transport ready. Production unchanged.",
    );
  } else {
    const release = new Date().toISOString().replace(/[^0-9]/g, "");
    const incoming = `${parent}/incoming-${release}`;
    console.log("Uploading changed data over SSH…");
    await command([
      "ssh",
      "-o",
      "BatchMode=yes",
      sshHost,
      `command -v rsync >/dev/null && mkdir ${incoming} && cp -a --reflink=auto ${parent}/code/. ${incoming}/`,
    ]);
    await command([
      "rsync",
      "-az",
      "--delete",
      "--no-whole-file",
      "-e",
      "ssh -o BatchMode=yes",
      `${staging}/`,
      `${sshHost}:${incoming}/`,
    ]);
    await command([
      "ssh",
      "-o",
      "BatchMode=yes",
      sshHost,
      `test -f ${incoming}/dist/index.html && test -f ${incoming}/Containerfile`,
    ]);
    await api("application.update", {
      applicationId,
      sourceType: "drop",
      autoDeploy: false,
      dropBuildPath: "/",
    });
    await command([
      "ssh",
      "-o",
      "BatchMode=yes",
      sshHost,
      `set -e; mv ${parent}/code ${parent}/code-before-${release}; if ! mv ${incoming} ${parent}/code; then mv ${parent}/code-before-${release} ${parent}/code; exit 1; fi`,
    ]);
    console.log(`Previous build preserved at ${parent}/code-before-${release}`);
    await api("application.deploy", {
      applicationId,
      title: `Local build ${release}`,
      description:
        "Current local working tree, uploaded over SSH; previous code directory preserved.",
    });
    const previous = new Set(
      before.map((deployment) => deployment.deploymentId),
    );
    const deadline = Date.now() + 10 * 60 * 1000;
    let completed;
    let lastStatus;
    while (Date.now() < deadline) {
      const deployments = await api(
        `deployment.all?applicationId=${applicationId}`,
      );
      const current = deployments.find(
        (deployment) => !previous.has(deployment.deploymentId),
      );
      if (current) {
        if (lastStatus !== current.status)
          console.log(`Deployment ${current.deploymentId}: ${current.status}`);
        lastStatus = current.status;
        if (current.status === "error")
          throw Error(
            `Deployment ${current.deploymentId} failed. Inspect its logs in Dokploy.`,
          );
        if (current.status === "done") {
          completed = current;
          break;
        }
      }
      await Bun.sleep(3000);
    }
    if (!completed)
      throw Error(
        "Deployment did not finish within 10 minutes. Check Dokploy before retrying.",
      );
    const expected = await readFile(join(staging, "dist/index.html"));
    let verified = false;
    for (let attempt = 0; attempt < 30; attempt++) {
      const response = await fetch(
        `${site}?deploy=${encodeURIComponent(completed.deploymentId)}`,
        { cache: "no-store", signal: AbortSignal.timeout(15000) },
      );
      if (
        response.ok &&
        expected.equals(Buffer.from(await response.arrayBuffer()))
      ) {
        verified = true;
        break;
      }
      await Bun.sleep(2000);
    }
    if (!verified)
      throw Error(
        "Dokploy finished, but public HTML does not match the uploaded build.",
      );
    const html = expected.toString();
    const assets = [
      ...html.matchAll(/(?:src|href)="(\.\/assets\/[^"?]+\.(?:js|css))"/g),
    ].map((match) => match[1]);
    if (!assets.some((asset) => asset.endsWith(".js")))
      throw Error("No production JavaScript asset found.");
    for (const asset of assets) {
      const response = await fetch(new URL(asset, site), {
        cache: "no-store",
        signal: AbortSignal.timeout(30000),
      });
      const local = await readFile(join(staging, "dist", asset));
      if (
        !response.ok ||
        !local.equals(Buffer.from(await response.arrayBuffer()))
      )
        throw Error(`Public asset does not match: ${asset}`);
    }
    await writeFile(
      join(root, ".tmp-work/dokploy-last-deployment.json"),
      JSON.stringify(
        {
          deploymentId: completed.deploymentId,
          site,
          verifiedAt: new Date().toISOString(),
          assets,
        },
        null,
        2,
      ),
    );
    console.log(`Verified current local build at ${site}`);
  }
} finally {
  if (staging) await rm(staging, { recursive: true, force: true });
  await rm(lock, { recursive: true, force: true });
}
