# Sweet Party — Game Engine

7x7 cluster-pays cascade slot game.

## Current State: Vanilla

The engine implements the core gameplay loop without multipliers, Gold X-Tile, or buy modes. These will be layered on in future iterations.

## Symbols

| Symbol | Type    | Min Cluster Pay (5) | Max Cluster Pay (15) |
| ------ | ------- | ------------------- | -------------------- |
| h1     | Regular | 2.0x                | 300.0x               |
| h2     | Regular | 1.5x                | 200.0x               |
| h3     | Regular | 1.0x                | 180.0x               |
| h4     | Regular | 0.8x                | 160.0x               |
| h5     | Regular | 0.6x                | 120.0x               |
| h6     | Regular | 0.5x                | 80.0x                |
| h7     | Regular | 0.4x                | 40.0x                |
| S      | Scatter | —                   | —                    |

No wild symbols in this game.

## Core Rules

- **Grid:** 7 reels x 7 rows
- **Win Type:** Cluster pays (5+ adjacent matching symbols, orthogonal only)
- **Wincap:** 10,000x base bet
- **Target RTP:** 96%
- **Cluster size cap:** Clusters larger than 15 pay at the size-15 rate

## Paytable

Payouts are in multiples of base bet.

| Size | h1    | h2    | h3    | h4    | h5    | h6   | h7   |
| ---- | ----- | ----- | ----- | ----- | ----- | ---- | ---- |
| 5    | 2.0   | 1.5   | 1.0   | 0.8   | 0.6   | 0.5  | 0.4  |
| 6    | 3.0   | 2.0   | 1.5   | 1.0   | 0.8   | 0.6  | 0.5  |
| 7    | 3.5   | 2.5   | 2.0   | 1.5   | 1.0   | 0.8  | 0.6  |
| 8    | 4.0   | 3.0   | 2.5   | 2.0   | 1.5   | 1.0  | 0.8  |
| 9    | 5.0   | 4.0   | 3.0   | 2.5   | 2.0   | 1.5  | 1.0  |
| 10   | 10.0  | 8.0   | 6.0   | 4.0   | 3.0   | 2.5  | 2.0  |
| 11   | 15.0  | 12.0  | 9.0   | 6.0   | 5.0   | 4.0  | 3.0  |
| 12   | 30.0  | 25.0  | 20.0  | 10.0  | 7.0   | 6.0  | 5.0  |
| 13   | 70.0  | 60.0  | 50.0  | 40.0  | 30.0  | 20.0 | 10.0 |
| 14   | 140.0 | 120.0 | 100.0 | 80.0  | 60.0  | 40.0 | 20.0 |
| 15+  | 300.0 | 200.0 | 180.0 | 160.0 | 120.0 | 80.0 | 40.0 |

## Game Flow

### Base Game Spin

```
1. Draw board from reel strips
2. Detect clusters (5+ adjacent matching symbols)
3. Calculate wins from paytable
4. Mark winning symbols for removal
5. WHILE there are wins AND wincap not hit:
   a. Tumble: remove winning symbols, cascade new ones from above
   b. Detect new clusters
   c. Calculate wins
6. Check for freespin trigger (3+ scatters)
7. If triggered, run freespin feature
8. Finalize win (capped at 10,000x)
```

### Freespin Feature

Triggered by landing 3+ scatter symbols on the initial board (before cascades).

**Initial spins awarded (from base game):**

| Scatters | Spins | Type        |
| -------- | ----- | ----------- |
| 3        | 8     | BONUS       |
| 4        | 10    | SUPER_BONUS |
| 5        | 11    | SUPER_BONUS |
| 6        | 12    | SUPER_BONUS |
| 7        | 13    | SUPER_BONUS |

**Retrigger (during freespins):**

| Scatters | Extra Spins |
| -------- | ----------- |
| 3        | +6          |
| 4        | +8          |
| 5        | +10         |
| 6        | +12         |
| 7        | +14         |

Each freespin follows the same cascade flow as the base game. Scatter counts above 7 are capped to 7 for trigger lookups.

## Bet Modes

Currently only the **base** mode is implemented (cost: 1x base bet).

### Simulation Distributions

| Criteria | Quota | Description                                     |
| -------- | ----- | ----------------------------------------------- |
| wincap   | 0.1%  | Forces freespin trigger + wincap hit at 10,000x |
| freegame | 10%   | Forces freespin trigger                         |
| 0        | 40%   | Guarantees zero-win outcome                     |
| basegame | 49.9% | Normal gameplay                                 |

## Reel Strips

Placeholder strips are currently in place. These need optimization tuning to hit the 96% RTP target.

| Strip | Rows | Scatters/Reel | Usage                     |
| ----- | ---- | ------------- | ------------------------- |
| BR0   | 70   | 2             | Base game                 |
| FR0   | 80   | 1             | Free game                 |
| WCAP  | 42   | 5             | Wincap forcing (freegame) |

## Edge Cases

- **Clusters > 15 symbols:** Pay at the size-15 rate. Actual cluster size is preserved in win event data.
- **Scatters > 7:** Capped to 7 for freespin trigger/retrigger lookups.
- **Wincap during cascade:** Cascade terminates immediately when running win reaches 10,000x.
- **Repeat validation:** Spins that fail their distribution criteria (e.g., forced freegame but no trigger, zero-criteria but non-zero win) are re-drawn.

## Not Yet Implemented

The following features from the spec are planned for future iterations:

- **Symbol multipliers:** Random 2x/4x multipliers on individual symbols
- **Gold X-Tile:** Board position that grants multipliers to clusters landing on it
- **Maximum multiplier product cap:** 1,024x
- **Buy modes:** FEATURE_5X (3x cost), FEATURE_Cluster Drop (25x), FEATURE_Max Multi Tile (500x)
- **BONUS buy:** 100x cost, direct entry to 8 free spins with 10% X-Tile chance per spin
- **SUPER_BONUS buy:** 300x cost, direct entry to free spins with guaranteed X-Tile per spin
- **BONUS/SUPER_BONUS differentiation:** Currently both use the same freespin flow; future work will add X-Tile mechanics that distinguish them

## Running

```bash
cd games/sweet_party
python run.py
```

Configuration in `run.py`:

- `num_threads`: parallel simulation threads (default: 10)
- `num_sim_args`: simulation count per bet mode
- `run_conditions`: toggle sims, optimization, analysis, format checks

## File Structure

```
games/sweet_party/
  game_config.py        # Paytable, symbols, triggers, bet modes, reel loading
  gamestate.py          # Main spin loop and freespin loop
  game_calculations.py  # Cluster evaluation with size capping
  game_executables.py   # Cluster detection, scatter capping, freespin updates
  game_override.py      # State resets, repeat validation
  game_events.py        # Game-specific events (placeholder)
  game_optimization.py  # RTP optimization parameters
  run.py                # Entry point
  reels/
    BR0.csv             # Base game reel strip
    FR0.csv             # Free game reel strip
    WCAP.csv            # Wincap reel strip
```
