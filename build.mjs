import path from 'path';
import * as esbuild from 'esbuild';

const args = process.argv.slice(2);
const isWatchMode = args.includes('--watch');

async function runBuild() {
  try {
    const ctx = await esbuild.context({
      entryPoints: {
        base_bundle: path.resolve('themes/bienensteff/bundle_src/js/main.ts'),
        bundle: path.resolve('bundle_src/js/main.ts'),
        base_style: path.resolve('themes/bienensteff/bundle_src/css/main.css'),
        style: path.resolve('bundle_src/css/style.css'),
      },
      // Output into Hugo's assets/ dir so Hugo Pipes can fingerprint + publish
      // (cache-busting, SRI). Nothing here is referenced directly by URL.
      outdir: 'assets/gen',
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
