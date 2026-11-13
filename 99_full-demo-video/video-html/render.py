"""3분 데모 HTML을 MP4로 렌더링합니다.

사용: python 99_full-demo-video/video-html/render.py [--fps 30] [--start 0] [--end 180] [--out 파일.mp4]
필요: Python Playwright(chromium), ffmpeg

화면을 실시간으로 녹화하지 않고, 페이지의 시간을 한 프레임씩 직접 넘기며 캡처하므로
컴퓨터 속도와 관계없이 끊김 없는 1920×1080 영상이 나옵니다. 배경음악은 ffmpeg로 입힙니다.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
OUT_DIR = HERE.parent
PAGE = OUT_DIR / 'NeckSlice_demo_3min.html'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--out', default=str(OUT_DIR / 'NeckSlice_demo_3min.mp4'))
    ap.add_argument('--frames', help='이 폴더에 지정 시점의 PNG만 저장(점검용)')
    ap.add_argument('--at', default='', help='--frames와 함께: 쉼표로 구분한 초')
    a = ap.parse_args()

    scenes = json.loads((HERE / 'scenes.json').read_text(encoding='utf-8'))
    music = scenes.get('music') or {}
    music_path = (HERE / music['file']).resolve() if music.get('file') else None

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required', '--hide-scrollbars'])
        page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
        page.goto(PAGE.as_uri() + '?render')
        page.wait_for_function("window.DEMO && !document.getElementById('stage').classList.contains('loading')", timeout=60000)
        page.evaluate('document.fonts.ready')
        page.evaluate('DEMO.renderStart()')
        total = page.evaluate('DEMO.TOTAL')
        end = min(a.end if a.end is not None else total, total)

        if a.frames:
            out = pathlib.Path(a.frames)
            out.mkdir(parents=True, exist_ok=True)
            ts = sorted(float(x) for x in a.at.split(',') if x)
            step = 1 / a.fps
            v = 0.0
            for t in ts:
                while v + step <= t:
                    v += step
                    page.evaluate(f'DEMO.renderTo({v})')
                page.evaluate(f'DEMO.renderTo({t})')
                v = t
                page.screenshot(path=str(out / f'frame_{t:06.2f}.png'))
            browser.close()
            print('saved', len(ts), 'frames to', out)
            return

        n0, n1 = round(a.start * a.fps), round(end * a.fps)
        cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
               '-f', 'image2pipe', '-framerate', str(a.fps), '-c:v', 'mjpeg', '-i', '-']
        if music_path and music_path.exists() and a.start == 0:
            fade = float(music.get('fadeOut', 3))
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                        str(music_path)], capture_output=True, text=True).stdout.strip() or end)
            fade_st = max(0.0, min(dur, end) - fade)
            cmd += ['-i', str(music_path), '-filter_complex',
                    f'[1:a]atrim=0:{end},afade=t=in:st=0:d=0.6,afade=t=out:st={fade_st:.3f}:d={fade},apad=whole_dur={end}[a]',
                    '-map', '0:v', '-map', '[a]', '-c:a', 'aac', '-b:a', '192k']
        cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-r', str(a.fps), '-movflags', '+faststart', a.out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        # 시작 지점까지 시간을 넘김(프레임 단위로 넘겨야 클릭·스크롤이 순서대로 일어남)
        for i in range(0, n0):
            page.evaluate(f'DEMO.renderTo({i / a.fps})')
        t0 = time.time()
        for i in range(n0, n1):
            page.evaluate(f'DEMO.renderTo({i / a.fps})')
            ff.stdin.write(page.screenshot(type='jpeg', quality=95))
            if (i - n0) % (a.fps * 5) == 0:
                done = i - n0 + 1
                eta = (time.time() - t0) / done * (n1 - i)
                print(f'{i / a.fps:6.1f}s / {end:.0f}s  (남은 시간 약 {eta / 60:.1f}분)', flush=True)
        ff.stdin.close()
        code = ff.wait()
        missed = page.evaluate('DEMO.missed')
        browser.close()
    if missed:
        print('! 실패한 클릭:', missed)
    print('done' if code == 0 else f'ffmpeg 오류 {code}', a.out)
    sys.exit(code)


if __name__ == '__main__':
    main()
