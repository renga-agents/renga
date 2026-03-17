---
applyTo: "**/animations/**,**/canvas/**,**/three/**,**/r3f/**,**/shaders/**,**/scenes/**,**/game/**,**/phaser/**,**/*.glsl,**/*.frag,**/*.vert,**/*.vs,**/*.fs"
---

# Animations & 3D Conventions

> **Three distinct technical regimes** — each with its own tools, performance constraints,
> and use cases. Choose the right regime **before** writing the first line of code.

---

## Choose your regime

| Context | Recommended stack | Selection criterion |
| --- | --- | --- |
| **Marketing site** | Spline + GSAP + ScrollTrigger | Short timeline, design-heavy team, turnkey WebGL rendering |
| **Immersive React app** | R3F + Drei + GSAP | Integrated React interface, complex 3D scenes, optimal DX |
| **Full control / shaders (web)** | Plain Three.js or OGL | Custom shaders, minimal bundle, web 3D experiences — **not for games** |
| **2D video game** | Phaser 3 | Game scene graph, physics, tilemaps, input, spritesheet animations |
| **3D video game** | Babylon.js | Full game engine: Havok physics, GUI, animation FSM, inspector |

> [!IMPORTANT]
> Never mix R3F and imperative Three.js inside the same canvas. R3F owns the renderer
> and the loop. Any external manipulation must go through R3F hooks such as `useThree`
> and `useFrame`.

> [!IMPORTANT]
> **Three.js ≠ Babylon.js**: Three.js is a web 3D rendering library for visualizations,
> experiences, and shaders. Babylon.js is a full game engine with built-in physics, GUI,
> input handling, animation FSMs, an optimizer, and an inspector. Do not use Three.js
> for a 3D game. Choose Babylon.js.

> [!IMPORTANT]
> Any code example involving a third-party library **must** be preceded by a call to
> `mcp_context7_resolve-library-id` and `mcp_context7_get-library-docs` before generation.
> If context7 is unavailable, annotate each example with
> `⚠️ context7 unavailable for <lib>`.

---

## Regime 1 — Marketing site: Spline + GSAP + ScrollTrigger

### Philosophy

Spline handles 3D visually through a no-code/low-code tool, GSAP drives page transitions,
and ScrollTrigger synchronizes animations with scroll. This regime maximizes design/dev
velocity without sacrificing visual quality.

### When to choose this regime

| Criterion | Marketing site ✅ | Other regime |
| --- | --- | --- |
| Strong design team, limited shader skills | ✅ | — |
| 3D scenes edited visually | ✅ | — |
| Critical TTI (< 3s) | With lazy loading ✅ | R3F if full control is needed |
| Complex scroll-driven animations | ✅ | — |
| Rich interactive scenes with physics/GPU logic | ❌ | R3F or Three.js |

### Installation

```bash

npm install @splinetool/react-spline @splinetool/runtime
npm install gsap @gsap/react

```

> [!NOTE]
> Reference versions (March 2026, verified on npm):
> `gsap` **3.14.2** · `@gsap/react` **2.1.2** · `@splinetool/react-spline` **4.1.0** · `@splinetool/runtime` **1.12.67**

### Spline integration in Next.js 16

> ⚠️ context7 unavailable for `@splinetool/react-spline` and `@splinetool/runtime`
> — examples based on training knowledge (v4.1.0 / v1.12.67), verify before use.
>
> ### Known public `Application` API (`@splinetool/runtime` v1.x):
>
> `findObjectByName(name)`, `findObjectById(uuid)`,
> `emitEvent(eventName, nameOrUuid)`, `emitEventReverse(eventName, nameOrUuid)`,
> `setZoom(zoom)`.
> There is **no** `setVariable` method in the public API.

```tsx

// components/animations/HeroScene.tsx
'use client' // Spline uses browser APIs

import { Suspense, useRef } from 'react'
import type { Application } from '@splinetool/runtime'

// Next.js: import from /next to get a server-rendered blurred placeholder
// (export the scene as "Next.js" from the Spline editor to generate it)
import Spline from '@splinetool/react-spline/next'

export function HeroScene() {
  const splineApp = useRef<Application | null>(null)

  function onLoad(spline: Application) {
    // Save the application reference for later use
    splineApp.current = spline
  }

  function triggerHoverAnimation() {
    // Trigger a Spline event by object name
    splineApp.current?.emitEvent('mouseHover', 'HeroObject')
  }

  return (
    // Suspense is required — the 3D scene loads asynchronously
    <Suspense fallback={<HeroSkeleton />}>
      <Spline
        scene="https://prod.spline.design/<scene-id>/scene.splinecode"
        onLoad={onLoad}
        className="w-full h-full"
      />
    </Suspense>
  )
}

function HeroSkeleton() {
  return <div className="w-full h-full animate-pulse bg-neutral-100" aria-hidden />
}

```

```tsx

// Interacting with scene objects
import { useRef } from 'react'
import type { Application } from '@splinetool/runtime'
import Spline from '@splinetool/react-spline/next'

export function InteractiveScene() {
  const cubeRef = useRef<ReturnType<Application['findObjectByName']>>(null)

  function onLoad(spline: Application) {
    // Query an object by name and save the reference
    const obj = spline.findObjectByName('Cube')
    // or: spline.findObjectById('8E8C2DDD-18B6-4C54-861D-7ED2519DE20E')
    cubeRef.current = obj ?? null
  }

  function moveObject() {
    if (!cubeRef.current) return
    // Directly mutate the object's position
    cubeRef.current.position.x += 10
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode"
        onLoad={onLoad}
      />
      <button type="button" onClick={moveObject} data-testid="move-cube">
        Move Cube
      </button>
    </div>
  )
}

```

