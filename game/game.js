/* =============================================================================
   Fundação da Realização Humana — o jogo
   Empilhe os oito degraus na ordem certa, do SER ao CONTRIBUIR.
   ========================================================================== */
(() => {
'use strict';

/* --------------------------------------------------------------- dados -- */

const LEVELS = [
  { n: 1, title: 'SER',           desc: 'caráter, consciência, presença',
    icon: '\u{1F9D8}', top: '#4a5057', face: '#2f3439', ink: '#f2efe9',
    reflect: 'Tudo começa por dentro. Sem caráter, nada do que vem acima se sustenta.',
    warn: 'Ser é o alicerce: nada pode ser posto abaixo dele.' },
  { n: 2, title: 'ORIENTAR-SE',   desc: 'Verdadeiro • Bom • Belo • Sentido',
    icon: '\u{1F9ED}', top: '#a9c0d2', face: '#8098ad', ink: '#152029',
    reflect: 'Sobre o caráter, a bússola: o que é verdadeiro, bom, belo — e por quê.',
    warn: 'Uma bússola só serve a quem já sabe quem é.' },
  { n: 3, title: 'RELACIONAR-SE', desc: 'amor, amizade, comunidade, serviço',
    icon: '\u{1F465}', top: '#a9bfa2', face: '#87a081', ink: '#16211a',
    reflect: 'Ninguém floresce sozinho. Direção compartilhada vira vínculo.',
    warn: 'Vínculos sem direção viram dependência.' },
  { n: 4, title: 'PENSAR',        desc: 'razão, filosofia, pensamento computacional',
    icon: '\u{1F4A1}', top: '#c4c0d8', face: '#a49fbd', ink: '#1b1a24',
    reflect: 'Pensar bem é dever de quem convive: a razão nasce do diálogo.',
    warn: 'Pensamento sem convívio vira abstração fria.' },
  { n: 5, title: 'AGIR',          desc: 'prudência, coragem, disciplina',
    icon: '\u{26F0}\u{FE0F}', top: '#dcb494', face: '#c0916f', ink: '#241a12',
    reflect: 'Pensar sem agir é ruído. Coragem e disciplina transformam ideia em obra.',
    warn: 'Agir antes de pensar é acidente, não virtude.' },
  { n: 6, title: 'ORGANIZAR',     desc: 'pessoas, processos, projetos, plataformas',
    icon: '\u{2699}\u{FE0F}', top: '#a6b8c2', face: '#84979f', ink: '#131b1f',
    reflect: 'A ação repetida com método vira sistema — e o sistema sustenta escala.',
    warn: 'Organizar o que ainda não se faz é burocracia vazia.' },
  { n: 7, title: 'AMPLIFICAR',    desc: 'tecnologia e IA',
    icon: '\u{1F331}', top: '#bcc9ac', face: '#9aa98a', ink: '#181d13',
    reflect: 'A tecnologia multiplica o que já existe — inclusive os erros.',
    warn: 'Amplificar o desorganizado só multiplica o caos.' },
  { n: 8, title: 'CONTRIBUIR',    desc: 'obra, legado, transformação do mundo',
    icon: '\u{1F310}', top: '#efd79c', face: '#cfae6b', ink: '#241d0e',
    reflect: 'O topo não é posse: é entrega. Pessoas íntegras constroem um mundo mais humano.',
    warn: 'Contribuição sem fundação vira ruído passageiro.' },
];

const DIFFICULTIES = {
  aprendiz:   { label: 'Aprendiz',   speed: 150, ramp: 12, tol: 1.35, drain: 0.75 },
  construtor: { label: 'Construtor', speed: 205, ramp: 20, tol: 1.00, drain: 1.00 },
  visionario: { label: 'Visionário', speed: 275, ramp: 30, tol: 0.78, drain: 1.30 },
};

const RANKS = [
  { min: 6000, title: 'Arquiteto do Amanhã' },
  { min: 4200, title: 'Construtor Íntegro' },
  { min: 2600, title: 'Aprendiz Firme' },
  { min: 0,    title: 'Pedreiro de Fundações' },
];

/* ------------------------------------------------------------ constantes -- */

const W = 900, H = 1180;
const GROUND_Y = 985;       // topo da rocha-base
const BLOCK_H  = 78;
const BASE_W   = 620;
const NARROW   = 32;        // quanto cada degrau afina
const CRANE_Y  = 168;
const GRAVITY  = 2600;
const MAX_DRIFT = 130;      // deslocamento máximo da torre em relação ao centro

const PRECISION = [
  { max: 11, key: 'perfeito', label: 'ENCAIXE PERFEITO', bonus: 300, stab: +5, shake: 0 },
  { max: 32, key: 'bom',      label: 'BOM ENCAIXE',      bonus: 150, stab:  0, shake: 2 },
  { max: 58, key: 'torto',    label: 'ENCAIXE TORTO',    bonus:  55, stab: -8, shake: 6 },
];
const TOPPLE_STAB = -22;
const WRONG_STAB  = -26;
const HINT_COST   = 150;

/* --------------------------------------------------------------- estado -- */

const canvas = document.getElementById('stage');
const ctx = canvas.getContext('2d');

const el = {
  hud: document.getElementById('hud'),
  score: document.getElementById('ui-score'),
  step: document.getElementById('ui-step'),
  combo: document.getElementById('ui-combo'),
  stabNum: document.getElementById('ui-stab-num'),
  stabFill: document.getElementById('ui-stab-fill'),
  banner: document.getElementById('banner'),
  bannerTitle: document.getElementById('banner-title'),
  bannerText: document.getElementById('banner-text'),
  controls: document.getElementById('controls'),
  cards: document.getElementById('cards'),
  drop: document.getElementById('btn-drop'),
  hint: document.getElementById('btn-hint'),
  screen: document.getElementById('screen'),
  scEyebrow: document.getElementById('sc-eyebrow'),
  scTitle: document.getElementById('sc-title'),
  scLede: document.getElementById('sc-lede'),
  scBody: document.getElementById('sc-body'),
  scStats: document.getElementById('sc-stats'),
  scAction: document.getElementById('sc-action'),
  scBest: document.getElementById('sc-best'),
  scDiff: document.getElementById('sc-diff'),
  sound: document.getElementById('btn-sound'),
};

const game = {
  phase: 'menu',            // menu | playing | over
  difficulty: 'construtor',
  placed: [],               // blocos já assentados
  candidates: [],           // índices (0..7) oferecidos
  choice: 0,
  falling: null,
  particles: [],
  crane: { x: W / 2, dir: 1 },
  towerX: W / 2,
  towerTopY: GROUND_Y,
  score: 0,
  combo: 0,
  bestCombo: 0,
  perfects: 0,
  mistakes: 0,
  stability: 100,
  hintUntil: 0,
  shake: 0,
  glow: 0,
  bannerUntil: 0,
  won: false,
  t: 0,
};

const best = { score: +(localStorage.getItem('frh.best') || 0) };
let soundOn = localStorage.getItem('frh.sound') !== 'off';

/* ---------------------------------------------------------------- áudio -- */

let actx = null;

function beep(freq, dur = 0.09, type = 'sine', gain = 0.05) {
  if (!soundOn) return;
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    if (actx.state === 'suspended') actx.resume();
    const osc = actx.createOscillator(), g = actx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, actx.currentTime);
    g.gain.setValueAtTime(gain, actx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, actx.currentTime + dur);
    osc.connect(g).connect(actx.destination);
    osc.start();
    osc.stop(actx.currentTime + dur);
  } catch (_) { /* áudio é enfeite: falhar em silêncio */ }
}

