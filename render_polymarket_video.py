import os
import sys
import wave
import struct
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import win32com.client
import imageio_ffmpeg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "video_audio_poly")
PUBLIC_VIDEOS = os.path.join(BASE_DIR, "public", "videos")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(PUBLIC_VIDEOS, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using FFmpeg: {FFMPEG_EXE}")

WIDTH = 1280
HEIGHT = 720
FPS = 15

# Color Palette
BG_DARK = (6, 10, 18)
PANEL_BG = (13, 20, 36)
PANEL_BORDER = (28, 42, 65)
CYAN_ACCENT = (0, 229, 255)
GREEN_ACCENT = (0, 230, 118)
RED_ACCENT = (255, 23, 68)
GOLD_ACCENT = (255, 215, 0)
PURPLE_ACCENT = (139, 92, 246)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
TEXT_DARK = (15, 23, 42)

# Load System Fonts
FONT_TITLE = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 32)
FONT_SUBTITLE = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 22)
FONT_HEADING = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 19)
FONT_BODY = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 16)
FONT_BODY_BOLD = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 16)
FONT_SMALL = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 13)
FONT_MONO = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 14)
FONT_MONO_BOLD = ImageFont.truetype("C:\\Windows\\Fonts\\consolab.ttf", 17)
FONT_SUBTITLE_TXT = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 19)

CHAPTER_DEFS = [
    {
        "id": 0,
        "title": "CH 1: OVERVIEW & 5-MIN MARKETS",
        "url": "https://polymarket.com/event/btc-updown-5m",
        "lines": [
            "Welcome to Polymarket BTC 5-Minute Live Predictor and Sniper Pro.",
            "Polymarket binary prediction markets allow traders to predict whether Bitcoin price will settle above or below a strike price within a five-minute epoch.",
            "Most retail participants lose money by guessing, reacting emotionally, or relying on lagging chart indicators.",
            "Our quantitative sniper system brings institutional algorithmic analysis directly into your browser with sub-second execution."
        ]
    },
    {
        "id": 1,
        "title": "CH 2: LIVE BINANCE TICK BRIDGE",
        "url": "https://polymarket.com/event/btc-updown-5m#feed",
        "lines": [
            "The foundation of our precision is a high-speed WebSocket connection directly to Binance BTC USDT spot order flow.",
            "Polymarket relies on oracle settlement benchmarks that closely follow real-time Binance spot pricing.",
            "By calculating price-to-beat delta in basis points with zero lag, you see market inflections seconds before crowd odds adjust.",
            "Every tick updates live on your floating HUD with instant visual and directional momentum feedback."
        ]
    },
    {
        "id": 2,
        "title": "CH 3: 16-PILLAR QUANT CONFLUENCE",
        "url": "https://polymarket.com/event/btc-updown-5m#quant",
        "lines": [
            "Unlike simple indicators, our quant engine simultaneously computes sixteen separate mathematical algorithms across four distinct market clusters.",
            "Cluster A measures trend velocity using Quad Exponential Moving Averages, SuperTrend, ADX, and Linear Regression slope.",
            "Cluster B synthesizes oscillator cycles with Dual RSI, Full Stochastic, True MACD, and Commodity Channel Index.",
            "Clusters C and D track volatility squeezes via Bollinger Bands and Keltner Channels, alongside real-time Volume Delta order flow."
        ]
    },
    {
        "id": 3,
        "title": "CH 4: LATE-ROUND SNIPER & MISPRICING",
        "url": "https://polymarket.com/event/btc-updown-5m#sniper",
        "lines": [
            "The most profitable opportunities occur in the final sixty seconds of each five-minute round.",
            "When Bitcoin is safely above the strike lock with high volatility exhaustion, the probability of closing UP exceeds ninety percent.",
            "The sniper engine calculates fair mathematical odds and compares them directly with the Polymarket order book.",
            "If fair odds are ninety-two percent while Polymarket is offering shares at sixty cents, you have a massive thirty-two percent asymmetric edge."
        ]
    },
    {
        "id": 4,
        "title": "CH 5: LIVE FLOATING HUD & 1-CLICK SNIPING",
        "url": "https://polymarket.com/event/btc-updown-5m#execution",
        "lines": [
            "The extension injects a lightweight, customizable HUD directly onto polymarket.com without obscuring your view.",
            "When high-conviction sniper conditions align, an audio alert fires and the action card flashes strong conviction.",
            "Clicking Buy Yes or Buy No instantly targets the exact Polymarket order ticket, scrolls to the button, and illuminates the trade.",
            "This reduces execution friction to under two hundred milliseconds, ensuring you secure optimal odds before the round closes."
        ]
    },
    {
        "id": 5,
        "title": "CH 6: LICENSE ACTIVATION & PORTAL",
        "url": "https://algo-trading-portal.onrender.com",
        "lines": [
            "Polymarket BTC 5M Sniper Pro is available for a one-time lifetime payment of just ten dollars USDT.",
            "You can activate immediately with your TRC20 or BEP20 transaction hash, or paste your license key from our official portal.",
            "You can also choose our Pro Trader Dual Bundle, which gives you lifetime access to both Polymarket and Pocket Option extensions for just eighteen dollars.",
            "Download your copy today, activate your lifetime key, and experience institutional quantitative trading on Polymarket."
        ]
    }
]