> [!TIP]
> For Next.js App Router **without** an SSR placeholder, lazy-load with `next/dynamic`:
>
> ```tsx
>
> const SplineScene = dynamic(() => import('@/components/animations/HeroScene'), { ssr: false })
>
> ```

> [!TIP]
> Host `.splinecode` assets on the Spline CDN instead of in the repository. Those files can
> weigh several MB. If you hit a CORS error, download the file and self-host it.

### GSAP — global configuration

> ⚠️ context7 unavailable for `gsap` and `@gsap/react`
> — examples based on training knowledge (gsap 3.14.2 / @gsap/react 2.1.2), verify before use.
>
> ### Known key points:
>
> - `gsap.registerPlugin(useGSAP)` is **mandatory** before using the hook
> - `gsap.context()` exists for imperative animations outside React (Regime 3). In React, prefer `useGSAP`
> - `gsap.defaults()` defines project-wide defaults
> - **All GSAP plugins have been 100% free since late 2024** including SplitText, MorphSVG, Flip, MotionPath, DrawSVG, and others. No more Club GreenSock license

```typescript

// lib/gsap.ts — register all plugins once at module level
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { SplitText } from 'gsap/SplitText'       // free since late 2024
import { useGSAP } from '@gsap/react'

// Register all plugins including the React hook itself
gsap.registerPlugin(ScrollTrigger, SplitText, useGSAP)

// Coherent project defaults
gsap.defaults({
  ease: 'power2.out',
  duration: 0.6,
})

export { gsap, ScrollTrigger, SplitText, useGSAP }

```

### ScrollTrigger — common patterns with `useGSAP`

> ⚠️ context7 unavailable for `gsap` and `@gsap/react`
> — examples based on training knowledge, verify before use.
>
> ### Known `useGSAP` signatures (`@gsap/react` 2.x):
>
> - `useGSAP(func)` — runs once after mount, unlike `useEffect` which reruns on every render
> - `useGSAP(func, { scope, dependencies, revertOnUpdate })`
> - `useGSAP(func, [dep1, dep2])` — useEffect-like syntax, less flexible
> - `const { contextSafe } = useGSAP(config)` — for event handlers triggered after mount

> [!IMPORTANT]
> Use `useGSAP` from `@gsap/react` rather than raw `useEffect` + `gsap.context()`.
> `useGSAP` handles scope, cleanup, and SSR isomorphism automatically.

```typescript

// animations/useRevealOnScroll.ts
import { useRef } from 'react'
import { gsap, ScrollTrigger, useGSAP } from '@/lib/gsap'

// Pattern 1: reveal on scroll
export function useRevealOnScroll() {
  const containerRef = useRef<HTMLDivElement>(null)

  useGSAP(
    () => {
      // Selector text is scoped to containerRef — no ref needed per element
      gsap.from('.reveal-item', {
        opacity: 0,
        y: 40,
        duration: 0.8,
        stagger: 0.1,
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top 85%', // fires when the top of the element reaches 85% of the viewport
          end: 'top 40%',
          toggleActions: 'play none none reverse',
        },
      })
    },
    { scope: containerRef },
  )

  return containerRef
}

// Pattern 2: scrubbed animation (1:1 tied to scroll position)
export function useScrubAnimation() {
  const containerRef = useRef<HTMLDivElement>(null)
  const targetRef = useRef<HTMLDivElement>(null)

  useGSAP(
    () => {
      gsap.to(targetRef.current, {
        xPercent: -50,
        ease: 'none', // ease: 'none' is mandatory for scrub animations
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top top',
          end: 'bottom top',
          scrub: 1, // lag in seconds — 1 = smooth, 0 = instantaneous
          pin: true,
        },
      })
    },
    { scope: containerRef },
  )

  return { containerRef, targetRef }
}

```

### Event handlers with `contextSafe`

> ⚠️ context7 unavailable for `@gsap/react` — based on training knowledge, verify before use.

```tsx

// When triggering animations from event handlers (executed AFTER useGSAP body runs),
// wrap them in contextSafe() so GSAP tracks and auto-cleans them up.
import { useRef } from 'react'
import { gsap, useGSAP } from '@/lib/gsap'

export function AnimatedButton() {
  const containerRef = useRef<HTMLDivElement>(null)

  // contextSafe is returned by useGSAP
  const { contextSafe } = useGSAP({ scope: containerRef })

  // ✅ contextSafe ensures the animation is tracked by the Context for cleanup
  const handleClick = contextSafe(() => {
    gsap.to('.btn', { scale: 0.95, duration: 0.1, yoyo: true, repeat: 1 })
  })

  return (
    <div ref={containerRef}>
      <button className="btn" onClick={handleClick} data-testid="animated-btn">
        Click me
      </button>
    </div>
  )
}

```

### Performance rules (marketing site)

- Limit Spline scenes to **1 per page**. Each scene opens its own WebGL context
- Lazy-load all Spline scenes with `next/dynamic` if there is no SSR placeholder
- Reduce polygon complexity in Spline Studio before export. Target: fewer than 50k triangles
- The `renderOnDemand` prop is `true` by default in Spline. Do not disable it without a measured reason
- Disable ScrollTrigger on mobile if the animation is purely decorative:

```typescript

import { gsap, ScrollTrigger } from '@/lib/gsap'

ScrollTrigger.config({ ignoreMobileResize: true })

// Always check prefers-reduced-motion before any animation
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  gsap.globalTimeline.timeScale(0) // pause all GSAP animations globally
}

```

---

## Regime 2 — Immersive React app: R3F + Drei + GSAP

### Philosophy

