# Sweet Party — Game Engine

7x7 cluster-pays cascade slot game. Reference: [Fruit Party (Pragmatic Play)](https://www.pragmaticplay.com/en/games/fruit-party-slot/).

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
- **Max multiplier product:** 1024x

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

## Symbol Multipliers

Every paying symbol (h1-h7) has a random chance to carry a **2x** or **4x** multiplier on both the initial board reveal and each tumble cascade.

- **Probability:** 5% per symbol
- **Distribution:** Weighted selection between 2x (75%) and 4x (25%)
- **Application:** When a winning cluster forms, all multipliers within the cluster are **multiplied together** (product, not sum)
- **Cap:** The product of multipliers is capped at **1024x**
- **Formula:** `cluster_win = paytable_win × multiplier_product`
- **Scatter exclusion:** Scatter symbols ("S") never receive multipliers

## Gold X-Tile

A special board position that grants multipliers to an entire winning cluster when any symbol from that cluster lands on the tile. **Only spawns during free spins (BONUS mode), never in base game.**

- **Spawn:** 10% chance to spawn once per free spin (rolled after the initial board draw, not re-rolled on tumbles)
- **Limit:** At most 1 X-Tile on the board at any time
- **Persists:** The X-Tile stays on the board through all tumble cascades until the free spin iteration ends
- **Not consumed:** When a winning cluster overlaps the X-Tile, the tile remains — it can affect clusters on every tumble
- **Effect:** Every symbol in an overlapping cluster that does NOT already have a native multiplier gets an independent random 2x or 4x (same weighted distribution as native multipliers: 75% for 2x, 25% for 4x)
- **Multiple clusters:** If multiple winning clusters overlap the X-Tile in the same evaluation, all of them receive multipliers
- **Events:** `xTileSpawn` (with position) and `xTileApply` (with cluster info, emitted per affected cluster)

## Game Flow

### Base Game Spin

```
1. Draw board from reel strips
2. Detect clusters (5+ adjacent matching symbols)
3. Calculate wins from paytable (including multiplier products)
4. Mark winning symbols for removal
5. WHILE there are wins AND wincap not hit:
   a. Tumble: remove winning symbols, cascade new ones from above
   b. Detect new clusters
   c. Calculate wins
6. Check for freespin trigger (3+ scatters)
7. If triggered, run BONUS freespin feature (8 spins)
8. Finalize win (capped at 10,000x)
```

### BONUS (Free Spins)

Triggered by landing 3+ scatter symbols on the initial base game board. Awards **8 free spins**.

Each free spin follows the same cascade flow as the base game, plus:
- **Gold X-Tile:** 10% chance to spawn once per free spin; persists through all tumbles
- **Retrigger:** Landing 3+ scatters during a free spin awards extra spins:

| Scatters | Extra Spins |
| -------- | ----------- |
| 3        | +6          |
| 4        | +8          |
| 5        | +10         |
| 6        | +12         |
| 7        | +14         |

Scatter counts above 7 are capped to 7 for retrigger lookups.

## Bet Modes

| Mode       | Cost       | Description                                                  |
| ---------- | ---------- | ------------------------------------------------------------ |
| base       | 1x         | Standard play. 3+ scatters trigger BONUS (8 free spins)     |
| FEATURE_5X | 3x         | 5x higher chance of landing scatter symbols (bonus trigger)  |
| BONUS      | 100x       | Direct buy into 8 free spins with 10% X-Tile chance per spin |

**base** and **feature_5x** are implemented. BONUS buy is not yet implemented.

### Simulation Distributions

**base mode:**

| Criteria | Quota | Description                                     |
| -------- | ----- | ----------------------------------------------- |
| wincap   | 0.1%  | Forces freespin trigger + wincap hit at 10,000x |
| freegame | 10%   | Forces freespin trigger                         |
| 0        | 40%   | Guarantees zero-win outcome                     |
| basegame | 49.9% | Normal gameplay                                 |

**feature_5x mode** (cost: 3x, 5x freespin trigger rate):

| Criteria | Quota | Description                                     |
| -------- | ----- | ----------------------------------------------- |
| wincap   | 0.1%  | Forces freespin trigger + wincap hit at 10,000x |
| freegame | 50%   | Forces freespin trigger (5x base rate)          |
| 0        | 20%   | Guarantees zero-win outcome                     |
| basegame | 29.9% | Normal gameplay                                 |

## Reel Strips

| Strip | Rows | Scatters/Reel | Usage                                          |
| ----- | ---- | ------------- | ---------------------------------------------- |
| BR0   | 70   | 1-3           | Base game                                      |
| FR0   | 80   | 1-2           | Free game                                      |
| WCAP  | 42   | 0             | Wincap forcing (freegame) — h1/h2 heavy, no scatters |

## Edge Cases

- **Clusters > 15 symbols:** Pay at the size-15 rate. Actual cluster size is preserved in win event data.
- **Scatters > 7:** Capped to 7 for retrigger lookups.
- **Wincap during cascade:** Cascade terminates immediately when running win reaches 10,000x.
- **Repeat validation:** Spins that fail their distribution criteria (e.g., forced freegame but no trigger, zero-criteria but non-zero win) are re-drawn.

## Running

```bash
cd games/sweet_party
python run.py
```

Configuration in `run.py`:

- `num_threads`: parallel simulation threads (default: 10)
- `num_sim_args`: simulation count per bet mode
- `run_conditions`: toggle sims, optimization, analysis, format checks

### Monte Carlo Pipeline

```bash
cd games/sweet_party
PYTHONPATH=../.. python monte_carlo.py --spins 100000 --threads 10
```

Runs the full pipeline: simulation → Rust optimization → PAR sheet analysis → report.

## File Structure

```
games/sweet_party/
  game_config.py        # Paytable, symbols, triggers, bet modes, reel loading
  gamestate.py          # Main spin loop and freespin loop
  game_calculations.py  # Cluster evaluation with size capping
  game_executables.py   # Cluster detection, scatter capping, freespin updates
  game_override.py      # State resets, repeat validation
  game_events.py        # X-Tile spawn/apply events
  game_optimization.py  # RTP optimization parameters
  monte_carlo.py        # Full Monte Carlo pipeline (sim + optimize + analyze)
  run.py                # Entry point
  reels/
    BR0.csv             # Base game reel strip
    FR0.csv             # Free game reel strip
    WCAP.csv            # Wincap reel strip (high-value, no scatters)
```
