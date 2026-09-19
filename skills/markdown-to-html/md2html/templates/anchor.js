function mdGithubSlug(text) {
  return String(text)
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]+/gu, '')
    .replace(/ /g, '-');
}

function mdUniqueSlug(slugs, base) {
  var original = base || 'section';
  var result = original;
  while (Object.prototype.hasOwnProperty.call(slugs, result)) {
    slugs[original] = (slugs[original] || 0) + 1;
    result = original + '-' + slugs[original];
  }
  slugs[result] = 0;
  return result;
}

function mdHeadingHtml(text, level, state) {
  state = state || { miscIdx: 0, slugs: Object.create(null) };
  if (!state.slugs) state.slugs = Object.create(null);
  var plain = String(text).replace(/<[^>]*>/g, '').trim();
  var id;
  var m = /^(\d+(?:\.\d+)*)/.exec(plain);
  if (m) {
    id = 'h-' + m[1].replace(/\./g, '-');
  } else {
    var ap = /^附录\s*([A-Z])/i.exec(plain);
    if (ap) {
      id = 'h-appendix-' + ap[1].toLowerCase();
    } else {
      state.miscIdx = (state.miscIdx || 0) + 1;
      id = 'h-misc-' + state.miscIdx;
    }
  }
  var slug = mdUniqueSlug(state.slugs, mdGithubSlug(plain));
  var escaped = slug.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  var hasSlug = new RegExp(
    '(?:\\s|\\b)(?:id|name)\\s*=\\s*["\']' + escaped + '["\']',
    'i'
  ).test(String(text));
  var extra = (!hasSlug && slug && slug !== id)
    ? '<span id="' + slug + '"></span>'
    : '';
  return '<h' + level + ' id="' + id + '">' + extra + text + '</h' + level + '>\n';
}

function mdFindHashTarget(getById, rawId) {
  var id = String(rawId || '');
  if (!id) return null;
  var target = getById(id);
  if (target) return target;
  try {
    var decoded = decodeURIComponent(id);
    if (decoded !== id) {
      target = getById(decoded);
      if (target) return target;
    }
  } catch (e) {}
  return null;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    mdGithubSlug: mdGithubSlug,
    mdHeadingHtml: mdHeadingHtml,
    mdFindHashTarget: mdFindHashTarget
  };
}
