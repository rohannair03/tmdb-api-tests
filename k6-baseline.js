import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '60s',
  thresholds: {
    http_req_duration: ['p(95)<1000'],  // single user, expect under 1s
    http_req_failed: ['rate<0.05'],
  },
};

const BASE = 'https://api.themoviedb.org/3';
const KEY = __ENV.TMDB_API_KEY;

export default function () {
  const res = http.get(`${BASE}/movie/popular?api_key=${KEY}`);
  check(res, { 'status is 200': r => r.status === 200 });
  sleep(1);
}