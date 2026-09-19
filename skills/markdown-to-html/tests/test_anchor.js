#!/usr/bin/env node
'use strict';

const path = require('path');
const { mdGithubSlug, mdHeadingHtml, mdFindHashTarget } = require(
  path.join(__dirname, '../md2html/templates/anchor.js')
);

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    console.error('FAIL:', label);
    console.error('  expected:', expected);
    console.error('  actual  :', actual);
    process.exit(1);
  }
}

function assert(cond, label) {
  if (!cond) {
    console.error('FAIL:', label);
    process.exit(1);
  }
}

const cases = [
  ['1. 怎么验证', '1-怎么验证'],
  ['2. 原理', '2-原理'],
  ['2.1 正常情况', '21-正常情况'],
  ['目录 • 冻结表格标题示例', '目录--冻结表格标题示例'],
  ['5. 不要这样做', '5-不要这样做']
];

for (const [title, slug] of cases) {
  assertEqual(mdGithubSlug(title), slug, 'slug ' + title);
}

const state = { miscIdx: 0, slugs: Object.create(null) };
const html = mdHeadingHtml('1. 怎么验证', 2, state);
assert(html.indexOf('id="h-1"') !== -1, 'numeric id h-1');
assert(html.indexOf('id="1-怎么验证"') !== -1, 'github slug id on heading 1. 怎么验证');

const html21 = mdHeadingHtml('2.1 正常情况', 3, state);
assert(html21.indexOf('id="h-2-1"') !== -1, 'numeric id h-2-1');
assert(html21.indexOf('id="21-正常情况"') !== -1, 'github slug id on heading 2.1');

const ids = Object.create(null);
ids['h-1'] = { name: 'h-1' };
ids['1-怎么验证'] = { name: 'slug' };
assertEqual(mdFindHashTarget(function (id) { return ids[id] || null; }, '1-怎么验证').name, 'slug', 'resolve TOC href');

const encoded = encodeURIComponent('1-怎么验证');
assertEqual(mdFindHashTarget(function (id) { return ids[id] || null; }, encoded).name, 'slug', 'resolve percent-encoded href');

console.log('ok');