def generate_voice_clips():
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = -1
    speaker.Volume = 100
    
    clip_info = []
    print("Generating speech audio tracks...")
    for ch in CHAPTER_DEFS:
        ch_id = ch["id"]
        for line_idx, line_text in enumerate(ch["lines"]):
            filename = f"poly_ch{ch_id}_line{line_idx}.wav"
            filepath = os.path.join(AUDIO_DIR, filename)
            
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(filepath, 3, False)
            speaker.AudioOutputStream = stream
            speaker.Speak(line_text)
            stream.Close()
            
            with wave.open(filepath, "rb") as wf:
                dur = wf.getnframes() / float(wf.getframerate())
                
            clip_info.append({
                "chapter_id": ch_id,
                "chapter_title": ch["title"],
                "url": ch["url"],
                "text": line_text,
                "filepath": filepath,
                "raw_dur": dur
            })
            print(f"  [Ch {ch_id}] {filename} ({dur:.2f}s): {line_text[:40]}...")
            
    return clip_info

def build_master_audio(clip_info):
    master_wav_path = os.path.join(AUDIO_DIR, "polymarket_master_audio.wav")
    with wave.open(clip_info[0]["filepath"], "rb") as first_wf:
        nchannels = first_wf.getnchannels()
        sampwidth = first_wf.getsampwidth()
        framerate = first_wf.getframerate()
        
    timeline = []
    current_time = 0.5
    audio_frames = bytearray()
    
    pre_samples = int(0.5 * framerate)
    audio_frames.extend(b"\x00" * (pre_samples * nchannels * sampwidth))
    
    for clip in clip_info:
        with wave.open(clip["filepath"], "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            
        dur = clip["raw_dur"]
        timeline.append({
            "chapter_id": clip["chapter_id"],
            "chapter_title": clip["chapter_title"],
            "url": clip["url"],
            "text": clip["text"],
            "start": current_time,
            "end": current_time + dur,
            "dur": dur
        })
        
        audio_frames.extend(frames)
        current_time += dur
        
        pause_samples = int(0.65 * framerate)
        audio_frames.extend(b"\x00" * (pause_samples * nchannels * sampwidth))
        current_time += 0.65
        
    outro_samples = int(1.5 * framerate)
    audio_frames.extend(b"\x00" * (outro_samples * nchannels * sampwidth))
    current_time += 1.5
    
    with wave.open(master_wav_path, "wb") as out_wf:
        out_wf.setnchannels(nchannels)
        out_wf.setsampwidth(sampwidth)
        out_wf.setframerate(framerate)
        out_wf.writeframes(audio_frames)
        
    print(f"\nMaster Audio Track: {master_wav_path} ({current_time:.2f}s total)")
    return master_wav_path, timeline, current_time

def draw_top_browser_bar(draw, url, chapter_title, current_sec, total_sec):
    draw.rectangle([(0, 0), (WIDTH, 60)], fill=(4, 7, 14))
    draw.line([(0, 60), (WIDTH, 60)], fill=CYAN_ACCENT, width=1)
    
    # Window dots
    draw.ellipse([(16, 24), (28, 36)], fill=(255, 95, 87))
    draw.ellipse([(34, 24), (46, 36)], fill=(254, 188, 46))
    draw.ellipse([(52, 24), (64, 36)], fill=(39, 201, 63))
    
    # Brand logo pill
    draw.rounded_rectangle([(76, 14), (290, 46)], radius=6, fill=(15, 23, 42), outline=CYAN_ACCENT, width=1)
    draw.text((86, 21), "⚡ POLYMARKET SNIPER", fill=CYAN_ACCENT, font=FONT_BODY_BOLD)
    
    # Simulated browser address bar
    draw.rounded_rectangle([(305, 14), (910, 46)], radius=6, fill=(11, 16, 29), outline=(40, 50, 70), width=1)
    draw.text((318, 21), "🔒", fill=GREEN_ACCENT, font=FONT_SMALL)
    draw.text((342, 21), url, fill=TEXT_MUTED, font=FONT_MONO)
    
    # Active Chapter badge
    draw.rounded_rectangle([(925, 14), (1135, 46)], radius=6, fill=(20, 30, 50), outline=CYAN_ACCENT, width=1)
    draw.text((935, 21), chapter_title[:23], fill=CYAN_ACCENT, font=FONT_SMALL)
    
    # Timecode
    cur_m, cur_s = int(current_sec // 60), int(current_sec % 60)
    tot_m, tot_s = int(total_sec // 60), int(total_sec % 60)
    tc_str = f"{cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}"
    draw.text((1150, 21), tc_str, fill=TEXT_WHITE, font=FONT_MONO_BOLD)

def draw_subtitle_bar(draw, active_subtitle, active_chapter_title):
    draw.rectangle([(0, 620), (WIDTH, 720)], fill=(3, 6, 12))
    draw.line([(0, 620), (WIDTH, 620)], fill=CYAN_ACCENT, width=2)
    
    draw.text((24, 636), "🔊", fill=CYAN_ACCENT, font=FONT_SUBTITLE)
    draw.text((68, 630), active_chapter_title, fill=CYAN_ACCENT, font=FONT_SMALL)
    
    txt = active_subtitle if active_subtitle else "..."
    if len(txt) > 85:
        split_idx = txt.rfind(" ", 0, 85)
        if split_idx == -1: split_idx = 80
        line1 = txt[:split_idx]
        line2 = txt[split_idx:].strip()
        draw.text((68, 650), line1, fill=TEXT_WHITE, font=FONT_SUBTITLE_TXT)
        draw.text((68, 678), line2, fill=TEXT_WHITE, font=FONT_SUBTITLE_TXT)
    else:
        draw.text((68, 656), txt, fill=TEXT_WHITE, font=FONT_SUBTITLE_TXT)

def draw_floating_hud(draw, t, spot_price=75420.50, strike=75280.00, remaining_s=45, conf=92):
    # Floating HUD Card at right side (x: 800 to 1240, y: 80 to 590)
    hx, hy, hw, hh = 800, 80, 440, 510
    draw.rounded_rectangle([(hx, hy), (hx + hw, hy + hh)], radius=14, fill=PANEL_BG, outline=CYAN_ACCENT, width=2)
    
    # HUD Header
    draw.rounded_rectangle([(hx, hy), (hx + hw, hy + 45)], radius=14, fill=(10, 17, 32), outline=PANEL_BORDER, width=1)
    draw.text((hx + 16, hy + 12), "⚡ BTC 5M SNIPER", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
    draw.rounded_rectangle([(hx + 175, hy + 10), (hx + 225, hy + 34)], radius=10, fill=(0, 229, 255, 40), outline=CYAN_ACCENT, width=1)
    draw.text((hx + 185, hy + 13), "PRO", fill=CYAN_ACCENT, font=FONT_SMALL)
    
    # Live WS Dot
    dot_color = GREEN_ACCENT if int(t * 2) % 2 == 0 else CYAN_ACCENT
    draw.ellipse([(hx + hw - 85, hy + 18), (hx + hw - 75, hy + 28)], fill=dot_color)
    draw.text((hx + hw - 70, hy + 15), "LIVE WS", fill=TEXT_MUTED, font=FONT_SMALL)
    
    # Row 1: Spot Price & Strike Lock
    cy = hy + 55
    draw.text((hx + 16, cy), "SPOT (BINANCE)", fill=TEXT_MUTED, font=FONT_SMALL)
    draw.text((hx + 240, cy), "STRIKE LOCK", fill=TEXT_MUTED, font=FONT_SMALL)
    
    tick_flash = GREEN_ACCENT if int(t * 3) % 2 == 0 else TEXT_WHITE
    draw.text((hx + 16, cy + 18), f"${spot_price:,.2f}", fill=tick_flash, font=FONT_TITLE)
    draw.text((hx + 240, cy + 18), f"${strike:,.2f}", fill=GOLD_ACCENT, font=FONT_TITLE)
    
    delta = spot_price - strike
    bps = (delta / strike) * 10000
    delta_str = f"▲ +${delta:.2f} ({bps:.1f} bps)" if delta >= 0 else f"▼ -${abs(delta):.2f} ({bps:.1f} bps)"
    delta_col = GREEN_ACCENT if delta >= 0 else RED_ACCENT
    draw.text((hx + 16, cy + 54), delta_str, fill=delta_col, font=FONT_BODY_BOLD)
    
    # Timer & Round
    draw.text((hx + 240, cy + 54), f"EPOCH: 00:{remaining_s:02d}", fill=CYAN_ACCENT, font=FONT_BODY_BOLD)
    
    # Progress Bar
    p_pct = max(0.05, remaining_s / 300.0)
    draw.rounded_rectangle([(hx + 16, cy + 80), (hx + hw - 16, cy + 86)], radius=3, fill=(20, 30, 48))
    draw.rounded_rectangle([(hx + 16, cy + 80), (hx + 16 + int((hw - 32) * p_pct), cy + 86)], radius=3, fill=CYAN_ACCENT)
    
    # Action Banner Card
    ay = cy + 98
    draw.rounded_rectangle([(hx + 16, ay), (hx + hw - 16, ay + 68)], radius=10, fill=(0, 230, 118, 30), outline=GREEN_ACCENT, width=2)
    draw.text((hx + 28, ay + 10), "⚡ HIGH CONVICTION: CALL UP (YES)", fill=GREEN_ACCENT, font=FONT_HEADING)
    draw.text((hx + 28, ay + 38), f"Late-Round Sniper Active • Conf: {conf}% • Edge: +32%", fill=TEXT_WHITE, font=FONT_SMALL)
    
    # 16-Indicator Cluster Grid
    gy = ay + 80
    draw.text((hx + 16, gy), "16-INDICATOR QUANT CONFLUENCE", fill=TEXT_MUTED, font=FONT_SMALL)
    
    pills = [
        ("Quad EMA", "BULLISH", GREEN_ACCENT),
        ("SuperTrend", "BULLISH", GREEN_ACCENT),
        ("ADX Trend", "46.2 HIGH", CYAN_ACCENT),
        ("LinReg Slope", "+17.2", GREEN_ACCENT),
        ("Dual RSI", "74.8 EXP", GREEN_ACCENT),
        ("Stochastic", "87.0 OB", GOLD_ACCENT),
        ("MACD Hist", "+1.28 EXP", GREEN_ACCENT),
        ("CCI (14)", "+113.4", GREEN_ACCENT),
        ("Bollinger %B", "0.88 HIGH", CYAN_ACCENT),
        ("Keltner Ch", "ABOVE", GREEN_ACCENT),
        ("Candle Geo", "82% BODY", GREEN_ACCENT),
        ("Volume Delta", "89% BUY", GREEN_ACCENT),
    ]
    
    col_w = (hw - 48) // 3
    for i, (name, val, col) in enumerate(pills):
        r = i // 3
        c = i % 3
        px = hx + 16 + c * (col_w + 8)
        py = gy + 20 + r * 38
        draw.rounded_rectangle([(px, py), (px + col_w, py + 32)], radius=6, fill=(10, 16, 28), outline=PANEL_BORDER, width=1)
        draw.text((px + 6, py + 3), name, fill=TEXT_MUTED, font=FONT_SMALL)
        draw.text((px + 6, py + 16), val, fill=col, font=FONT_SMALL)
        
    # Bottom Action Buttons
    by = gy + 180
    btn_w = (hw - 40) // 2
    draw.rounded_rectangle([(hx + 16, by), (hx + 16 + btn_w, by + 40)], radius=8, fill=(0, 200, 83), outline=GREEN_ACCENT, width=1)
    draw.text((hx + 36, by + 11), "BUY YES (CALL UP)", fill=(5, 46, 22), font=FONT_BODY_BOLD)
    
    draw.rounded_rectangle([(hx + 24 + btn_w, by), (hx + hw - 16, by + 40)], radius=8, fill=(213, 0, 0), outline=RED_ACCENT, width=1)
    draw.text((hx + 44 + btn_w, by + 11), "BUY NO (CALL DOWN)", fill=TEXT_WHITE, font=FONT_BODY_BOLD)

def render_frame_for_time(t, total_dur, timeline):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    active_entry = None
    for entry in timeline:
        if entry["start"] <= t <= entry["end"]:
            active_entry = entry
            break
            
    if not active_entry:
        active_ch_id = 0
        elapsed = 0.0
        for ch in CHAPTER_DEFS:
            if t < elapsed + 30.0 or ch["id"] == 5:
                active_ch_id = ch["id"]
                break
            elapsed += 30.0
        active_ch = CHAPTER_DEFS[active_ch_id]
        active_url = active_ch["url"]
        active_title = active_ch["title"]
        active_sub = ""
    else:
        active_ch_id = active_entry["chapter_id"]
        active_title = active_entry["chapter_title"]
        active_url = active_entry["url"]
        active_sub = active_entry["text"]

    draw_top_browser_bar(draw, active_url, active_title, t, total_dur)
    
    # Left Main Stage (x: 40 to 760, y: 80 to 600)
    # Simulated Polymarket Web Interface
    draw.rounded_rectangle([(40, 80), (760, 600)], radius=14, fill=(11, 16, 28), outline=PANEL_BORDER, width=1)
    
    # Breadcrumb & Event Title
    draw.text((64, 100), "POLYMARKET > CRYPTO > BITCOIN > 5-MINUTE MARKETS", fill=CYAN_ACCENT, font=FONT_SMALL)
    draw.text((64, 122), "Bitcoin Up or Down in 5 mins? (Round #1788)", fill=TEXT_WHITE, font=FONT_TITLE)
    
    # Polymarket Round Stats Row
    draw.text((64, 170), "STRIKE PRICE LOCK: $75,280.00", fill=GOLD_ACCENT, font=FONT_BODY_BOLD)
    draw.text((380, 170), "POOL VOLUME: $184,920 USDC", fill=TEXT_MUTED, font=FONT_BODY)
    draw.text((640, 170), "CLOSES IN: 00:45", fill=CYAN_ACCENT, font=FONT_BODY_BOLD)
    
    # Simulated Candlestick Chart Area (x: 64 to 736, y: 205 to 440)
    draw.rounded_rectangle([(64, 205), (736, 440)], radius=8, fill=(7, 11, 20), outline=(20, 30, 50), width=1)
    
    # Grid lines
    for gy in range(230, 440, 45):
        draw.line([(64, gy), (736, gy)], fill=(18, 26, 40), width=1)
    for gx in range(120, 736, 80):
        draw.line([(gx, 205), (gx, 440)], fill=(18, 26, 40), width=1)
        
    # Strike Line (Gold Dashed)
    draw.line([(64, 340), (736, 340)], fill=GOLD_ACCENT, width=2)
    draw.text((70, 322), "STRIKE $75,280", fill=GOLD_ACCENT, font=FONT_SMALL)
    
    # Simulated Candles
    candles = [
        (100, 360, 345, 370, 340, False),
        (150, 345, 350, 358, 340, True),
        (200, 350, 335, 355, 330, False),
        (250, 335, 325, 340, 320, False),
        (300, 325, 330, 336, 322, True),
        (350, 330, 310, 335, 305, False),
        (400, 310, 290, 315, 285, False),
        (450, 290, 270, 295, 265, False),
        (500, 270, 255, 275, 250, False),
        (550, 255, 240, 260, 235, False),
        (600, 240, 230, 245, 225, False),
        (650, 230, 220 + int(math.sin(t * 3) * 6), 235, 215, False)
    ]
    for cx, c_open, c_close, c_high, c_low, is_red in candles:
        col = RED_ACCENT if is_red else GREEN_ACCENT
        draw.line([(cx, c_high), (cx, c_low)], fill=col, width=1)
        top_y = min(c_open, c_close)
        bot_y = max(c_open, c_close)
        draw.rectangle([(cx - 8, top_y), (cx + 8, bot_y)], fill=col)
        
    # Polymarket Betting Cards (Bottom of left stage)
    # YES Card
    draw.rounded_rectangle([(64, 460), (380, 580)], radius=10, fill=(16, 28, 48), outline=GREEN_ACCENT, width=2)
    draw.text((84, 474), "UP / YES", fill=GREEN_ACCENT, font=FONT_HEADING)
    draw.text((84, 502), "Market Odds: 58¢ (58%)", fill=TEXT_MUTED, font=FONT_BODY)
    draw.text((84, 528), "Fair Quant Odds: 92¢ (92%)", fill=CYAN_ACCENT, font=FONT_BODY_BOLD)
    draw.text((84, 552), "★ EDGE: +34% UNDERPRICED", fill=GOLD_ACCENT, font=FONT_SMALL)
    
    # NO Card
    draw.rounded_rectangle([(410, 460), (736, 580)], radius=10, fill=(16, 22, 38), outline=PANEL_BORDER, width=1)
    draw.text((430, 474), "DOWN / NO", fill=RED_ACCENT, font=FONT_HEADING)
    draw.text((430, 502), "Market Odds: 42¢ (42%)", fill=TEXT_MUTED, font=FONT_BODY)
    draw.text((430, 528), "Fair Quant Odds: 8¢ (8%)", fill=TEXT_MUTED, font=FONT_BODY)
    draw.text((430, 552), "OVERPRICED TICKET", fill=TEXT_MUTED, font=FONT_SMALL)

    # Right Floating HUD Overlay
    hud_spot = 75422.50 + math.sin(t * 2.5) * 8.0
    hud_remaining = max(12, int(45 - (t % 30)))
    draw_floating_hud(draw, t, spot_price=hud_spot, strike=75280.00, remaining_s=hud_remaining, conf=92)
    
    # Interactive Chapter Highlights
    if active_ch_id == 4: # 1-Click execution demo: Draw simulated cursor clicking YES
        cursor_x = int(64 + 200 + math.sin(t * 2) * 20)
        cursor_y = int(460 + 50)
        # Highlight outline around YES card
        draw.rounded_rectangle([(60, 456), (384, 584)], radius=12, outline=CYAN_ACCENT, width=3)
        # Mouse cursor
        poly = [(cursor_x, cursor_y), (cursor_x, cursor_y + 20), (cursor_x + 6, cursor_y + 15), (cursor_x + 12, cursor_y + 19), (cursor_x + 16, cursor_y + 14), (cursor_x + 8, cursor_y + 11), (cursor_x + 14, cursor_y + 8)]
        draw.polygon(poly, fill=(255, 255, 255), outline=(0, 0, 0))
        if int(t * 2) % 2 == 0:
            draw.ellipse([(cursor_x - 10, cursor_y - 10), (cursor_x + 16, cursor_y + 16)], outline=CYAN_ACCENT, width=2)
            
    elif active_ch_id == 5: # Web Store card overlay
        draw.rounded_rectangle([(100, 140), (700, 550)], radius=14, fill=(10, 18, 34), outline=CYAN_ACCENT, width=2)
        draw.text((130, 165), "💎 ALGO TRADING PORTAL - OFFICIAL STORE", fill=CYAN_ACCENT, font=FONT_HEADING)
        draw.text((130, 205), "• Polymarket BTC 5M Sniper Pro: $10 USDT (Lifetime)", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
        draw.text((130, 240), "• Pocket Option Signal Pro: $10 USDT (Lifetime)", fill=TEXT_WHITE, font=FONT_BODY_BOLD)
        draw.text((130, 280), "• Pro Trader Dual VIP Bundle: $18 USDT (Save $2)", fill=GOLD_ACCENT, font=FONT_TITLE)
        draw.text((130, 335), "Automated On-Chain USDT Verification (TRC-20 & BEP-20)", fill=GREEN_ACCENT, font=FONT_BODY)
        draw.text((130, 370), "Instant License Key Issuance & Extension Zip Download", fill=TEXT_MUTED, font=FONT_BODY)
        draw.rounded_rectangle([(130, 420), (450, 475)], radius=8, fill=CYAN_ACCENT)
        draw.text((150, 436), "VISIT ALGO-TRADING-PORTAL.ONRENDER.COM", fill=(6, 10, 18), font=FONT_BODY_BOLD)

    # Bottom Subtitle Bar
    draw_subtitle_bar(draw, active_sub, active_title)
    return img

def main():
    print("=== Polymarket BTC 5M Sniper Pro Video Renderer ===")
    
    # Step 1: Speech Audio
    clip_info = generate_voice_clips()
    master_audio_path, timeline, total_duration = build_master_audio(clip_info)
    
    # Step 2: Video Encoding Setup
    output_mp4 = os.path.join(PUBLIC_VIDEOS, "polymarket-sniper-walkthrough.mp4")
    total_frames = int(total_duration * FPS)
    print(f"\nRendering {total_frames} frames ({FPS} fps) for {total_duration:.2f}s...")
    
    ffmpeg_cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-", # Pipe raw video frames
        "-i", master_audio_path, # Audio track
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    for frame_idx in range(total_frames):
        t = frame_idx / float(FPS)
        frame_img = render_frame_for_time(t, total_duration, timeline)
        proc.stdin.write(frame_img.tobytes())
        
        if frame_idx % 75 == 0 or frame_idx == total_frames - 1:
            pct = (frame_idx / float(total_frames)) * 100
            print(f"  Frame {frame_idx}/{total_frames} ({pct:.1f}%) rendered at t={t:.1f}s")
            
    proc.stdin.close()
    proc.wait()
    
    if os.path.exists(output_mp4):
        size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
        print(f"\nSUCCESS! Video generated at: {output_mp4} ({size_mb:.2f} MB)")
    else:
        print("\nERROR: Video file was not created.")

if __name__ == "__main__":
    main()
