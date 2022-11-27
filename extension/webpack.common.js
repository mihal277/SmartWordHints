const path = require('path');

const CopyPlugin = require('copy-webpack-plugin');

const DIST_DIR = path.resolve(__dirname, 'dist');
const SRC_DIR = path.resolve(__dirname, 'src');
const scriptsPath = path.join(SRC_DIR, 'scripts');

module.exports = {
  entry: {
    background: path.join(scriptsPath, 'background.ts'),
    main: path.join(scriptsPath, 'main.ts'),
    popup: path.join(scriptsPath, 'popup.ts'),
  },

  output: {
    filename: 'scripts/[name].js',
    path: DIST_DIR,
    clean: true,
  },

  resolve: {
    extensions: [".ts", ".js"],
  },

  module: {
    rules: [
      { test: /\.tsx?$/, loader: "ts-loader" },
      { test: /\.js$/, loader: "source-map-loader" },
    ],
  },

  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'src/static' },
        {
          from: 'node_modules/webextension-polyfill/dist/browser-polyfill.js',
          to: 'scripts/browser-polyfill.js',
        },
      ],
    }),
  ],
};