const SFX = {
  pick:    () => beep(520, 0.05, 'triangle', 0.03),
  drop:    () => beep(240, 0.07, 'sine', 0.04),
  land:    () => beep(180, 0.12, 'sine', 0.06),
  perfect: () => { beep(660, 0.09, 'triangle', 0.05); setTimeout(() => beep(990, 0.14, 'triangle', 0.045), 80); },
  wrong:   () => beep(110, 0.28, 'sawtooth', 0.05),
  win:     () => [0, 130, 260, 430].forEach((d, i) => setTimeout(() => beep([523, 659, 784, 1047][i], 0.3, 'triangle', 0.05), d)),
  lose:    () => [0, 160, 340].forEach((d, i) => setTimeout(() => beep([330, 262, 175][i], 0.4, 'sawtooth', 0.05), d)),
};

/* ------------------------------------------------------------ utilidades -- */

const cfg = () => DIFFICULTIES[game.difficulty];
const widthOf = (n) => BASE_W - (n - 1) * NARROW;
const nextIndex = () => game.placed.length;          // 0..7 → próximo degrau esperado
const rand = (a, b) => a + Math.random() * (b - a);

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/* --------------------------------------------------------------- fluxo -- */

function start() {
  Object.assign(game, {
    phase: 'playing',
    placed: [], particles: [], falling: null,
    crane: { x: W / 2, dir: 1 },
    towerX: W / 2, towerTopY: GROUND_Y,
    score: 0, combo: 0, bestCombo: 0, perfects: 0, mistakes: 0,
    stability: 100, hintUntil: 0, shake: 0, glow: 0, bannerUntil: 0,
    won: false, t: 0,
  });
  dealCandidates();
  el.screen.classList.add('hidden');
  el.hud.classList.remove('hidden');
  el.controls.classList.remove('hidden');
  syncHud();
  showBanner('Degrau 1', 'Comece pela base: o que sustenta tudo o mais?');
}