React Three Fiber (R3F) maps the React paradigm such as components, hooks, and props onto
Three.js. Drei provides high-level abstractions like cameras, lights, helpers, and loaders.
GSAP integrates through `useGSAP` for complex animations driven by React.

### When to choose this regime

| Criterion | R3F ✅ | Other regime |
| --- | --- | --- |
| Integrated React interface with UI + 3D | ✅ | — |
| 3D scenes with GLTF/GLB assets | ✅ | — |
| Enter/exit animations via GSAP | ✅ | — |
| Postprocessing such as bloom, DOF, SSAO | ✅ via `@react-three/postprocessing` | — |
| Minimal bundle without React | ❌ | Plain Three.js or OGL |
| Ultra-optimized custom shaders | Possible but with overhead | Plain Three.js |

### Installation

```bash

npm install three @react-three/fiber @react-three/drei
npm install gsap @gsap/react
npm install -D @types/three

```

> [!NOTE]
> `@types/three` is a separate package. Do not forget the dev dependency install.
> Reference versions (March 2026):
> `@react-three/fiber` **9.5.0** · `@react-three/drei` **10.7.7** · `three` **0.183.2**

### Anatomy of an R3F scene

> ⚠️ context7 unavailable for `@react-three/fiber` — based on training knowledge
> (v9.5.0), verify before use.
>
> ### Known `Canvas` props:
>
> - `camera` — initial config such as `{ position, fov, near, far }` or a Three.js instance
> - `dpr` — pixel ratio, accepts `[min, max]`, and should always be capped to `[1, 2]`
> - `gl` — `WebGLRenderer` options like `antialias`, `alpha`, `powerPreference`, and so on
> - `frameloop` — `'always'` (default) | `'demand'` | `'never'`
> - `shadows` — `boolean` | `'soft'` | `'variance'` | `PCFSoftShadowMap`

```tsx

// components/three/Scene.tsx
'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, Stats } from '@react-three/drei'
import { Suspense } from 'react'

export function Scene() {
  return (
    // Canvas creates the renderer, render loop, and Three.js context
    <Canvas
      camera={{ position: [0, 2, 5], fov: 60 }}
      dpr={[1, 2]}                    // cap pixel ratio for mobile performance
      gl={{ antialias: true, alpha: false }}
      frameloop="always"              // use "demand" for static scenes
    >
      {/* Suspense is required whenever a child loads async assets */}
      <Suspense fallback={null}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <Environment preset="city" />
        <MyModel />
      </Suspense>

      <OrbitControls enableDamping />

      {/* Remove in production */}
      {process.env.NODE_ENV === 'development' && <Stats />}
    </Canvas>
  )
}

```

### Loading 3D models

> ⚠️ context7 unavailable for `@react-three/drei` — based on training knowledge
> (v10.7.7), verify before use.
>
> **`useGLTF` returns:** `{ scene, nodes, materials, animations }` typed as `GLTF`.
> `useGLTF.preload(path)` triggers the fetch at module evaluation time before mount.

```tsx

// components/three/MyModel.tsx
import { useGLTF } from '@react-three/drei'
import { useRef } from 'react'
import type { Group } from 'three'

// ✅ preload() outside the component — triggers the fetch at module evaluation time
useGLTF.preload('/models/my-model.glb')

export function MyModel() {
  const groupRef = useRef<Group>(null)
  const { nodes, materials } = useGLTF('/models/my-model.glb')

  return (
    <group ref={groupRef}>
      <mesh geometry={nodes.Body.geometry} material={materials.BaseMaterial} />
    </group>
  )
}

```

> [!TIP]
> Generate TypeScript types for your models with `npx gltfjsx model.glb`
> from package `@react-three/gltfjsx`. It produces a typed, optimized component automatically.

### `useGSAP` vs `useFrame` — the separation rule

> ⚠️ context7 unavailable for `gsap` and `@react-three/fiber` — based on training knowledge, verify before use.

> [!IMPORTANT]
>
> ### Rule of thumb:
>
> - `useGSAP` for **discrete** animations such as scene entry, UI feedback, transitions, and sequences
> - `useFrame` for **continuous time-based** animations such as constant rotation, oscillation, and simulation
>
> Do not use `useFrame` for animations that have a clear start and end. GSAP is more readable,
> more efficient because it does not compute every frame when inactive, and it handles cleanup automatically.

```tsx

// components/three/AnimatedMesh.tsx
import { useRef } from 'react'
import { gsap, useGSAP } from '@/lib/gsap' // useGSAP already registered in lib/gsap.ts
import type { Mesh } from 'three'

// ✅ useGSAP handles scope and cleanup automatically in React
export function AnimatedMesh() {
  const meshRef = useRef<Mesh>(null)

  // No scope needed here — refs are used directly, not selector text
  useGSAP(() => {
    if (!meshRef.current) return

    // Animate Three.js object properties directly
    gsap.to(meshRef.current.rotation, {
      y: Math.PI * 2,
      duration: 4,
      repeat: -1,
      ease: 'none',
    })

    gsap.to(meshRef.current.position, {
      y: 0.3,
      duration: 2,
      yoyo: true,
      repeat: -1,
      ease: 'power1.inOut',
    })
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}

```

### `useFrame` — render loop

```tsx

// components/three/RotatingMesh.tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import type { Mesh } from 'three'

// useFrame fires every frame (60fps) — use only for continuous, time-based updates
export function RotatingMesh() {
  const meshRef = useRef<Mesh>(null)

  // delta = elapsed time since previous frame (seconds) → frame-rate independent
  useFrame((_state, delta) => {
    if (!meshRef.current) return
    meshRef.current.rotation.y += delta * 0.5
  })

  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[1, 0.4, 16, 64]} />
      <meshNormalMaterial />
    </mesh>
  )
}

```

