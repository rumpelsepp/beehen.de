import fs from 'fs';
import path from 'path';
import * as esbuild from 'esbuild';

const args = process.argv.slice(2);
const isWatchMode = args.includes('--watch');

// Output into Hugo's assets/ dir so Hugo Pipes can fingerprint + publish
// (cache-busting, SRI). Nothing here is referenced directly by URL.
const outdir = 'assets/gen';

async function runBuild() {
  try {
    // Chunk names carry a content hash, so every change leaves the old ones
    // behind -- start from an empty outdir so Hugo doesn't publish stale
    // chunks (it publishes everything under gen/chunks/, see
    // themes/bienensteff/layouts/_partials/head/js.html).
    fs.rmSync(outdir, { recursive: true, force: true });

    const ctx = await esbuild.context({
      // This site has no JS of its own; add a `bundle` entry pointing to
      // bundle_src/js/main.ts once it does.
      entryPoints: {
        base_bundle: path.resolve('themes/bienensteff/bundle_src/js/main.ts'),
        base_style: path.resolve('themes/bienensteff/bundle_src/css/main.css'),
        style: path.resolve('bundle_src/css/style.css'),
      },
      outdir,
      splitting: true,
      chunkNames: 'chunks/[name]-[hash]',
      bundle: true,
      // Sourcemaps only for local `--watch`; keep them out of the deployed site.
      sourcemap: isWatchMode ? 'linked' : false,
      minify: true,
      target: 'es2024',
      format: 'esm',
      logLevel: 'info',
      loader: {
        '.woff': 'file',
        '.woff2': 'file'
      },
      assetNames: '[name]',
    });

    if (isWatchMode) {
      await ctx.watch();
    } else {
      const result = await ctx.rebuild();
      console.log('Build completed successfully:', result);

      await ctx.dispose();
      process.exit(0);
    }

  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

runBuild();