/** Sorteia até 3 opções, sempre incluindo o degrau correto. */
function dealCandidates() {
  const correct = nextIndex();
  const others = shuffle(LEVELS.map((_, i) => i).filter((i) => i > correct));
  game.candidates = shuffle([correct, ...others.slice(0, 2)]);
  game.choice = 0;
  renderCards();
}

function renderCards() {
  el.cards.innerHTML = '';
  game.candidates.forEach((li, i) => {
    const L = LEVELS[li];
    const b = document.createElement('button');
    b.className = 'card' + (i === game.choice ? ' is-on' : '');
    b.type = 'button';
    b.innerHTML =
      `<i class="swatch" style="background:${L.face}"></i>` +
      `<span class="idx">OPÇÃO ${i + 1}</span>` +
      `<span class="name">${L.title}</span>` +
      `<span class="desc">${L.desc}</span>`;
    b.addEventListener('click', () => choose(i));
    el.cards.appendChild(b);
  });
  applyHintStyle();
}

function choose(i) {
  if (i < 0 || i >= game.candidates.length || i === game.choice) return;
  game.choice = i;
  [...el.cards.children].forEach((c, k) => c.classList.toggle('is-on', k === i));
  SFX.pick();
}

function cycleChoice(dir) {
  choose((game.choice + dir + game.candidates.length) % game.candidates.length);
}

function useHint() {
  if (game.phase !== 'playing' || game.hintUntil > game.t) return;
  game.hintUntil = game.t + 3;
  game.score = Math.max(0, game.score - HINT_COST);
  syncHud();
  applyHintStyle();
  SFX.pick();
}

function applyHintStyle() {
  const on = game.hintUntil > game.t;
  [...el.cards.children].forEach((c, k) => {
    c.classList.toggle('is-hinted', on && game.candidates[k] === nextIndex());
  });
}

function drop() {
  if (game.phase !== 'playing' || game.falling) return;
  const li = game.candidates[game.choice];
  game.falling = { li, x: game.crane.x, y: CRANE_Y + 34, vy: 0, w: widthOf(LEVELS[li].n) };
  SFX.drop();
  syncHud();
}

