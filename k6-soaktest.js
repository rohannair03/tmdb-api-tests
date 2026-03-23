import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '300s',
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 20 virutal users, over 5 minutes, response under 2s 
    http_req_failed: ['rate<0.01'],
  },
};

const BASE = 'https://api.themoviedb.org/3';
const KEY = __ENV.TMDB_API_KEY;

export default function () {
  if (Math.random() < 0.5) {
    const res = http.get(`${BASE}/movie/popular?api_key=${KEY}`);
    check(res, { 'status is 200': r => r.status === 200 });
    sleep(1);
    const res1 = http.get(`${BASE}/search/movie?query=Dune+Part+Two&api_key=${KEY}`);
    check(res1, { 'status is 200': r => r.status === 200 });
    sleep(1);
    const res2 = http.get(`${BASE}/tv/1396?api_key=${KEY}`);
    check(res2, { 'status is 200': r => r.status === 200 });
    sleep(1);
  } 
  else {
    const res = http.get(`${BASE}/genre/movie/list?api_key=${KEY}`);
    check(res, { 'status is 200': r => r.status === 200 });
    sleep(1);
    const res1 = http.get(`${BASE}/genre/tv/list?api_key=${KEY}`);
    check(res1, { 'status is 200': r => r.status === 200 });
    sleep(1);
    const res2 = http.get(`${BASE}/discover/movie?with_genres=28&api_key=${KEY}`);
    check(res2, { 'status is 200': r => r.status === 200 });
    sleep(1);
  }
}