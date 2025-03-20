async function  fetchSonglist(query) {
	const response = await fetch(`/api/search/songs?q=${encodeURIComponent(query)}`);
	const data = await response.json();
    return data;
}
async function fetchGlobalSongs() {
	const resp = await fetch('/api/global');
    return await resp.json();
}
async function fetchTrendingsongs() {
	const trend =await fetch('/api/trending');
	return await trend.json()
}