> [!WARNING]
> Never use `useFrame` for one-off animations such as scene entry or exit.
> That is GSAP’s job. `useFrame` is reserved for **continuous, time-based**
> animation such as permanent rotation, oscillation, or lightweight physics simulation.

> [!WARNING]
> Never create `new Vector3()` or any other Three.js object **inside** `useFrame`.
> That allocates memory every frame. Declare working variables outside the hook.

### R3F optimizations

> ⚠️ context7 unavailable for `@react-three/drei` — based on training knowledge, verify before use.

```tsx

// 1. Instances for repeated objects (particles, trees, crowds, etc.)
// All instances share one draw call — critical for large-scale performance
import { Instances, Instance } from '@react-three/drei'

function Particles({ count = 1000 }: { count?: number }) {
  return (
    <Instances limit={count}>
      <sphereGeometry args={[0.05, 8, 8]} />
      <meshStandardMaterial />
      {Array.from({ length: count }, (_, i) => (
        <Instance
          key={i}
          position={[
            Math.random() * 10 - 5,
            Math.random() * 10,
            Math.random() * 10 - 5,
          ]}
        />
      ))}
    </Instances>
  )
}

```

```tsx

// 2. Disable continuous rendering for static scenes
// Add frameloop="demand" to Canvas, then call invalidate() on every state change
import { useThree } from '@react-three/fiber'

function StaticSceneController() {
  const { invalidate } = useThree()
  // Call invalidate() when something changes to trigger exactly one render frame
  // e.g. on OrbitControls change, on model load, on window resize
  return null
}
// On the Canvas: <Canvas frameloop="demand">

```

### Performance rules (R3F)

- Always use `dpr={[1, 2]}`. Never leave the native ratio uncapped on mobile
- Prefer `meshStandardMaterial` on mobile. Use `meshPhysicalMaterial` only on desktop
- Use Drei’s `<Preload all />` to preload assets during Suspense
- Profile with `<Stats />` in development. Target more than 55 fps on mid-range mobile
- Dispose geometries and materials on unmount. See the cross-cutting rules section

---

## Regime 3 — Full control: plain Three.js or OGL

### When to choose this regime

- Custom GLSL shaders with logic too complex for standard Three.js materials
- Minimal bundle without React overhead for an ultra-light landing page or technical demo
- Custom post-processing such as ping-pong FBOs and bespoke convolution
- Critical performance measured and proven insufficient with R3F

> [!NOTE]
> **OGL** v1.0.11 weighs **29kb total** with tree-shaking: core 8kb + math 6kb + extras 15kb,
> versus roughly 120-180kb for Three.js. Choose OGL only if bundle size is a hard constraint
> and the project does not need the Three.js loaders such as GLTF, complex lights, or shadows.

### Plain Three.js — minimal setup

> ⚠️ context7 unavailable for `three` — based on training knowledge (v0.183.2), verify before use.
>
> ### Key points:
>
> - Always use named imports, never `import * as THREE`, for tree-shaking
> - `HalfFloatType` is directly importable from `'three'` since r140+
> - `WebGLRenderer.dispose()` does not free geometries or materials. Call `dispose()` manually on every resource

> Versions verified on npm (March 2026): `three` v0.183.2
> TypeScript types live in the separate package `@types/three`.

```typescript

// lib/three-scene.ts
// Always use named imports for tree-shaking — never "import * as THREE from 'three'"
import {
  WebGLRenderer,
  PerspectiveCamera,
  Scene,
  Clock,
} from 'three'

export class ThreeScene {
  protected renderer: WebGLRenderer
  protected camera: PerspectiveCamera
  protected scene: Scene
  protected clock = new Clock()
  private rafId = 0

  constructor(private canvas: HTMLCanvasElement) {
    this.renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

    this.camera = new PerspectiveCamera(60, this.aspect, 0.1, 100)
    this.camera.position.set(0, 0, 5)

    this.scene = new Scene()

    this.resize()
    window.addEventListener('resize', this.resize)
  }

  private get aspect() {
    return this.canvas.clientWidth / this.canvas.clientHeight
  }

  private resize = () => {
    const { clientWidth: w, clientHeight: h } = this.canvas
    this.renderer.setSize(w, h, false)
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
  }

  start() {
    const tick = () => {
      this.rafId = requestAnimationFrame(tick)
      const elapsed = this.clock.getElapsedTime()
      this.update(elapsed)
      this.renderer.render(this.scene, this.camera)
    }
    tick()
  }

  protected update(_elapsed: number): void {
    // Override in subclasses
  }

  dispose() {
    cancelAnimationFrame(this.rafId)
    window.removeEventListener('resize', this.resize)
    this.renderer.dispose()
  }
}

```

### OGL — minimal setup for a full-screen shader

> ⚠️ context7 unavailable for `ogl` — based on training knowledge (v1.0.11), verify before use.

> Versions verified on npm (March 2026): `ogl` v1.0.11
> Import pattern: `import { ... } from 'ogl'`

