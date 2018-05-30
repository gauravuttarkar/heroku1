const webpackMerge = require('webpack-merge');
var S3Plugin = require('webpack-s3-plugin')

const buildConfig = require('./webpack.build');

module.exports = function () {
  return webpackMerge(buildConfig(), {
    plugins: [
      new S3Plugin({
        s3Options: {
          accessKeyId: "AKIAIED2fdN5WDHUCZA",
          secretAccessKey: "F2wvLqVy2u0qxc6kqZcgAAzII+BJLgAV6k/7u",
        },
        s3UploadOptions: {
          Bucket: 'ya-manik'
        }
      })
    ]
  })
}