function showBanner(title, text, secs = 2.6) {
  el.bannerTitle.textContent = title;
  el.bannerText.textContent = text;
  el.banner.classList.remove('hidden');
  placeBanner();
  el.banner.style.animation = 'none';
  void el.banner.offsetWidth;              // reinicia a animação
  el.banner.style.animation = '';
  game.bannerUntil = game.t + secs;
}

/** Posiciona o banner no espaço vazio entre o bloco içado e o topo da torre. */
function placeBanner() {
  const r = canvas.getBoundingClientRect();
  const gapTop = CRANE_Y + 34 + BLOCK_H + 30;
  const gapY = Math.max(gapTop + 60, (gapTop + game.towerTopY) / 2);
  el.banner.style.top = (r.top + (Math.min(gapY, GROUND_Y - 40) / H) * r.height) + 'px';
}

function land() {
  const f = game.falling;
  const L = LEVELS[f.li];
  game.falling = null;

  // Bloco errado: a ordem é a regra do jogo.
  if (f.li !== nextIndex()) {
    shatter(f.x, game.towerTopY - 20, L.face, 34);
    game.combo = 0;
    game.mistakes++;
    damage(WRONG_STAB);
    game.shake = 14;
    SFX.wrong();
    showBanner('Fora de ordem', L.warn, 3);
    dealCandidates();
    syncHud();
    return;
  }

  const dx = f.x - game.towerX;
  const tol = cfg().tol;
  const grade = PRECISION.find((p) => Math.abs(dx) <= p.max * tol);

  // Desalinhado demais: o bloco tomba.
  if (!grade) {
    shatter(f.x, game.towerTopY - 20, L.face, 26);
    game.combo = 0;
    game.mistakes++;
    damage(TOPPLE_STAB);
    game.shake = 12;
    SFX.wrong();
    showBanner('O bloco tombou', 'Fora do eixo, nada se sustenta. Mire no centro da torre.', 2.4);
    syncHud();
    return;
  }

  // Assentado.
  const clampedX = Math.max(W / 2 - MAX_DRIFT, Math.min(W / 2 + MAX_DRIFT, f.x));
  game.placed.push({ li: f.li, x: clampedX, y: game.towerTopY - BLOCK_H, w: f.w, wob: grade.shake, wobT: 0 });
  game.towerTopY -= BLOCK_H;
  game.towerX = clampedX;

  if (grade.key === 'torto') game.combo = 0;
  else { game.combo++; game.bestCombo = Math.max(game.bestCombo, game.combo); }
  if (grade.key === 'perfeito') game.perfects++;

  const mult = 1 + Math.min(game.combo, 4) * 0.5;
  game.score += Math.round((100 + grade.bonus) * mult);
  damage(grade.stab);
  game.shake = grade.shake;
  game.glow = 1;

  if (grade.key === 'perfeito') SFX.perfect(); else SFX.land();
  showBanner(`${L.n}. ${L.title}${grade.key === 'perfeito' ? ' — ' + grade.label : ''}`, L.reflect, 2.8);

  if (game.placed.length === LEVELS.length) return finish(true);
  dealCandidates();
  syncHud();
}

function damage(delta) {
  const d = delta < 0 ? delta * cfg().drain : delta;
  game.stability = Math.max(0, Math.min(100, game.stability + d));
  if (game.stability <= 0) finish(false);
}

function finish(won) {
  game.phase = 'over';
  game.won = won;
  if (won) {
    game.score += Math.round(game.stability * 20);
    SFX.win();
  } else {
    SFX.lose();
    for (let i = 0; i < 60; i++) {
      const b = game.placed[Math.floor(Math.random() * Math.max(1, game.placed.length))];
      if (b) shatter(b.x + rand(-b.w / 2, b.w / 2), b.y + rand(0, BLOCK_H), LEVELS[b.li].face, 1);
    }
  }
  if (game.score > best.score) {
    best.score = game.score;
    localStorage.setItem('frh.best', String(best.score));
  }
  syncHud();
  setTimeout(() => showEndScreen(won), won ? 900 : 1200);
}

/* --------------------------------------------------------------- telas -- */

