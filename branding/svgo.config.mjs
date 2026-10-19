export default {
  multipass: true,
  floatPrecision: 3,
  plugins: [
    { name: 'preset-default', params: { overrides: { convertPathData: { makeArcs: false }, removeViewBox: false } } },
    { name: 'prefixIds', params: { delim: '-', prefix: (_, info) => info.path.split('/').pop().replace('.svg','') } },
  ],
};
