# Fundação da Realização Humana — o jogo

Jogo de navegador (HTML + Canvas, sem dependências) inspirado no infográfico
*Fundação da Realização Humana*: uma torre de oito degraus que vai do **SER** ao
**CONTRIBUIR**.

A tese do infográfico vira a regra do jogo: **cada degrau só se sustenta sobre o
que vem antes**. Amplificar com tecnologia o que ainda não foi organizado
derruba a torre; agir antes de pensar também.

## Como jogar

Abra `game/index.html` no navegador — ou sirva a pasta:

```bash
python3 -m http.server 8000 --directory game
# http://localhost:8000
```

1. Escolha, entre as opções oferecidas, **qual é o próximo degrau da fundação**.
2. O guindaste vai e volta no topo. Solte o bloco quando ele estiver alinhado
   com o centro da torre (a seta dourada marca o eixo).
3. Encaixe perfeito rende bônus e combo; encaixe torto, erro de ordem ou bloco
   tombado consomem **estabilidade**. Se ela zerar, a torre rui.
4. Complete os oito degraus para fechar a fundação — o placar final soma a
   estabilidade que sobrou.

### Controles

| Ação | Teclado | Toque |
| --- | --- | --- |
| Escolher bloco | `1` `2` `3` ou `←` `→` | tocar no cartão |
| Soltar bloco | `espaço` | tocar na cena ou em *Soltar bloco* |
| Consultar a ordem (dica, −150 pontos) | `H` | botão *Consultar a ordem* |
| Ligar/desligar som | `S` | botão ♪ |

Três dificuldades (Aprendiz / Construtor / Visionário) mudam a velocidade do
guindaste, a tolerância de encaixe e o peso das penalidades. A melhor pontuação
fica salva no `localStorage`.

## Os oito degraus

| # | Degrau | |
| --- | --- | --- |
| 1 | SER | caráter, consciência, presença |
| 2 | ORIENTAR-SE | Verdadeiro • Bom • Belo • Sentido |
| 3 | RELACIONAR-SE | amor, amizade, comunidade, serviço |
| 4 | PENSAR | razão, filosofia, pensamento computacional |
| 5 | AGIR | prudência, coragem, disciplina |
| 6 | ORGANIZAR | pessoas, processos, projetos, plataformas |
| 7 | AMPLIFICAR | tecnologia e IA |
| 8 | CONTRIBUIR | obra, legado, transformação do mundo |

## Arquivos

- `index.html` — marcação, HUD e telas de início/fim
- `style.css` — estilo (tema claro impresso nas telas, cena escura no jogo)
- `game.js` — dados dos degraus, regras, física e desenho no canvas

Cada acerto revela a reflexão do degrau; cada erro explica por que aquele bloco
ainda não podia ser posto. Sem dependências, sem build, sem rede.
