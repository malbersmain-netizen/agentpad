#!/usr/bin/env python3
"""Generate the illustrated build guide (figures for the case + every solder step).

    mise exec -- python tools/build-figures.py
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "build-figures.html")

S = 3.3                                   # px per mm
CW, CH, CD = 95, 140, 28                  # case, mm
def mm(v): return v * S

# ---- face layout, to scale -------------------------------------------------
BTN, LED, LCDW, LCDH = 12, 5, 80, 36
gap = (CW - 4*BTN) / 5                    # even gaps across the width
CX  = [gap + BTN/2 + i*(BTN+gap) for i in range(4)]
Y_LCD, Y_LED, Y_BTN, Y_ANS = 10, 58, 75, 112
COL = ["#9d2933", "#2f5d1e", "#14538a", "#8a5a12"]
NAME = ["1", "2", "3", "4"]

def fig1():
    w, h = mm(CW)+180, mm(CH)+70
    o = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">']
    ox, oy = 30, 30
    o.append(f'<rect x="{ox}" y="{oy}" width="{mm(CW)}" height="{mm(CH)}" rx="10" fill="#3c3c3a" stroke="#222"/>')
    # LCD
    lx = ox + mm((CW-LCDW)/2); ly = oy + mm(Y_LCD)
    o.append(f'<rect x="{lx}" y="{ly}" width="{mm(LCDW)}" height="{mm(LCDH)}" rx="3" fill="#2b2b2a" stroke="#6a6a68" stroke-dasharray="4 3"/>')
    vw, vh = 64.5, 16
    vx = ox + mm((CW-vw)/2); vy = ly + mm((LCDH-vh)/2)
    o.append(f'<rect x="{vx}" y="{vy}" width="{mm(vw)}" height="{mm(vh)}" rx="2" fill="#1d3b2a" stroke="#4a7"/>')
    o.append(f'<text x="{vx+mm(vw)/2}" y="{vy+mm(vh)/2+4}" text-anchor="middle" font-size="10" fill="#8fd6a8">A3 BLOCKED 4:21</text>')
    o.append(f'<text x="{lx+mm(LCDW)+8}" y="{ly+12}" font-size="11" fill="#c33">module 80×36 — only 7.5mm margin!</text>')
    o.append(f'<text x="{vx+mm(vw)+8}" y="{vy+mm(vh)+18}" font-size="11" fill="#8fd6a8">cut only the 64.5×16 window</text>')
    # LEDs + buttons
    for i,cx in enumerate(CX):
        x = ox+mm(cx)
        o.append(f'<circle cx="{x}" cy="{oy+mm(Y_LED)}" r="{mm(LED)/2}" fill="{COL[i]}" stroke="#111"/>')
        o.append(f'<rect x="{x-mm(BTN)/2}" y="{oy+mm(Y_BTN)-mm(BTN)/2}" width="{mm(BTN)}" height="{mm(BTN)}" rx="3" fill="{COL[i]}" stroke="#111"/>')
        o.append(f'<text x="{x}" y="{oy+mm(Y_BTN)+5}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">{NAME[i]}</text>')
    o.append(f'<text x="{ox+mm(CW)+8}" y="{oy+mm(Y_LED)+4}" font-size="11" fill="#666">status LEDs (5mm)</text>')
    o.append(f'<text x="{ox+mm(CW)+8}" y="{oy+mm(Y_BTN)+4}" font-size="11" fill="#666">select — pitch {BTN+gap:.1f}mm</text>')
    # answer row: AA far left, no/yes right
    for cx,lab,col in [(16,"AA","#8a5a12"), (62,"no","#1b1b1b"), (80,"yes","#0f6b52")]:
        x=ox+mm(cx)
        o.append(f'<rect x="{x-mm(BTN)/2}" y="{oy+mm(Y_ANS)-mm(BTN)/2}" width="{mm(BTN)}" height="{mm(BTN)}" rx="3" fill="{col}" stroke="#111"/>')
        o.append(f'<text x="{x}" y="{oy+mm(Y_ANS)+4}" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">{lab}</text>')
    o.append(f'<text x="{ox+mm(CW)+8}" y="{oy+mm(Y_ANS)+4}" font-size="11" fill="#666">answer row</text>')
    # ESP32 zone
    zx, zy, zw, zh = ox+mm(18), oy+mm(84), mm(58), mm(24)
    o.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="4" fill="none" stroke="#d99a2b" stroke-width="2" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{zx+zw/2}" y="{zy+zh/2+4}" text-anchor="middle" font-size="11" font-weight="700" fill="#d99a2b">ESP32 zone — needs 55×28mm</text>')
    o.append(f'<text x="{zx}" y="{zy+zh+16}" font-size="10.5" fill="#c33">this band is ~24mm today; open it to 30mm</text>')
    # usb
    o.append(f'<rect x="{ox+mm(CW)/2-14}" y="{oy+mm(CH)-4}" width="28" height="10" rx="3" fill="#888"/>')
    o.append(f'<text x="{ox+mm(CW)/2+22}" y="{oy+mm(CH)+8}" font-size="10.5" fill="#666">USB-C</text>')
    o.append('</svg>')
    return "".join(o)

# ---- depth section ---------------------------------------------------------
def fig2():
    w,h=760,330; o=[f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">']
    def stack(x0,title,layers,total,ok):
        o.append(f'<text x="{x0}" y="26" font-size="14" font-weight="700" fill="#222">{title}</text>')
        y=44
        for lab,mmv,col in layers:
            hh=mmv*6
            o.append(f'<rect x="{x0}" y="{y}" width="200" height="{hh}" fill="{col}" stroke="#333"/>')
            o.append(f'<text x="{x0+210}" y="{y+hh/2+4}" font-size="11" fill="#444">{lab} — {mmv}mm</text>')
            y+=hh
        c = "#2f7d4f" if ok else "#c33"
        o.append(f'<text x="{x0}" y="{y+24}" font-size="13" font-weight="700" fill="{c}">total {total}mm — {"FITS in 28mm" if ok else "TOO DEEP for 28mm"}</text>')
    stack(30,"A. ESP32 stacked under board",
          [("face",2.5,"#8d8d88"),("button cap clearance",12.5,"#c9c9c2"),("perfboard",1.6,"#3a6b3a"),
           ("header + ESP32 + USB",13.6,"#2b2b33"),("back",2.5,"#8d8d88")],32.7,False)
    stack(400,"B. ESP32 coplanar (beside)",
          [("face",2.5,"#8d8d88"),("tallest part (ESP32 13.6)",13.6,"#c9c9c2"),("perfboard",1.6,"#3a6b3a"),
           ("wire bend room",4,"#5a5a63"),("back",2.5,"#8d8d88")],24.2,True)
    o.append('</svg>'); return "".join(o)

# ---- perfboard layout ------------------------------------------------------
GC, GR, P = 34, 50, 12
def board(show, note=""):
    w,h=GC*P+300,GR*P+70
    o=[f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">']
    ox,oy=30,30
    o.append(f'<rect x="{ox-8}" y="{oy-8}" width="{GC*P+16}" height="{GR*P+16}" rx="6" fill="#2f6b3f" stroke="#1c4527"/>')
    for c in range(GC):
        for r in range(GR):
            o.append(f'<circle cx="{ox+c*P}" cy="{oy+r*P}" r="1.7" fill="#1c4527"/>')
    def X(c): return ox+c*P
    def Y(r): return oy+r*P
    # buses
    if "bus" in show:
        o.append(f'<line x1="{X(1)}" y1="{Y(46)}" x2="{X(32)}" y2="{Y(46)}" stroke="#111" stroke-width="5"/>')
        o.append(f'<text x="{X(33)}" y="{Y(46)+4}" font-size="11" font-weight="700" fill="#111">GND bus</text>')
        o.append(f'<line x1="{X(1)}" y1="{Y(48)}" x2="{X(32)}" y2="{Y(48)}" stroke="#c33" stroke-width="5"/>')
        o.append(f'<text x="{X(33)}" y="{Y(48)+4}" font-size="11" font-weight="700" fill="#c33">5V bus</text>')
    if "hdr" in show:
        for c in (11,20):
            o.append(f'<rect x="{X(c)-6}" y="{Y(28)-6}" width="12" height="{15*P+12}" rx="3" fill="#1b1b1b"/>')
        o.append(f'<text x="{X(15.5)}" y="{Y(35)}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">ESP32</text>')
        o.append(f'<text x="{X(15.5)}" y="{Y(36.4)}" text-anchor="middle" font-size="9" fill="#9ad">female header</text>')
        o.append(f'<text x="{X(15.5)}" y="{Y(44)}" text-anchor="middle" font-size="9" fill="#cfc">USB toward bottom edge</text>')
    if "lcd" in show:
        o.append(f'<rect x="{X(2)-6}" y="{Y(2)-6}" width="{3*P+12}" height="12" rx="3" fill="#c60"/>')
        o.append(f'<text x="{X(6)}" y="{Y(2)+4}" font-size="11" fill="#c60">LCD 4-pin (flying leads)</text>')
    if "led" in show:
        for i,c in enumerate((4,12,20,28)):
            o.append(f'<circle cx="{X(c)}" cy="{Y(8)}" r="7" fill="{COL[i]}" stroke="#111"/>')
            o.append(f'<rect x="{X(c)-4}" y="{Y(10)}" width="8" height="{2*P}" rx="2" fill="#c8862a"/>')
        o.append(f'<text x="{X(31)}" y="{Y(8)+4}" font-size="11" fill="#333">LEDs</text>')
        o.append(f'<text x="{X(31)}" y="{Y(11)+4}" font-size="11" fill="#c8862a">220Ω → GND bus</text>')
    if "btn" in show:
        for i,c in enumerate((4,12,20,28)):
            o.append(f'<rect x="{X(c)-P*2}" y="{Y(15)-P*2}" width="{P*4}" height="{P*4}" rx="4" fill="{COL[i]}" stroke="#111"/>')
        for c,l in ((5,"AA"),(19,"no"),(26,"yes")):
            o.append(f'<rect x="{X(c)-P*1.5}" y="{Y(22)-P*1.5}" width="{P*3}" height="{P*3}" rx="4" fill="#444" stroke="#111"/>')
            o.append(f'<text x="{X(c)}" y="{Y(22)+4}" text-anchor="middle" font-size="10" fill="#fff">{l}</text>')
    if note:
        o.append(f'<text x="{ox}" y="{oy+GR*P+34}" font-size="12" fill="#555">{note}</text>')
    o.append('</svg>'); return "".join(o)

# ---- detail insets ---------------------------------------------------------
def fig_details():
    o=['<svg width="900" height="270" viewBox="0 0 900 270" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">']
    # LED polarity
    o.append('<text x="20" y="24" font-size="14" font-weight="700" fill="#222">LED polarity</text>')
    o.append('<polygon points="60,70 110,70 85,105" fill="#c33" stroke="#333"/><line x1="60" y1="105" x2="110" y2="105" stroke="#333" stroke-width="3"/>')
    o.append('<line x1="70" y1="105" x2="70" y2="170" stroke="#888" stroke-width="3"/><line x1="100" y1="105" x2="100" y2="150" stroke="#888" stroke-width="3"/>')
    o.append('<text x="30" y="185" font-size="11" fill="#333">long leg (+)</text><text x="118" y="150" font-size="11" fill="#333">short leg (−)</text>')
    o.append('<text x="20" y="215" font-size="11.5" fill="#555">long → GPIO · short → 220Ω → GND bus.</text>')
    o.append('<text x="20" y="234" font-size="11.5" fill="#555">Backwards just doesn\'t light — no damage.</text>')
    # button pairs
    o.append('<text x="330" y="24" font-size="14" font-weight="700" fill="#222">Button: use DIAGONAL legs</text>')
    o.append('<rect x="380" y="60" width="110" height="110" rx="6" fill="#cfcfca" stroke="#777"/>')
    for (x,y) in [(380,60),(490,60),(380,170),(490,170)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#999" stroke="#555"/>')
    o.append('<line x1="380" y1="60" x2="380" y2="170" stroke="#c33" stroke-width="4"/>')
    o.append('<line x1="490" y1="60" x2="490" y2="170" stroke="#c33" stroke-width="4"/>')
    o.append('<text x="330" y="200" font-size="11.5" fill="#c33">red = permanently joined pairs</text>')
    o.append('<circle cx="380" cy="60" r="12" fill="none" stroke="#2f7d4f" stroke-width="3"/>')
    o.append('<circle cx="490" cy="170" r="12" fill="none" stroke="#2f7d4f" stroke-width="3"/>')
    o.append('<text x="330" y="220" font-size="11.5" fill="#2f7d4f">green = use these two (opposite corners)</text>')
    o.append('<text x="330" y="240" font-size="11.5" fill="#555">Always-pressed? Rotate it 90°.</text>')
    # joints
    o.append('<text x="640" y="24" font-size="14" font-weight="700" fill="#222">Joint quality</text>')
    o.append('<line x1="680" y1="70" x2="680" y2="150" stroke="#888" stroke-width="5"/>')
    o.append('<path d="M660 150 Q680 118 700 150 Z" fill="#b9bcc2" stroke="#666"/>')
    o.append('<text x="640" y="180" font-size="11.5" fill="#2f7d4f">good: shiny, concave fillet</text>')
    o.append('<line x1="810" y1="70" x2="810" y2="150" stroke="#888" stroke-width="5"/>')
    o.append('<circle cx="810" cy="140" r="19" fill="#9aa0a8" stroke="#666"/>')
    o.append('<text x="770" y="180" font-size="11.5" fill="#c33">bad: dull ball = cold joint</text>')
    o.append('<text x="640" y="205" font-size="11.5" fill="#555">Reflow with flux until it wets flat.</text>')
    o.append('</svg>'); return "".join(o)

FIGS = [
 ("Overall design — to scale (95 × 140mm)", fig1(),
  "Your sketch is schematic; this is true scale. The LCD module really does span 80 of the 95mm width. "
  "The dashed orange box is where the ESP32 must live — coplanar, not stacked."),
 ("Depth budget — why the ESP32 can't stack", fig2(),
  "28mm is the constraint. Stacking the ESP32 under the perfboard needs 32.7mm and will not close. "
  "Placing it beside the components comes to 24.2mm."),
 ("Step 1–2 — header and buses first", board({"hdr","bus"},
  "Solder the female header and the two buses before anything else. Beep out every bus point, and check GND↔5V does NOT beep."),
  "The buses are the perfboard version of the breadboard rails. A broken rail section caused most of the prototype's bugs."),
 ("Step 3 — LCD connector", board({"hdr","bus","lcd"},
  "Four flying leads to the panel-mounted LCD: GND, VIN(5V), SDA→21, SCL→22."),
  "Test with firmware/lcdtest — it scans I²C and prints the address it finds (0x27 on this build)."),
 ("Step 4 — LEDs and resistors", board({"hdr","bus","lcd","led"},
  "Each LED: long leg to its GPIO, short leg through its own 220Ω down to the GND bus."),
  "Leave the LED legs long — the LEDs must reach up to the face, which sits ~12.5mm above the board."),
 ("Step 5 — all seven buttons", board({"hdr","bus","lcd","led","btn"},
  "Four select buttons in a row, then AA / no / yes. Diagonal legs: one to its GPIO, one to the GND bus."),
  "If several buttons fail at once, suspect the GND bus — not the switches. That exact failure happened twice on the breadboard."),
 ("Details worth getting right", fig_details(),
  "The three things most likely to cost you an hour."),
]

CSS = """
:root{color-scheme:light dark}
body{margin:0;padding:2rem 1.25rem 4rem;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
background:#faf9f6;color:#22252a;max-width:70rem;margin-inline:auto}
h1{font-size:2rem;margin:0 0 .2em}
.sub{color:#666;margin-bottom:2.5rem}
figure{margin:0 0 3rem;padding:1.25rem;background:#fff;border:1px solid #e6e3da;border-radius:12px;overflow-x:auto}
figcaption{margin-top:.9rem;font-size:.95rem;color:#555;border-top:1px solid #eee;padding-top:.7rem}
h2{font-size:1.15rem;margin:0 0 .9rem}
.warn{background:#fdf6e7;border-left:4px solid #d99a2b;padding:.9em 1.1em;border-radius:0 8px 8px 0;margin:1.5rem 0}
@media (prefers-color-scheme:dark){
 body{background:#16181c;color:#d8dae0}figure{background:#1c1f24;border-color:#2c3038}
 figcaption{color:#aab;border-color:#2c3038}.sub{color:#99a}
 .warn{background:#2a2418}}
"""
body = "".join(
    f'<figure><h2>{t}</h2>{svg}<figcaption>{cap}</figcaption></figure>' for t,svg,cap in FIGS)
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Pad — illustrated build</title><style>{CSS}</style></head><body>
<h1>Agent Pad — illustrated build</h1>
<p class="sub">Figures for the case and every solder step. Drawn to scale where it matters.</p>
<div class="warn"><strong>Two changes before you print:</strong> open the middle band to ~30mm so the ESP32
can sit coplanar (stacked it needs 32.7mm and won't fit in 28mm), and cut the LCD window at
<strong>64.5 × 16mm</strong> — not the module's 80 × 36mm outline, or it drops straight through.
Mount holes are M3 on ~75 × 31mm centres.</div>
{body}</body></html>"""
open(OUT,"w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
