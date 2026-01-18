# numerical-natsim-project

Numerical methods project implementing a discrete-time simulation of a predator–prey system
with spatial structure.

The project models interactions between wolves and rabbits on a two-dimensional grid,
including movement, hunting, reproduction, starvation, and shelter behavior.
The system evolution is visualized using an animated representation.

## Project Goal

The goal of this project is to study predator–prey dynamics using numerical simulation
methods with discrete time and space.

Instead of directly solving continuous differential equations, the model is based on
an agent-based approach, allowing local interactions, stochastic behavior, and
emergent spatial patterns.

## Model Description

The environment is represented as a two-dimensional grid with periodic boundary
conditions.

### Agents

**Wolves (predators):**
- Move across the grid searching for rabbits
- Hunt rabbits outside their shelters
- Accumulate food required for reproduction
- Starve if no food is consumed for a fixed number of time steps
- Reproduce only near the wolf den

**Rabbits (prey):**
- Move randomly while foraging
- Detect nearby wolves and escape to their burrows
- Accumulate food and reproduce when sufficient food is collected
- Are protected from predators while inside burrows

### Shelters

- A single wolf den located near the center of the grid
- Multiple rabbit burrows distributed across the environment

## Numerical Aspects

- Time is discretized into equal steps (Δt = 1)
- Agent states are updated synchronously at each time step
- Stochastic elements are introduced through random movement and encounters
- The model can be interpreted as a spatial, stochastic analogue of the
  Lotka–Volterra predator–prey system

## Visualization

The simulation is visualized using Matplotlib animation.
Custom drawing routines are used to represent agents and shelters,
as well as a dynamically generated background.

The animation displays:
- Spatial distribution of agents
- Population sizes over time
- Real-time simulation step information