function showEndScreen(won) {
  const rank = RANKS.find((r) => game.score >= r.min).title;
  el.hud.classList.add('hidden');
  el.controls.classList.add('hidden');
  el.banner.classList.add('hidden');

  el.scEyebrow.textContent = won ? 'Fundação completa' : 'A torre ruiu';
  el.scTitle.innerHTML = won ? 'Um mundo<br>mais humano' : 'Fundações<br>invisíveis';
  el.scLede.textContent = won
    ? 'Você subiu do SER ao CONTRIBUIR sem pular degraus.'
    : 'Sem base firme, o que está acima não se sustenta. Reconstrua.';

  el.scBody.classList.add('hidden');
  el.scStats.classList.remove('hidden');
  el.scStats.innerHTML =
    `<div class="stat-grid">
       <div class="stat"><b>${game.score}</b><span>pontos</span></div>
       <div class="stat"><b>${game.placed.length}/8</b><span>degraus</span></div>
       <div class="stat"><b>${game.perfects}</b><span>perfeitos</span></div>
     </div>
     <p class="eyebrow" style="margin-bottom:10px">${rank} · melhor combo x${1 + Math.min(game.bestCombo, 4) * 0.5} · ${game.mistakes} erro(s)</p>
     <ul class="ladder">` +
    LEVELS.map((L, i) => {
      const done = i < game.placed.length;
      return `<li class="${done ? '' : 'miss'}">
        <i class="dot" style="background:${L.face}"></i>
        <span class="n">${L.n}</span>
        <span class="t">${L.title}</span>
        <span class="s">— ${L.desc}</span>
      </li>`;
    }).join('') + '</ul>';

  el.scAction.textContent = won ? 'Construir de novo' : 'Tentar de novo';
  el.scBest.textContent = best.score;
  el.screen.classList.remove('hidden');
}

function syncHud() {
  el.score.textContent = game.score;
  el.step.textContent = Math.min(game.placed.length + 1, 8);
  el.combo.textContent = 'x' + (1 + Math.min(game.combo, 4) * 0.5);
  el.stabNum.textContent = Math.round(game.stability) + '%';
  el.stabFill.style.width = game.stability + '%';
  el.stabFill.classList.toggle('low', game.stability <= 35);
  el.drop.disabled = !!game.falling;
}

/* ---------------------------------------------------------- partículas -- */

function shatter(x, y, color, n) {
  for (let i = 0; i < n; i++) {
    game.particles.push({
      x, y, color,
      vx: rand(-260, 260), vy: rand(-420, -60),
      size: rand(4, 13), rot: rand(0, 6.3), vr: rand(-9, 9), life: rand(0.7, 1.5),
    });
  }
}

/* ------------------------------------------------------------ simulação -- */

function update(dt) {
  game.t += dt;
  if (game.bannerUntil && game.t > game.bannerUntil) {
    el.banner.classList.add('hidden');
    game.bannerUntil = 0;
  }
  if (game.hintUntil && game.t > game.hintUntil) { game.hintUntil = 0; applyHintStyle(); }

  game.shake = Math.max(0, game.shake - dt * 26);
  game.glow = Math.max(0, game.glow - dt * 1.6);

  if (game.phase === 'playing') {
    // guindaste
    const c = cfg();
    const speed = c.speed + game.placed.length * c.ramp;
    const half = widthOf(LEVELS[game.candidates[game.choice]].n) / 2;
    const left = 70 + half, right = W - 70 - half;
    game.crane.x += game.crane.dir * speed * dt;
    if (game.crane.x < left)  { game.crane.x = left;  game.crane.dir = 1; }
    if (game.crane.x > right) { game.crane.x = right; game.crane.dir = -1; }

    // bloco em queda
    const f = game.falling;
    if (f) {
      f.vy += GRAVITY * dt;
      f.y += f.vy * dt;
      if (f.y + BLOCK_H >= game.towerTopY) { f.y = game.towerTopY - BLOCK_H; land(); syncHud(); }
    }
  }

  // oscilação dos blocos tortos
  for (const b of game.placed) {
    if (b.wob > 0.02) { b.wobT += dt * 12; b.wob *= 1 - dt * 1.8; }
  }

  // partículas
  for (let i = game.particles.length - 1; i >= 0; i--) {
    const p = game.particles[i];
    p.vy += 1500 * dt;
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.rot += p.vr * dt;
    p.life -= dt;
    if (p.life <= 0 || p.y > H + 60) game.particles.splice(i, 1);
  }
}