```typescript

// lib/ogl-scene.ts
import { Renderer, Geometry, Program, Mesh } from 'ogl'

export class OGLScene {
  private renderer: Renderer
  private mesh: Mesh
  private rafId = 0

  constructor(container: HTMLElement) {
    this.renderer = new Renderer({
      width: window.innerWidth,
      height: window.innerHeight,
    })
    const { gl } = this.renderer
    container.appendChild(gl.canvas)

    window.addEventListener('resize', this.resize)
    this.resize()

    // Triangle covering the full viewport — standard full-screen shader pattern
    const geometry = new Geometry(gl, {
      position: { size: 2, data: new Float32Array([-1, -1, 3, -1, -1, 3]) },
      uv: { size: 2, data: new Float32Array([0, 0, 2, 0, 0, 2]) },
    })

    const program = new Program(gl, {
      vertex: /* glsl */ `
        attribute vec2 position;
        attribute vec2 uv;
        varying vec2 v_uv;
        void main() {
          v_uv = uv;
          gl_Position = vec4(position, 0.0, 1.0);
        }
      `,
      fragment: /* glsl */ `
        precision highp float;
        uniform float u_time;
        varying vec2 v_uv;
        void main() {
          gl_FragColor = vec4(v_uv, 0.5 + 0.5 * sin(u_time), 1.0);
        }
      `,
      uniforms: { u_time: { value: 0 } },
    })

    this.mesh = new Mesh(gl, { geometry, program })
    this.start()
  }

  private resize = () => {
    this.renderer.setSize(window.innerWidth, window.innerHeight)
  }

  private start() {
    const tick = (t: number) => {
      this.rafId = requestAnimationFrame(tick)
      ;(this.mesh.program.uniforms['u_time'] as { value: number }).value = t * 0.001
      this.renderer.render({ scene: this.mesh })
    }
    this.rafId = requestAnimationFrame(tick)
  }

  dispose() {
    cancelAnimationFrame(this.rafId)
    window.removeEventListener('resize', this.resize)
    this.renderer.gl.canvas.remove()
  }
}

```

---

## Regime 4 — 2D video game: Phaser 3

### Philosophy

Phaser 3 is the reference framework for browser-based 2D games. It ships with its own
custom WebGL renderer and automatically falls back to Canvas 2D through `Phaser.AUTO`
on devices that do not support WebGL. It covers all game layers out of the box: physics,
input, camera, tilemaps, spritesheet animations, tweens, and audio, without third-party dependencies.

### When to choose this regime

| Criterion | Phaser 3 ✅ | Other regime |
| --- | --- | --- |
| 2D game: platformer, puzzle, RPG, arcade | ✅ | — |
| Tilemaps from Tiled Editor | ✅ | — |
| Spritesheet / atlas animations | ✅ | — |
| AABB or polygon physics | ✅ | — |
| 3D scene / custom shaders | ❌ | R3F or Three.js |
| Bundle under 100 kb | ❌ (~1 MB minimum) | OGL or Three.js |

### Installation

```bash

npm install phaser

```

> [!NOTE]
> Reference version (March 2026): `phaser` **3.87.0**
> TypeScript types are bundled in the package, so there is no `@types/phaser`.

### Scene structure

> ⚠️ context7 unavailable for `phaser` at the time of writing — based on training knowledge (v3.87.0). Call `mcp_context7_get-library-docs` before generating production code.

```typescript

// scenes/GameScene.ts
import Phaser from 'phaser'

export class GameScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private groundLayer!: Phaser.Tilemaps.TilemapLayer

  constructor() {
    super({ key: 'GameScene' })
  }

  preload() {
    // All assets declared here — never in create() or update()
    this.load.atlas('player', 'assets/player.png', 'assets/player.json')
    this.load.tilemapTiledJSON('map', 'assets/level1.json')
    this.load.image('tiles', 'assets/tiles.png')
  }

  create() {
    // Tilemap
    const map = this.make.tilemap({ key: 'map' })
    const tileset = map.addTilesetImage('tiles', 'tiles')!
    this.groundLayer = map.createLayer('Ground', tileset, 0, 0)!
    this.groundLayer.setCollisionByProperty({ collides: true })

    // Player
    this.player = this.physics.add.sprite(100, 300, 'player')
    this.player.setCollideWorldBounds(true)

    // Animations
    this.anims.create({
      key: 'walk',
      frames: this.anims.generateFrameNames('player', { prefix: 'walk_', start: 0, end: 7 }),
      frameRate: 12,
      repeat: -1,
    })
    this.anims.create({
      key: 'idle',
      frames: this.anims.generateFrameNames('player', { prefix: 'idle_', start: 0, end: 3 }),
      frameRate: 8,
      repeat: -1,
    })

    // Colliders
    this.physics.add.collider(this.player, this.groundLayer)

    // Camera
    this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels)
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1)

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys()
  }

  update() {
    const onGround = (this.player.body as Phaser.Physics.Arcade.Body).blocked.down

    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-160)
      this.player.setFlipX(true)
      this.player.anims.play('walk', true)
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(160)
      this.player.setFlipX(false)
      this.player.anims.play('walk', true)
    } else {
      this.player.setVelocityX(0)
      this.player.anims.play('idle', true)
    }

    if (this.cursors.up.isDown && onGround) {
      this.player.setVelocityY(-400)
    }
  }
}

```

### React / Next.js 16 integration

```tsx

// components/game/PhaserGame.tsx
'use client' // Phaser requires browser APIs

import { useEffect, useRef } from 'react'
import type { Game } from 'phaser'

interface Props {
  width?: number
  height?: number
}

export function PhaserGame({ width = 800, height = 600 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const gameRef = useRef<Game | null>(null)

  useEffect(() => {
    if (gameRef.current || !containerRef.current) return

    // Dynamic import — avoids SSR issues and reduces the initial bundle (~1 MB)
    Promise.all([
      import('phaser'),
      import('@/scenes/GameScene'),
    ]).then(([{ default: Phaser }, { GameScene }]) => {
      gameRef.current = new Phaser.Game({
        type: Phaser.AUTO, // WebGL → Canvas 2D fallback
        parent: containerRef.current!,
        width,
        height,
        physics: {
          default: 'arcade',
          arcade: {
            gravity: { x: 0, y: 300 },
            debug: process.env.NODE_ENV === 'development',
          },
        },
        scale: {
          mode: Phaser.Scale.FIT,
          autoCenter: Phaser.Scale.CENTER_BOTH,
        },
        scene: [GameScene],
      })
    })

    return () => {
      // Destroy releases the WebGL context and all assets
      gameRef.current?.destroy(true)
      gameRef.current = null
    }
  }, [])

  return <div ref={containerRef} className="w-full h-full" />
}

```

