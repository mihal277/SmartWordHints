const path = require('path');

const CopyPlugin = require('copy-webpack-plugin');

const DIST_DIR = path.resolve(__dirname, 'dist');
const SRC_DIR = path.resolve(__dirname, 'src');
const scriptsPath = path.join(SRC_DIR, 'scripts');

const buildForChromium = process.argv.indexOf('BUILD_FOR_CHROMIUM') > -1;

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
    extensions: ['.ts', '.js'],
  },

  module: {
    rules: [
      { test: /\.tsx?$/, loader: 'ts-loader' },
      { test: /\.js$/, loader: 'source-map-loader' },
    ],
  },

  plugins: [
    new CopyPlugin({
      patterns: [
        {
          from: 'src/static',
          globOptions: {
            ignore: ['**/manifest-*.json'],
          },
        },
        {
          from: buildForChromium ? 'manifest-chromium.json' : 'manifest-firefox.json',
          to: 'manifest.json',
          context: path.resolve(SRC_DIR, 'static'),
        },
      ],
    }),
  ],
};
