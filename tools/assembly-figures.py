#!/usr/bin/env python3
"""Illustrated assembly guide — how the parts physically fit together, for someone
who has never soldered.

    mise exec -- python tools/assembly-figures.py
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assembly-guide.html")
F = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'

# ---------------------------------------------------------------- 1. exploded stack
def fig_stack():
    o=[f'<svg width="900" height="560" viewBox="0 0 900 560" {F}>']
    def layer(y,h,col,label,detail,tag=""):
        o.append(f'<rect x="120" y="{y}" width="440" height="{h}" rx="4" fill="{col}" stroke="#333"/>')
        o.append(f'<text x="580" y="{y+h/2+1}" font-size="14" font-weight="700" fill="#222">{label}</text>')
        o.append(f'<text x="580" y="{y+h/2+18}" font-size="11.5" fill="#666">{detail}</text>')
        if tag: o.append(f'<text x="110" y="{y+h/2+4}" text-anchor="end" font-size="11" fill="#999">{tag}</text>')
    layer(40,16,"#8d8d88","FACE PLATE (printed)","holes for LEDs + buttons, window for LCD","2.5mm")
    # LCD hanging under face
    o.append('<rect x="180" y="58" width="240" height="26" rx="3" fill="#1d3b2a" stroke="#4a7"/>')
    o.append('<text x="300" y="75" text-anchor="middle" font-size="11" fill="#8fd6a8">LCD — screwed to the face</text>')
    o.append('<text x="580" y="72" font-size="12" fill="#2a7d55">The LCD hangs from the FACE, not the board.</text>')
    o.append('<text x="580" y="88" font-size="11.5" fill="#666">4 wires run down to the perfboard.</text>')
    # buttons + leds poking up
    for x,lab in ((150,"btn"),(230,"btn"),(310,"LED"),(390,"LED")):
        o.append(f'<rect x="{x}" y="112" width="30" height="46" rx="3" fill="#b33" stroke="#333"/>')
        o.append(f'<text x="{x+15}" y="140" text-anchor="middle" font-size="9" fill="#fff">{lab}</text>')
    o.append('<text x="580" y="140" font-size="13" font-weight="700" fill="#222">buttons + LEDs</text>')
    o.append('<text x="580" y="157" font-size="11.5" fill="#666">soldered to the board, poking UP through the face</text>')
    layer(158,14,"#2f6b3f","PERFBOARD — the only circuit board","everything solders here","1.6mm")
    # esp32 under? no - on top, beside
    o.append('<rect x="200" y="112" width="150" height="46" rx="3" fill="none" stroke="#d99a2b" stroke-width="2" stroke-dasharray="5 3"/>')
    o.append('<text x="275" y="106" text-anchor="middle" font-size="10.5" fill="#d99a2b">ESP32 sits here too (beside them, same level)</text>')
    layer(200,60,"#c9c9c2","BOX (printed)","walls, floor, standoffs, USB slot","")
    o.append('<text x="340" y="236" text-anchor="middle" font-size="12" fill="#555">empty space — wire bends</text>')
    o.append('<text x="120" y="300" font-size="13" font-weight="700" fill="#222">Reading it: the face plate screws onto the box, sandwiching the perfboard between them.</text>')
    o.append('<text x="120" y="322" font-size="12.5" fill="#555">The board sits on standoffs. Buttons and LEDs are tall enough to reach the face. The LCD is the</text>')
    o.append('<text x="120" y="342" font-size="12.5" fill="#555">only component that is NOT on the board — it screws to the underside of the face plate.</text>')
    o.append('</svg>'); return "".join(o)

# ------------------------------------------------------------- 2. what's on the board
def fig_board_parts():
    o=[f'<svg width="900" height="420" viewBox="0 0 900 420" {F}>']
    o.append('<rect x="40" y="40" width="380" height="330" rx="6" fill="#2f6b3f" stroke="#1c4527"/>')
    for c in range(19):
        for r in range(17):
            o.append(f'<circle cx="{58+c*20}" cy="{58+r*19}" r="1.8" fill="#1c4527"/>')
    def part(x,y,w,h,col,lab,fs=10):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{col}" stroke="#111"/>')
        o.append(f'<text x="{x+w/2}" y="{y+h/2+3}" text-anchor="middle" font-size="{fs}" fill="#fff">{lab}</text>')
    part(60,58,90,14,"#c60","LCD 4-pin")
    for i,c in enumerate((70,150,230,310)):
        o.append(f'<circle cx="{c+15}" cy="140" r="8" fill="{["#9d2933","#2f5d1e","#14538a","#8a5a12"][i]}" stroke="#111"/>')
        part(c,170,30,30,["#9d2933","#2f5d1e","#14538a","#8a5a12"][i],str(i+1),11)
    part(60,300,34,34,"#6a4a12","AA")
    part(300,300,34,34,"#1b1b1b","no")
    part(345,300,34,34,"#0f6b52","yes")
    o.append('<rect x="150" y="250" width="120" height="110" rx="4" fill="#2b2b33" stroke="#111"/>')
    o.append('<text x="210" y="300" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">ESP32</text>')
    o.append('<text x="210" y="316" text-anchor="middle" font-size="9" fill="#9ad">plugs into header</text>')
    o.append('<line x1="60" y1="232" x2="400" y2="232" stroke="#111" stroke-width="4"/>')
    o.append('<text x="404" y="236" font-size="10" font-weight="700" fill="#111">GND</text>')
    o.append('<line x1="60" y1="243" x2="400" y2="243" stroke="#c33" stroke-width="4"/>')
    o.append('<text x="404" y="247" font-size="10" font-weight="700" fill="#c33">5V</text>')
    txt = [("Everything above is ONE board.",700,"#222",13),
           ("• LEDs + buttons solder straight to it and poke through the face.",0,"#555",12),
           ("• The ESP32 does NOT get soldered. You solder two rows of female",0,"#555",12),
           ("  header sockets; the ESP32 pushes into them like a chip in a socket,",0,"#555",12),
           ("  so it can be pulled out and swapped.",0,"#555",12),
           ("• The two thick lines are the buses: bare wires every ground and",0,"#555",12),
           ("  power connection ties to. Solder these EARLY.",0,"#555",12),
           ("• The orange strip is a 4-pin connector — the LCD's wires land there.",0,"#555",12)]
    y=70
    for t,_,c,fs in txt:
        o.append(f'<text x="450" y="{y}" font-size="{fs}" fill="{c}" font-weight="{700 if fs==13 else 400}">{t}</text>')
        y += 26 if fs==13 else 20
    o.append('</svg>'); return "".join(o)

# ------------------------------------------------------------------ 3. LCD mounting
def fig_lcd():
    o=[f'<svg width="900" height="400" viewBox="0 0 900 400" {F}>']
    o.append('<text x="30" y="28" font-size="14" font-weight="700" fill="#222">Side view — how the LCD attaches</text>')
    o.append('<rect x="60" y="60" width="420" height="14" fill="#8d8d88" stroke="#333"/>')
    o.append('<text x="490" y="72" font-size="12" fill="#444">face plate</text>')
    o.append('<rect x="150" y="74" width="240" height="10" fill="#111"/>')
    o.append('<rect x="150" y="84" width="240" height="30" fill="#1d3b2a" stroke="#4a7"/>')
    o.append('<text x="270" y="103" text-anchor="middle" font-size="11" fill="#8fd6a8">LCD module</text>')
    o.append('<rect x="200" y="114" width="140" height="16" fill="#33333b" stroke="#111"/>')
    o.append('<text x="270" y="126" text-anchor="middle" font-size="9" fill="#9ad">I²C board on the back</text>')
    # window
    o.append('<rect x="215" y="60" width="110" height="14" fill="#fff" stroke="#4a7"/>')
    o.append('<text x="600" y="66" font-size="12" fill="#2a7d55">window cut 64.5 × 16mm — the glass shows through</text>')
    # screws
    for x in (160,380):
        o.append(f'<line x1="{x}" y1="52" x2="{x}" y2="120" stroke="#777" stroke-width="4"/>')
        o.append(f'<circle cx="{x}" cy="50" r="6" fill="#999" stroke="#555"/>')
    o.append('<text x="600" y="90" font-size="12" fill="#444">M3 screws through the LCD\'s own corner holes</text>')
    o.append('<text x="600" y="108" font-size="12" fill="#444">into posts printed on the face (75 × 31mm centres)</text>')
    # wires down to board
    for i,(x,lab,col) in enumerate([(215,"GND","#111"),(245,"VCC","#c33"),(275,"SDA","#e80"),(305,"SCL","#852")]):
        o.append(f'<path d="M {x} 130 C {x} 200, {x+40} 230, {x+60} 268" stroke="{col}" stroke-width="3" fill="none"/>')
        o.append(f'<text x="{x-6}" y="145" font-size="10" fill="{col}">{lab}</text>')
    o.append('<rect x="60" y="268" width="420" height="12" fill="#2f6b3f" stroke="#1c4527"/>')
    o.append('<text x="490" y="279" font-size="12" fill="#444">perfboard</text>')
    o.append('<text x="60" y="320" font-size="13" font-weight="700" fill="#222">Only 4 wires connect the LCD to the board:</text>')
    o.append('<text x="60" y="342" font-size="12.5" fill="#555">GND → GND bus · VCC → 5V bus · SDA → GPIO 21 · SCL → GPIO 22</text>')
    o.append('<text x="60" y="364" font-size="12.5" fill="#a60">Use STRANDED wire and leave them long — the face has to lift off while you work.</text>')
    o.append('</svg>'); return "".join(o)

# ------------------------------------------------------- 4. how a button/LED sits
def fig_through():
    o=[f'<svg width="900" height="340" viewBox="0 0 900 340" {F}>']
    o.append('<text x="30" y="26" font-size="14" font-weight="700" fill="#222">Side view — a button and an LED through the face</text>')
    o.append('<rect x="60" y="70" width="700" height="14" fill="#8d8d88" stroke="#333"/>')
    o.append('<rect x="150" y="70" width="46" height="14" fill="#faf9f6"/>')
    o.append('<rect x="430" y="70" width="20" height="14" fill="#faf9f6"/>')
    o.append('<rect x="60" y="230" width="700" height="12" fill="#2f6b3f" stroke="#1c4527"/>')
    o.append('<text x="775" y="80" font-size="12" fill="#444">face</text>')
    o.append('<text x="775" y="241" font-size="12" fill="#444">board</text>')
    # button
    o.append('<rect x="146" y="56" width="54" height="18" rx="3" fill="#9d2933" stroke="#111"/>')
    o.append('<text x="173" y="50" text-anchor="middle" font-size="10" fill="#333">cap</text>')
    o.append('<rect x="152" y="74" width="42" height="30" fill="#cfcfca" stroke="#777"/>')
    o.append('<rect x="140" y="104" width="66" height="126" fill="none"/>')
    for x in (156,190):
        o.append(f'<line x1="{x}" y1="104" x2="{x}" y2="236" stroke="#888" stroke-width="3"/>')
        o.append(f'<path d="M {x-7} 236 Q {x} 222 {x+7} 236 Z" fill="#b9bcc2" stroke="#666"/>')
    o.append('<text x="240" y="120" font-size="12" fill="#444">Switch body is BELOW the face;</text>')
    o.append('<text x="240" y="138" font-size="12" fill="#444">only the cap pokes through.</text>')
    o.append('<text x="240" y="156" font-size="12" fill="#a60">Hole is sized to the CAP (+0.4mm).</text>')
    o.append('<text x="240" y="180" font-size="12" fill="#444">Legs solder to the board — the joint is</text>')
    o.append('<text x="240" y="198" font-size="12" fill="#444">on the UNDERSIDE, shown as the fillets.</text>')
    # LED
    o.append('<circle cx="440" cy="66" r="11" fill="#c33" stroke="#111"/>')
    o.append('<line x1="434" y1="76" x2="434" y2="236" stroke="#888" stroke-width="3"/>')
    o.append('<line x1="446" y1="76" x2="446" y2="236" stroke="#888" stroke-width="3"/>')
    for x in (434,446): o.append(f'<path d="M {x-7} 236 Q {x} 222 {x+7} 236 Z" fill="#b9bcc2" stroke="#666"/>')
    o.append('<text x="500" y="120" font-size="12" fill="#444">LED body sits IN the 5.2mm hole.</text>')
    o.append('<text x="500" y="138" font-size="12" fill="#a60">Leave the legs long: push the LED up to</text>')
    o.append('<text x="500" y="156" font-size="12" fill="#a60">the face BEFORE soldering, then trim.</text>')
    o.append('<text x="500" y="180" font-size="12" fill="#444">Long leg = +, goes to the GPIO.</text>')
    o.append('<text x="500" y="198" font-size="12" fill="#444">Short leg = −, via 220Ω to the GND bus.</text>')
    o.append('<text x="60" y="290" font-size="12.5" fill="#555">Assemble in this order: seat the part in the face, THEN solder its legs. If you solder first, the</text>')
    o.append('<text x="60" y="310" font-size="12.5" fill="#555">heights will not line up and the caps will bind or the LEDs will sit sunken.</text>')
    o.append('</svg>'); return "".join(o)

# --------------------------------------------------------------- 5. one solder joint
def fig_joint():
    o=[f'<svg width="900" height="330" viewBox="0 0 900 330" {F}>']
    o.append('<text x="30" y="26" font-size="14" font-weight="700" fill="#222">Making one joint — the whole motion takes 2–4 seconds</text>')
    for i,(t,cap) in enumerate([
        ("1. Heat BOTH","Touch the iron so it<tspan x='0' dy='15'>touches the pad AND</tspan><tspan x='0' dy='15'>the leg at once. ~2s.</tspan>"),
        ("2. Feed solder","Into the JOINT, not<tspan x='0' dy='15'>onto the iron. It should</tspan><tspan x='0' dy='15'>flow instantly.</tspan>"),
        ("3. Solder away","Remove the solder<tspan x='0' dy='15'>first, then the iron.</tspan><tspan x='0' dy='15'>Don't wiggle it.</tspan>"),
        ("4. Trim","Snip the leg flush<tspan x='0' dy='15'>once cool. Joint should</tspan><tspan x='0' dy='15'>be shiny + concave.</tspan>")]):
        x = 40 + i*220
        o.append(f'<rect x="{x}" y="50" width="190" height="150" rx="8" fill="#fff" stroke="#ddd"/>')
        o.append(f'<text x="{x+12}" y="72" font-size="13" font-weight="700" fill="#222">{t}</text>')
        # board + pad + leg
        o.append(f'<rect x="{x+20}" y="150" width="150" height="10" fill="#2f6b3f"/>')
        o.append(f'<rect x="{x+80}" y="146" width="30" height="6" fill="#c8a13a"/>')
        o.append(f'<line x1="{x+95}" y1="100" x2="{x+95}" y2="152" stroke="#888" stroke-width="4"/>')
        if i==0:
            o.append(f'<line x1="{x+130}" y1="105" x2="{x+100}" y2="145" stroke="#b55" stroke-width="7" stroke-linecap="round"/>')
        if i==1:
            o.append(f'<line x1="{x+130}" y1="105" x2="{x+100}" y2="145" stroke="#b55" stroke-width="7" stroke-linecap="round"/>')
            o.append(f'<line x1="{x+55}" y1="110" x2="{x+88}" y2="142" stroke="#aaa" stroke-width="4" stroke-linecap="round"/>')
        if i>=2:
            o.append(f'<path d="M {x+80} 152 Q {x+95} 132 {x+110} 152 Z" fill="#b9bcc2" stroke="#666"/>')
        if i==3:
            o.append(f'<line x1="{x+95}" y1="100" x2="{x+95}" y2="130" stroke="#faf9f6" stroke-width="6"/>')
        o.append(f'<text x="{x+12}" y="222" font-size="11.5" fill="#555"><tspan x="{x+12}">{cap}</tspan></text>')
    o.append('<text x="40" y="300" font-size="12.5" fill="#a00">If it is not flowing, STOP. Add flux and retry. Holding the iron there lifts the pad and kills the part.</text>')
    o.append('</svg>'); return "".join(o)

FIGS=[
 ("How it all fits together", fig_stack(),
  "The single most important picture. Face plate on top, box underneath, perfboard sandwiched between."),
 ("There is only ONE circuit board", fig_board_parts(),
  "The ESP32 is not soldered — it plugs into header sockets. Only the LCD lives off-board."),
 ("How the LCD attaches", fig_lcd(),
  "It screws to the face plate and reaches the board with 4 stranded wires. It never touches the perfboard."),
 ("How buttons and LEDs pass through the face", fig_through(),
  "Seat the part against the face first, then solder. Solder first and the heights won't line up."),
 ("Making a single solder joint", fig_joint(),
  "Practise this on scrap holes ten times before touching the real board."),
]
CSS="""
:root{color-scheme:light dark}
body{margin:0;padding:2rem 1.25rem 4rem;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
background:#faf9f6;color:#22252a;max-width:70rem;margin-inline:auto}
h1{font-size:2rem;margin:0 0 .2em}.sub{color:#666;margin-bottom:2rem}
figure{margin:0 0 2.6rem;padding:1.25rem;background:#fff;border:1px solid #e6e3da;border-radius:12px;overflow-x:auto}
figcaption{margin-top:.8rem;font-size:.95rem;color:#555;border-top:1px solid #eee;padding-top:.6rem}
h2{font-size:1.15rem;margin:0 0 .8rem}
.key{background:#eef6f0;border-left:4px solid #2f7d4f;padding:.9em 1.1em;border-radius:0 8px 8px 0;margin:1.2rem 0}
@media (prefers-color-scheme:dark){body{background:#16181c;color:#d8dae0}
figure{background:#1c1f24;border-color:#2c3038}figcaption{color:#aab;border-color:#2c3038}
.sub{color:#99a}.key{background:#16241c}}
"""
body="".join(f'<figure><h2>{t}</h2>{s}<figcaption>{c}</figcaption></figure>' for t,s,c in FIGS)
page=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Pad — how it fits together</title><style>{CSS}</style></head><body>
<h1>How it fits together</h1>
<p class="sub">Read this before the step-by-step build. It answers "what am I actually making?"</p>
<div class="key"><strong>The one-sentence version:</strong> there is a single perfboard;
the LEDs and buttons solder to it and poke up through holes in the printed face plate; the
ESP32 plugs into sockets on it; the LCD screws to the face plate and reaches the board with
four wires; the face screws onto the printed box with the board sandwiched between.</div>
{body}</body></html>"""
open(OUT,"w").write(page)
print(OUT)
subprocess.run(["open", OUT], check=False)
