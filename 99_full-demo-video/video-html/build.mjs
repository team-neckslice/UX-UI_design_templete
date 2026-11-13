// 3분 데모 영상 HTML 빌드
// 사용: node 99_full-demo-video/video-html/build.mjs
// 01~07 단계 프로토타입 HTML을 한 파일 안에 넣어(파일을 직접 열어도 동작하도록) 영상 HTML과 자막(SRT)을 만듭니다.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const outDir = join(here, '..');

const STAGES = [
  '01_tester-profile', '02_request-create', '03_group-proposal', '04_offer-accept',
  '05_test-feedback', '06_progress-result', '07_reward-history',
];
// srcdoc 안에서는 history.replaceState 가 막히므로(주소 #번호 갱신) 오류 없이 넘어가도록 감쌉니다.
const SHIM = '<script>(function(){var r=history.replaceState;history.replaceState=function(){try{return r.apply(history,arguments)}catch(e){}}})()</script>';
// 플랫폼 이름을 NeckSlice로 표시(원본 프로토타입 파일은 그대로 둠). 받침에 맞춰 조사도 바꿉니다.
const rename = h => h.replace(/© 2028 PlayFit · 데모 화면\(가상 데이터\)/g, '© 2026 NeckSlice').replace(/PlayFit/g, 'NeckSlice').replace(/플레이핏이/g, 'NeckSlice가').replace(/플레이핏은/g, 'NeckSlice는')
  .replace(/플레이핏을/g, 'NeckSlice를').replace(/플레이핏과/g, 'NeckSlice와').replace(/플레이핏으로/g, 'NeckSlice로').replace(/플레이핏/g, 'NeckSlice');
const protos = STAGES.map(s => rename(readFileSync(join(root, s, 'prototypes', `${s}_v1.html`), 'utf8')).replace(/<head>/i, m => m + SHIM));
const scenes = JSON.parse(readFileSync(join(here, 'scenes.json'), 'utf8'));
// 배경음악: mp3를 HTML 안에 넣어 파일 하나로 재생되게 합니다.
let music = '';
if (scenes.music?.file) {
  try { music = 'data:audio/mpeg;base64,' + readFileSync(join(here, scenes.music.file)).toString('base64'); }
  catch { console.warn(`! 음악 파일을 찾지 못했습니다: ${scenes.music.file}`); }
}
const template = readFileSync(join(here, 'template.html'), 'utf8');

const safe = v => JSON.stringify(v).replace(/<\/(script)/gi, '<\\/$1').replace(/<!--/g, '<\\!--');
const html = template.replace('/*__DATA__*/', () => `const SCENES=${safe(scenes)};\nconst PROTOS=${safe(protos)};
const MUSIC=${safe(music)};`);
writeFileSync(join(outDir, 'NeckSlice_demo_3min.html'), html);

// 자막(SRT) — 영상 편집 프로그램에 바로 불러올 수 있게
const subs = [];
let t = 0;
const push = (list, base, dur) => list.forEach((s, i, a) => subs.push([base + s.t, base + (i + 1 < a.length ? a[i + 1].t : dur), s.text]));
push(scenes.intro.subs, 0, scenes.intro.dur); t = scenes.intro.dur;
for (const st of scenes.stages) {
  subs.push([t, t + st.card.dur, st.card.sub]); t += st.card.dur;
  for (const sc of st.screens) {
    if (sc.subs) push(sc.subs, t, sc.dur); else subs.push([t, t + sc.dur, sc.sub]);
    t += sc.dur;
  }
}
push(scenes.outro.subs, t, scenes.outro.dur); t += scenes.outro.dur;
const tc = x => {
  const ms = Math.round(x * 1000);
  const p = (n, w = 2) => String(n).padStart(w, '0');
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`;
};
writeFileSync(join(outDir, 'NeckSlice_demo_3min.srt'),
  subs.map(([s, e, text], i) => `${i + 1}\n${tc(s)} --> ${tc(e)}\n${text}\n`).join('\n'));

console.log(`total ${t.toFixed(2)}s · ${subs.length} subtitles · ${(html.length / 1024).toFixed(0)}KB`);
if (Math.abs(t - 180) > 0.01) console.warn(`! 전체 길이가 180초가 아닙니다: ${t}s`);