/* ------------------------------------------------------------- desenho -- */

function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function drawBackground() {
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#c9d6de');
  sky.addColorStop(0.32, '#e6e2d6');
  sky.addColorStop(0.62, '#cdd3cd');
  sky.addColorStop(1, '#5f6a68');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, W, H);

  // brilho do amanhecer no topo
  const glow = ctx.createRadialGradient(W / 2, 40, 10, W / 2, 40, 470);
  glow.addColorStop(0, `rgba(255, 238, 196, ${0.34 + game.glow * 0.18})`);
  glow.addColorStop(0.55, `rgba(255, 238, 196, ${0.12 + game.glow * 0.08})`);
  glow.addColorStop(1, 'rgba(255, 238, 196, 0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, 560);

  // montanhas distantes
  const ridge = (baseY, height, color, seed) => {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(-20, H);
    ctx.lineTo(-20, baseY);
    for (let x = -20; x <= W + 20; x += 30) {
      const y = baseY - Math.abs(Math.sin((x + seed) * 0.0045) * Math.cos((x + seed) * 0.0017)) * height;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(W + 20, H);
    ctx.closePath();
    ctx.fill();
  };
  ridge(620, 240, 'rgba(120, 137, 148, .42)', 120);
  ridge(720, 200, 'rgba(86, 102, 111, .5)', 640);
  ridge(830, 150, 'rgba(58, 70, 76, .62)', 240);

  // vale e chão
  const ground = ctx.createLinearGradient(0, GROUND_Y - 120, 0, H);
  ground.addColorStop(0, '#4a5450');
  ground.addColorStop(1, '#232a2b');
  ctx.fillStyle = ground;
  ctx.beginPath();
  ctx.moveTo(0, GROUND_Y + 6);
  ctx.quadraticCurveTo(W / 2, GROUND_Y - 34, W, GROUND_Y + 6);
  ctx.lineTo(W, H);
  ctx.lineTo(0, H);
  ctx.closePath();
  ctx.fill();

  // vinheta
  const vig = ctx.createRadialGradient(W / 2, H * 0.45, H * 0.3, W / 2, H * 0.5, H * 0.78);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(8,11,14,.5)');
  ctx.fillStyle = vig;
  ctx.fillRect(0, 0, W, H);
}

function drawPlinth() {
  const w = BASE_W + 90, x = W / 2 - w / 2, y = GROUND_Y, h = 52;
  ctx.fillStyle = 'rgba(0,0,0,.32)';
  ctx.beginPath();
  ctx.ellipse(W / 2, y + h + 12, w / 2 + 30, 22, 0, 0, Math.PI * 2);
  ctx.fill();

  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, '#3d4348');
  g.addColorStop(1, '#20252a');
  ctx.fillStyle = g;
  roundRect(x, y, w, h, 8);
  ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.1)';
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = 'rgba(244, 241, 234, .5)';
  ctx.font = '13px ui-sans-serif, system-ui, sans-serif';
  ctx.letterSpacing = '7px';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('FUNDAÇÃO', W / 2, y + h / 2 + 1);
  ctx.letterSpacing = '0px';
}