### Object pooling — performance basics

```typescript

// ❌ Bad: creates a new object on every call — high GC pressure
fireBullet(x: number, y: number) {
  this.physics.add.image(x, y, 'bullet') // systematic allocation
}

// ✅ Correct: group with a max size — reuses inactive objects
create() {
  this.bullets = this.physics.add.group({
    classType: Phaser.Physics.Arcade.Image,
    maxSize: 30,         // capped — no object created beyond this point
    runChildUpdate: true,
  })
}

fireBullet(x: number, y: number) {
  const bullet = this.bullets.get(x, y, 'bullet') // fetch an inactive object
  if (!bullet) return // pool exhausted — ignore according to game design intent
  bullet
    .setActive(true)
    .setVisible(true)
    .setVelocityY(-500)
}

```

### Phaser 3 conventions

- **Always** declare assets in `preload()`, never in `create()` or `update()`
- **Always** define one TypeScript class per scene using `class MyScene extends Phaser.Scene`. Do not use inline object configs
- **Always** use `Phaser.AUTO` for the renderer type
- **Always** call `game.destroy(true)` in the `useEffect` cleanup
- **Always** use `setCollideWorldBounds(true)` for active physics entities
- **Never** call `this.add.*` or `this.physics.add.*` inside `update()`. Use pools
- **Never** import Phaser synchronously in Next.js. Always use dynamic `import()`
- Use **only** `Phaser.AUTO`. Do not force `Phaser.CANVAS` without measured justification

---

## Regime 5 — 3D video game: Babylon.js

### Philosophy

Babylon.js is a full 3D game engine. It is not limited to rendering like Three.js. It provides
an integrated ecosystem with physics plugins such as Havok, Cannon, and Ammo; a skeletal
animation system with blending; in-world and fullscreen GUI; keyboard, pointer, and gamepad
input; asset loaders; and a scene inspector in development. Its plugin architecture lets you import only the modules you use.

**Selection rule**: if the project includes a game loop, physics, animation states, or a canvas HUD,
use Babylon.js. If the project is a web 3D experience, data visualization, or a site with custom shaders,
use Three.js or R3F.

### When to choose this regime

| Criterion | Babylon.js ✅ | Other regime |
| --- | --- | --- |
| 3D game: FPS, TPS, simulation, RPG | ✅ | — |
| 3D physics: collisions, rigid bodies | ✅ | — |
| Skeletal animations + blending | ✅ | — |
| In-world GUI: HUD, 3D panels | ✅ | — |
| Web 3D experience / custom shaders | ❌ | Three.js / R3F |
| Bundle under 500 kb | ❌ (~2 MB full stack) | Three.js or OGL |
| Deep React component integration | ❌ | R3F + Drei |

### Installation

```bash

npm install @babylonjs/core @babylonjs/loaders
# optional depending on needs:
npm install @babylonjs/gui        # in-world or fullscreen GUI
npm install @babylonjs/havok      # recommended physics plugin
npm install @babylonjs/inspector  # development only — never in production

```

> [!NOTE]
> Reference version (March 2026): `@babylonjs/core` **7.x** (v7.39+)
> Import from `@babylonjs/core` for tree-shaking, **not** from the old `babylonjs` package.

### Minimal setup

> ⚠️ context7 unavailable for `@babylonjs/core` at the time of writing — based on training knowledge (v7.x). Call `mcp_context7_get-library-docs` before generating any production code.

```typescript

// lib/babylon-game.ts
import { Engine, Scene, FreeCamera, HemisphericLight, Vector3, MeshBuilder } from '@babylonjs/core'

export class BabylonGame {
  private engine: Engine
  private scene: Scene

  constructor(private canvas: HTMLCanvasElement) {
    this.engine = new Engine(canvas, true /* antialias */)
    this.scene = new Scene(this.engine)

    // Dev inspector — never in production
    if (process.env.NODE_ENV === 'development') {
      import('@babylonjs/inspector').then(() => {
        this.scene.debugLayer.show({ embedMode: true })
      })
    }

    this.setup()
    this.engine.runRenderLoop(() => this.scene.render())
    window.addEventListener('resize', this.onResize)
  }

  private setup() {
    const camera = new FreeCamera('cam', new Vector3(0, 5, -10), this.scene)
    camera.setTarget(Vector3.Zero())
    camera.attachControl(this.canvas, true)

    new HemisphericLight('light', new Vector3(0, 1, 0), this.scene)

    const ground = MeshBuilder.CreateGround('ground', { width: 20, height: 20 }, this.scene)
    ground.freezeWorldMatrix() // static mesh — skip transform recalculation

    const box = MeshBuilder.CreateBox('box', { size: 1 }, this.scene)
    box.position.y = 0.5
  }

  private onResize = () => this.engine.resize()

  dispose() {
    // Releases the WebGL context + all GPU assets
    window.removeEventListener('resize', this.onResize)
    this.engine.dispose()
  }
}

```

### React / Next.js 16 integration

