# Changelog

## [0.2.0](https://github.com/davisbuilds/dojo/compare/dojo-cli-v0.1.0...dojo-cli-v0.2.0) (2026-10-30)


### ⚠ BREAKING CHANGES

* retire Vercel skills and shipping profile ([#125](https://github.com/davisbuilds/dojo/issues/125))
* Vercel skill paths and the shipping overlay are removed. Coordinate managed consumer links and declarations before merging and syncing.

### Features

* **cli:** add catalog discovery, runtime info, and version flags ([cc57a88](https://github.com/davisbuilds/dojo/commit/cc57a884f721e6948d295c7144bacd37bbf4dd22))
* **cli:** add discovery commands and automated tooling releases ([#105](https://github.com/davisbuilds/dojo/issues/105)) ([264e87c](https://github.com/davisbuilds/dojo/commit/264e87c76028386b3487a3ec830bf309fe75f6d0))
* **cli:** add focused skill checks and Codex exposure inspection ([25c14c1](https://github.com/davisbuilds/dojo/commit/25c14c12d6f5f888556eed9178a01e034628661c))
* **cli:** add focused skill checks and Codex exposure inspection ([#100](https://github.com/davisbuilds/dojo/issues/100)) ([aa9012a](https://github.com/davisbuilds/dojo/commit/aa9012a5f55982925fcc11707116cfa70990edb6))
* **cli:** make dojo directly available on PATH ([#104](https://github.com/davisbuilds/dojo/issues/104)) ([ffa7bc7](https://github.com/davisbuilds/dojo/commit/ffa7bc7aa53b5f1989882adda7f5bb567f8d4eb8))
* **cli:** support a symlinked dojo command with checkout environment selection ([794d9a8](https://github.com/davisbuilds/dojo/commit/794d9a88e9f6d2228f8d78b825c37c55b4948aae))
* **links:** validate local Markdown heading fragments ([197ebc2](https://github.com/davisbuilds/dojo/commit/197ebc2039af37656bac18cc90e537075670b3a2))
* **links:** validate local Markdown heading fragments ([#120](https://github.com/davisbuilds/dojo/issues/120)) ([ff4d31e](https://github.com/davisbuilds/dojo/commit/ff4d31e27688a0d580fef41a0864e10dd7be0fc6))
* **standardizer:** report installed skill version deltas ([e5a06ad](https://github.com/davisbuilds/dojo/commit/e5a06ad7064176cedb3bc154cf8189bff9bb2719))
* **standardizer:** report installed skill version deltas ([#122](https://github.com/davisbuilds/dojo/issues/122)) ([6739192](https://github.com/davisbuilds/dojo/commit/67391920c7f8161ce637d7e69ee7bd1c4fb6d305))


### Bug Fixes

* **catalog:** preserve literal text in embedded skill data ([e9ced05](https://github.com/davisbuilds/dojo/commit/e9ced05e9d94fb1e5402835849b2811208e8009e))
* **catalog:** preserve literal text; add frontend edge-case guidance and centralize credits ([#126](https://github.com/davisbuilds/dojo/issues/126)) ([c330233](https://github.com/davisbuilds/dojo/commit/c3302338f5fc8760198a2d9e1152ce15b8593a2f))
* **cli:** classify exposure against the selected catalog ([5ab593f](https://github.com/davisbuilds/dojo/commit/5ab593f9315fa0a7e60d36bb551d2c20e6234181))
* **cli:** compare installed skill content through directory links ([3ca8e04](https://github.com/davisbuilds/dojo/commit/3ca8e0418580b3815067cb83c172024d4da9d848))
* **cli:** compare installed skill content through directory links ([#101](https://github.com/davisbuilds/dojo/issues/101)) ([e6591e9](https://github.com/davisbuilds/dojo/commit/e6591e938d711004542691b98bedb4231121040c))
* **hooks:** select the checkout environment independently of harness PATH ([d1ae579](https://github.com/davisbuilds/dojo/commit/d1ae57972f232c24bd47558586e362b6672c0c9c))
* **links:** address final heading-fragment review findings ([492656b](https://github.com/davisbuilds/dojo/commit/492656b22df55c09de22b90c3d629b5e70d53bac))
* **links:** address six final heading-fragment review findings ([#121](https://github.com/davisbuilds/dojo/issues/121)) ([aeea176](https://github.com/davisbuilds/dojo/commit/aeea1764b31e78ec17a6ddaf68abe40dd53a7a00))
* **links:** align heading and container boundaries ([049cb1e](https://github.com/davisbuilds/dojo/commit/049cb1e47b80213ce0bc5d9355ac63aa9e9735ce))
* **links:** correct setext and underscore boundary handling ([e3b2190](https://github.com/davisbuilds/dojo/commit/e3b2190461ea648e527e19d6c7553fb46dbcca78))
* **links:** distinguish code and preceding heading blocks ([438323e](https://github.com/davisbuilds/dojo/commit/438323e0817ccce60b650de50eff9112f54da5b2))
* **links:** exclude code examples and uncertain reference headings ([eecf2c9](https://github.com/davisbuilds/dojo/commit/eecf2c95cffbc754874492ed8f473dc54faab5e8))
* **links:** handle quoted fences and encoded anchors ([6b2f15c](https://github.com/davisbuilds/dojo/commit/6b2f15cc923eb53852e5d81d48b83bed50604530))
* **links:** handle reviewed Markdown edge cases ([8605525](https://github.com/davisbuilds/dojo/commit/860552515892a50b2d42483ddd0466a89616ea84))
* **links:** preserve fence boundaries and literal link syntax ([8e2eb94](https://github.com/davisbuilds/dojo/commit/8e2eb94d25ae47a665c97246c256b1d7dbc50cbb))
* **links:** respect comment and container boundaries ([ab52168](https://github.com/davisbuilds/dojo/commit/ab52168a96e8176b7ff52d1bf1f4c9a9feaefd57))
* **profiles:** retain the standalone creator on Codex ([e280d0b](https://github.com/davisbuilds/dojo/commit/e280d0b508786d1ead02af60cc12326e02011337))
* **profiles:** retain the standalone creator on Codex ([#109](https://github.com/davisbuilds/dojo/issues/109)) ([fbb5c7e](https://github.com/davisbuilds/dojo/commit/fbb5c7e7d515c7576d8b50f34fddc7b25198b360))
* **standardizer:** decode single-line YAML version scalars ([d11a05d](https://github.com/davisbuilds/dojo/commit/d11a05dceec320dc45a3b2c4a7a3146b5676f00b))
* **standardizer:** parse version keys and compare large versions ([e86bd05](https://github.com/davisbuilds/dojo/commit/e86bd05b1f3b48848fe452c8f49a9bcee848c39a))
* **standardizer:** preserve equal normalized prerelease ordering ([0ef16c7](https://github.com/davisbuilds/dojo/commit/0ef16c71a454863269920d9b0b5eeb074bd931f3))


### Refactoring

* retire Vercel skills and shipping profile ([bf4f529](https://github.com/davisbuilds/dojo/commit/bf4f52929e096d0251c14247c1011273bc9617ac))
* retire Vercel skills and shipping profile ([#125](https://github.com/davisbuilds/dojo/issues/125)) ([80ed0fb](https://github.com/davisbuilds/dojo/commit/80ed0fb24391c462c09fb03f3e8ffbe9a5e1124e))

## Dojo CLI and tooling changelog

Release Please maintains consumer-facing CLI/tooling release notes here.
Individual skill versions and changelogs remain in `skills/<name>/`.

The initial `0.1.0` metadata is a bootstrap baseline; it does not imply a
historical release. Published releases will appear below.