function drawBlock(L, cx, y, w, opts = {}) {
  const h = BLOCK_H, depth = 15;
  const x = cx - w / 2;
  ctx.save();
  if (opts.angle) {
    ctx.translate(cx, y + h);
    ctx.rotate(opts.angle);
    ctx.translate(-cx, -(y + h));
  }
  ctx.globalAlpha = opts.alpha != null ? opts.alpha : 1;

  // sombra projetada
  ctx.fillStyle = 'rgba(10,14,18,.3)';
  roundRect(x + 6, y + 10, w, h, 7);
  ctx.fill();

  // face frontal
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, L.top);
  g.addColorStop(0.55, L.face);
  g.addColorStop(1, L.face);
  ctx.fillStyle = g;
  roundRect(x, y, w, h, 7);
  ctx.fill();

  // topo em perspectiva
  ctx.fillStyle = L.top;
  ctx.beginPath();
  ctx.moveTo(x + 5, y);
  ctx.lineTo(x + w - 5, y);
  ctx.lineTo(x + w - 5 - depth, y - depth * 0.62);
  ctx.lineTo(x + 5 + depth, y - depth * 0.62);
  ctx.closePath();
  ctx.fill();

  ctx.strokeStyle = 'rgba(255,255,255,.28)';
  ctx.lineWidth = 1;
  roundRect(x, y, w, h, 7);
  ctx.stroke();

  // número + divisória (só no bloco já assentado: o carregado não entrega a ordem)
  ctx.fillStyle = L.ink;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  ctx.globalAlpha = (opts.alpha != null ? opts.alpha : 1) * 0.75;
  ctx.font = '600 26px "Iowan Old Style", Georgia, serif';
  ctx.fillText(opts.number ? String(L.n) : '?', x + 30, y + h / 2);
  ctx.globalAlpha = (opts.alpha != null ? opts.alpha : 1) * 0.35;
  ctx.fillRect(x + 50, y + 18, 1, h - 36);
  ctx.globalAlpha = opts.alpha != null ? opts.alpha : 1;

  // ícone
  ctx.font = '30px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
  ctx.fillText(L.icon, x + 84, y + h / 2);

  // título e descrição
  const tx = x + w / 2 + 22;
  ctx.fillStyle = L.ink;
  ctx.font = '700 27px "Iowan Old Style", Georgia, serif';
  ctx.letterSpacing = '2px';
  ctx.fillText(L.title, tx, y + h / 2 - 12);
  ctx.letterSpacing = '0px';
  ctx.globalAlpha = (opts.alpha != null ? opts.alpha : 1) * 0.78;
  ctx.font = '16px "Iowan Old Style", Georgia, serif';
  ctx.fillText(L.desc, tx, y + h / 2 + 16);
  ctx.restore();
}

function drawCrane() {
  const li = game.candidates[game.choice];
  if (li == null) return;
  const L = LEVELS[li];
  const w = widthOf(L.n);
  const x = game.crane.x;

  // trilho
  ctx.strokeStyle = 'rgba(30,36,42,.45)';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(40, CRANE_Y - 26);
  ctx.lineTo(W - 40, CRANE_Y - 26);
  ctx.stroke();

  // carro + cabos
  ctx.fillStyle = '#2b3238';
  roundRect(x - 26, CRANE_Y - 40, 52, 26, 5);
  ctx.fill();
  ctx.strokeStyle = 'rgba(30,36,42,.7)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x - 16, CRANE_Y - 14); ctx.lineTo(x - 16, CRANE_Y + 34);
  ctx.moveTo(x + 16, CRANE_Y - 14); ctx.lineTo(x + 16, CRANE_Y + 34);
  ctx.stroke();

  if (!game.falling) {
    drawBlock(L, x, CRANE_Y + 34, w, { angle: Math.sin(game.t * 2.2) * 0.012 });
    // linha de mira
    ctx.save();
    ctx.setLineDash([7, 11]);
    ctx.strokeStyle = 'rgba(255, 252, 240, .5)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, CRANE_Y + 34 + BLOCK_H);
    ctx.lineTo(x, game.towerTopY - 6);
    ctx.stroke();
    ctx.restore();
  }

  // marcador do centro da torre
  ctx.fillStyle = 'rgba(255, 252, 240, .55)';
  ctx.beginPath();
  ctx.moveTo(game.towerX, game.towerTopY - 30);
  ctx.lineTo(game.towerX - 9, game.towerTopY - 46);
  ctx.lineTo(game.towerX + 9, game.towerTopY - 46);
  ctx.closePath();
  ctx.fill();
}