```tsx

// components/game/BabylonGame.tsx
'use client'

import { useEffect, useRef } from 'react'
import type { BabylonGame } from '@/lib/babylon-game'

export function BabylonGameCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const gameRef = useRef<BabylonGame | null>(null)

  useEffect(() => {
    if (gameRef.current || !canvasRef.current) return

    // Dynamic import prevents SSR issues and defers the ~2 MB bundle
    import('@/lib/babylon-game').then(({ BabylonGame }) => {
      gameRef.current = new BabylonGame(canvasRef.current!)
    })

    return () => {
      gameRef.current?.dispose()
      gameRef.current = null
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full touch-none"
      style={{ outline: 'none' }}
    />
  )
}

```

### Physics with Havok

```typescript

import { HavokPlugin, PhysicsAggregate, PhysicsShapeType } from '@babylonjs/core'
import HavokPhysics from '@babylonjs/havok'

// In Scene setup:
async function enablePhysics(scene: Scene) {
  const havok = await HavokPhysics()
  const physicsPlugin = new HavokPlugin(true, havok)
  scene.enablePhysics(new Vector3(0, -9.81, 0), physicsPlugin)
}

// Apply physics to a mesh:
const aggregate = new PhysicsAggregate(
  mesh,
  PhysicsShapeType.SPHERE, // or BOX, CAPSULE, MESH...
  { mass: 1, restitution: 0.3 },
  scene
)

```

### Babylon.js conventions

- **Always** import from `@babylonjs/core`, not `babylonjs`, for tree-shaking
- **Always** call `engine.dispose()` in the React cleanup
- **Never** include `@babylonjs/inspector` in the production bundle
- **Always** lazy-import with `import('@/lib/babylon-game')` in Next.js
- **Freeze** static meshes with `mesh.freezeWorldMatrix()`
- **Prefer `PBRMaterial`** over `StandardMaterial` for visible surfaces
- **Use `createInstance()`** for all repeated objects to enable GPU instancing
- **Enable `scene.autoClear = false`** only when the background is managed manually as a draw-call optimization

---

## GLSL — conventions and shaders

### Naming conventions

```glsl

// shaders/my-effect.vert
// ─────────────────────────────────────────────────────────
// Naming conventions:
//   u_ = uniform   (passed from JS)
//   v_ = varying   (interpolated between vertex and fragment)
//   a_ = attribute (per-vertex, vertex shader only)
// ─────────────────────────────────────────────────────────

uniform float u_time;
uniform vec2  u_resolution;

varying vec2 v_uv;

void main() {
  v_uv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}

```

```glsl

// shaders/my-effect.frag
precision highp float;

uniform float     u_time;
uniform vec2      u_resolution;
uniform sampler2D u_texture;

varying vec2 v_uv;

// ─── Utility functions ───────────────────────────────────

// Remap value from [a, b] → [0, 1]
float remap(float value, float a, float b) {
  return clamp((value - a) / (b - a), 0.0, 1.0);
}

// Simple 2D value noise
float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// ─── Main ────────────────────────────────────────────────

void main() {
  vec2 uv = v_uv;
  vec3 color = vec3(uv, 0.5 + 0.5 * sin(u_time));
  gl_FragColor = vec4(color, 1.0);
}

```

### Loading shaders in TypeScript

> ⚠️ context7 unavailable for `three` and `ShaderMaterial` — based on training knowledge, verify before use.

```typescript

// Vite — import .glsl files directly as raw strings (native, no plugin needed)
import vertexShader from './shaders/my-effect.vert?raw'
import fragmentShader from './shaders/my-effect.frag?raw'

// Named imports for tree-shaking
import { ShaderMaterial, Vector2 } from 'three'

const material = new ShaderMaterial({
  vertexShader,
  fragmentShader,
  uniforms: {
    u_time:       { value: 0 },
    u_resolution: { value: new Vector2(window.innerWidth, window.innerHeight) },
  },
})

// In the render loop:
material.uniforms['u_time']!.value = clock.getElapsedTime()

```

> [!TIP]
> Configure TypeScript types for Vite `?raw` imports with no plugin required:
>
> ```typescript
>
> // vite-env.d.ts
> declare module '*.glsl?raw' { const value: string; export default value }
> declare module '*.vert?raw' { const value: string; export default value }
> declare module '*.frag?raw' { const value: string; export default value }
> declare module '*.vs?raw'   { const value: string; export default value }
> declare module '*.fs?raw'   { const value: string; export default value }
>
> ```

### Post-processing — ping-pong FBO (plain Three.js)

> ⚠️ context7 unavailable for `three` — based on training knowledge (v0.183.2), verify before use.
>
> **`HalfFloatType`:** directly importable from `'three'` since r140+.
> There is no longer any need to import it from `three/src/constants`.

```typescript

// Ping-pong render targets for effects that read their own previous output
// (fluid simulation, feedback loops, reaction-diffusion, etc.)
import {
  WebGLRenderTarget,
  WebGLRenderer,
  Scene,
  Camera,
  NearestFilter,
  RGBAFormat,
  HalfFloatType, // higher precision for HDR / accumulation effects
} from 'three'

function createRenderTarget(width: number, height: number): WebGLRenderTarget {
  return new WebGLRenderTarget(width, height, {
    minFilter: NearestFilter,
    magFilter: NearestFilter,
    format: RGBAFormat,
    type: HalfFloatType,
  })
}

// Two alternating targets: write to A while reading from B, then swap
let targets: [WebGLRenderTarget, WebGLRenderTarget] = [
  createRenderTarget(innerWidth, innerHeight),
  createRenderTarget(innerWidth, innerHeight),
]

function pingPongRender(
  renderer: WebGLRenderer,
  simScene: Scene,
  simCamera: Camera,
  outputScene: Scene,
  outputCamera: Camera,
  fboUniforms: { u_previous: { value: unknown } },
) {
  // Write the current simulation step to targets[0]
  renderer.setRenderTarget(targets[0])
  renderer.render(simScene, simCamera)

  // Feed the result as texture input for the next step
  fboUniforms.u_previous.value = targets[0].texture

  // Swap targets
  ;[targets[0], targets[1]] = [targets[1], targets[0]]

  // Render final output to screen
  renderer.setRenderTarget(null)
  renderer.render(outputScene, outputCamera)
}

// ✅ Must dispose both targets on cleanup
function disposePingPong() {
  targets[0].dispose()
  targets[1].dispose()
}

```

