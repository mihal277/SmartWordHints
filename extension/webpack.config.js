const path = require('path');

const webpack = require('webpack');
const CopyPlugin = require('copy-webpack-plugin');

const DIST_DIR = path.resolve(__dirname, 'dist');
const SRC_DIR = path.resolve(__dirname, 'src');
const scriptsPath = path.join(SRC_DIR, 'scripts');

module.exports = {
  entry: {
    background: path.join(scriptsPath, 'background.js'),
    main: path.join(scriptsPath, 'main.js'),
    popup: path.join(scriptsPath, 'popup.js'),
    browser_polyfill: {
      import: path.join(scriptsPath, 'browser-polyfill.min.js'),
      filename: 'scripts/browser-polyfill.min.js',
    },
  },
  output: {
    filename: 'scripts/[name].js',
    path: DIST_DIR,
    clean: true,
  },
  // module: {
  //   rules: [
  //     { test: /\.js$/, exclude: /node_modules/, use: 'babel-loader' },
  //   ],
  // },
  resolve: {
    fallback: {
      buffer: require.resolve('buffer'),
    },
  },
  mode: 'none',
  plugins: [
    new CopyPlugin({
      patterns: [{ from: 'src/static' }],
    }),
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
    }),
  ],
};