function draw() {
  ctx.save();
  if (game.shake > 0.2) {
    ctx.translate(rand(-game.shake, game.shake), rand(-game.shake, game.shake));
  }

  drawBackground();
  drawPlinth();

  for (const b of game.placed) {
    const angle = b.wob > 0.02 ? Math.sin(b.wobT) * b.wob * 0.004 : 0;
    drawBlock(LEVELS[b.li], b.x, b.y, b.w, { angle, number: true });
  }

  if (game.phase === 'playing') {
    drawCrane();
    if (game.falling) {
      const f = game.falling;
      drawBlock(LEVELS[f.li], f.x, f.y, f.w);
    }
  }

  // partículas
  for (const p of game.particles) {
    ctx.save();
    ctx.globalAlpha = Math.max(0, Math.min(1, p.life));
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rot);
    ctx.fillStyle = p.color;
    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
    ctx.restore();
  }

  // raio de luz na vitória
  if (game.phase === 'over' && game.won) {
    const g = ctx.createLinearGradient(0, 0, 0, GROUND_Y);
    g.addColorStop(0, 'rgba(255, 233, 176, .55)');
    g.addColorStop(1, 'rgba(255, 233, 176, 0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(W / 2 - 40, 0);
    ctx.lineTo(W / 2 + 40, 0);
    ctx.lineTo(game.towerX + 240, game.towerTopY);
    ctx.lineTo(game.towerX - 240, game.towerTopY);
    ctx.closePath();
    ctx.fill();
  }

  ctx.restore();
}

/* --------------------------------------------------------------- laço -- */

let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  update(dt);
  draw();
  requestAnimationFrame(frame);
}

/* --------------------------------------------------------- interação -- */

function resize() {
  const pad = 0;
  const scale = Math.min((window.innerWidth - pad) / W, (window.innerHeight - pad) / H);
  canvas.style.width = Math.floor(W * scale) + 'px';
  canvas.style.height = Math.floor(H * scale) + 'px';
  if (game.bannerUntil) placeBanner();
}

window.addEventListener('resize', resize);
resize();

document.addEventListener('keydown', (e) => {
  if (e.key === 's' || e.key === 'S') return toggleSound();
  if (game.phase !== 'playing') {
    if (e.code === 'Space' || e.key === 'Enter') { e.preventDefault(); el.scAction.click(); }
    return;
  }
  if (e.code === 'Space') { e.preventDefault(); drop(); }
  else if (e.key === 'ArrowLeft')  cycleChoice(-1);
  else if (e.key === 'ArrowRight') cycleChoice(1);
  else if (e.key >= '1' && e.key <= '3') choose(+e.key - 1);
  else if (e.key === 'h' || e.key === 'H') useHint();
});

canvas.addEventListener('pointerdown', () => { if (game.phase === 'playing') drop(); });
el.drop.addEventListener('click', drop);
el.hint.addEventListener('click', useHint);

el.scDiff.addEventListener('click', (e) => {
  const b = e.target.closest('.diff');
  if (!b) return;
  game.difficulty = b.dataset.diff;
  [...el.scDiff.children].forEach((c) => c.classList.toggle('is-on', c === b));
});

el.scAction.addEventListener('click', () => {
  el.scBody.classList.remove('hidden');
  el.scStats.classList.add('hidden');
  start();
});

function toggleSound() {
  soundOn = !soundOn;
  localStorage.setItem('frh.sound', soundOn ? 'on' : 'off');
  el.sound.classList.toggle('off', !soundOn);
  if (soundOn) SFX.pick();
}
el.sound.addEventListener('click', toggleSound);
el.sound.classList.toggle('off', !soundOn);

el.scBest.textContent = best.score;
requestAnimationFrame(frame);
})();