---

## Cross-cutting rules

### Performance — universal safeguards

> [!WARNING]
> Three.js and WebGL do **not** automatically release GPU resources such as geometries,
> materials, textures, and render targets. Every created resource must be explicitly disposed
> with `dispose()`. Forgetting `dispose()` causes GPU memory leaks that gradually degrade
> performance and can eventually crash the app.

```typescript

// ✅ Reuse objects — never allocate in the render loop
import { Vector3 } from 'three'

const _tmpVec3 = new Vector3()
function update(x: number, y: number, z: number) {
  _tmpVec3.set(x, y, z) // reuse — no "new Vector3()" inside the loop
}

// ✅ dispose() is mandatory — Three.js does NOT garbage-collect GPU resources
import { Scene, Mesh } from 'three'

function disposeScene(scene: Scene): void {
  scene.traverse((object) => {
    if (!(object instanceof Mesh)) return

    object.geometry.dispose()

    const materials = Array.isArray(object.material)
      ? object.material
      : [object.material]

    for (const mat of materials) {
      // Dispose all texture slots (map, normalMap, roughnessMap, etc.)
      for (const key of Object.keys(mat)) {
        const value = (mat as Record<string, unknown>)[key]
        if (value && typeof value === 'object' && 'isTexture' in value) {
          (value as { dispose(): void }).dispose()
        }
      }
      mat.dispose()
    }
  })
}

```

### Animation accessibility — `prefers-reduced-motion`

```typescript

// Always check before starting any animation
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

if (prefersReducedMotion) {
  // Option A: stop all GSAP animations globally
  gsap.globalTimeline.timeScale(0)

  // Option B (preferred for 3D): show a static fallback instead of the canvas
  // showStaticFallback()
}

// In React: use gsap.matchMedia() for responsive + accessible animations
import { gsap } from '@/lib/gsap'

const mm = gsap.matchMedia()

mm.add('(prefers-reduced-motion: no-preference)', () => {
  // Full animations
  gsap.from('.hero-title', { opacity: 0, y: 40, duration: 0.8 })
})

mm.add('(prefers-reduced-motion: reduce)', () => {
  // Instant state with no motion
  gsap.set('.hero-title', { opacity: 1, y: 0 })
})

```

### File organization

```text

src/
  components/
    three/                  ← R3F components (.tsx)
      Scene.tsx
      models/
        MyModel.tsx
      effects/
        Particles.tsx
  lib/
    gsap.ts                 ← Plugin registration and project defaults
    three-scene.ts          ← Base class for imperative Three.js (regime 3)
    ogl-scene.ts            ← Base class for OGL (regime 3)
  shaders/
    my-effect.vert          ← One file per shader, named by visual effect
    my-effect.frag
    ping-pong.frag
  animations/
    useRevealOnScroll.ts    ← Reusable animation hooks (regimes 1 & 2)
    useScrubAnimation.ts

```

### Bundling and tree-shaking

> [!WARNING]
> Never use `import * as THREE from 'three'`. That pulls in the entire Three.js bundle.
> Use **only** named imports to allow tree-shaking.

```typescript

// ✅ Named imports — tree-shakeable (Vite, webpack ≥ 5)
import { Mesh, BoxGeometry, MeshStandardMaterial } from 'three'

// ❌ Namespace import — pulls the entire library (~36MB unpacked)
import * as THREE from 'three'

```

Measure bundle impact **before every merge** that introduces a new 3D dependency:

```bash

# Vite
npm run build -- --report

# Next.js (with @next/bundle-analyzer)
ANALYZE=true npm run build

```

---

## Bundle budget by stack

| Stack | JS budget (gzip) | Reference versions |
| --- | --- | --- |
| GSAP only | < 30 kb | gsap v3.14.2 |
| GSAP + ScrollTrigger | < 40 kb | gsap v3.14.2 |
| GSAP + ScrollTrigger + SplitText | < 50 kb | gsap v3.14.2 |
| Plain Three.js (tree-shaken subset) | < 120 kb | three v0.183.2 |
| Plain Three.js (broader usage) | < 180 kb | three v0.183.2 |
| R3F + Drei (subset) | < 250 kb | r3f v9.5.0 + drei v10.7.7 |
| OGL (full stack) | < 30 kb | ogl v1.0.11 |
| Spline runtime | < 500 kb | @splinetool/runtime |
| Phaser 3 (full bundle) | ~1 000 kb | phaser v3.87.0 |
| Babylon.js core only | ~800 kb | @babylonjs/core v7.x |
| Babylon.js + loaders + GUI + Havok | ~2 000 kb | @babylonjs/core v7.x |

> [!NOTE]
> These budgets assume effective tree-shaking with Vite or webpack ≥ 5 in `production` mode.
> R3F already includes Three.js in its bundle. Do not install a separate Three.js bundle if
> the project uses only R3F, or you risk duplication.
>
> ⚠️ context7 was unavailable while this file was written. All APIs and versions are based
> on training knowledge plus npm verification. Re-run `mcp_context7_get-library-docs` for
> each library before adding production code.
