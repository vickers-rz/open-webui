// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
import type { i18n } from 'i18next';
import type { Writable } from 'svelte/store';

declare global {
	const APP_VERSION: string;
	const APP_BUILD_HASH: string;
	const google: any;

	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface Platform {}
	}
}

declare module 'svelte' {
	function getContext(key: 'i18n'): Writable<i18n>;
}

export {};
