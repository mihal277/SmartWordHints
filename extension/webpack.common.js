const path = require('path');

const CopyPlugin = require('copy-webpack-plugin');

const DIST_DIR = path.resolve(__dirname, 'dist');
const SRC_DIR = path.resolve(__dirname, 'src');
const scriptsPath = path.join(SRC_DIR, 'scripts');

module.exports = {
  entry: {
    background: path.join(scriptsPath, 'background.js'),
    main: path.join(scriptsPath, 'main.js'),
    popup: path.join(scriptsPath, 'popup.js'),
  },
  output: {
    filename: 'scripts/[name].js',
    path: DIST_DIR,
    clean: true,
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
