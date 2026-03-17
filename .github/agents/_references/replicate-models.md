# Replicate Models Catalog

> Shared reference between **GameAssetGenerator** and **AudioGenerator** agents.
> Prices and availability change frequently — consult [replicate.com/pricing](https://replicate.com/pricing) before any major batch.

---

## Image Models

### Images — General Purpose

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Fast previews / iterations | `black-forest-labs/flux-schnell` | ~$0.003/img |
| Standard assets (characters, backgrounds, UI) | `black-forest-labs/flux-1.1-pro` | ~$0.04/img |
| High-resolution assets (4MP, photorealism) | `black-forest-labs/flux-1.1-pro-ultra` | ~$0.06/img |
| Hero assets (splash art, multi-reference) | `black-forest-labs/flux-2-pro` | ~$0.08–0.12/img |
| Logos / SVG icons | `recraft-ai/recraft-v3-svg` | ~$0.04/img |
| UI with readable text | `ideogram-ai/ideogram-v3-turbo` | ~$0.02/img |

### Images — Video Game Specialized

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Pixel art (sprites, tiles, icons) | `retro-diffusion/rd-plus` | ~$0.02–0.05/img |
| Fast pixel art / prototyping | `retro-diffusion/rd-fast` | ~$0.01–0.02/img |
| Seamless tilesets | `retro-diffusion/rd-tile` | ~$0.02–0.04/img |
| Animated sprite sheets | `retro-diffusion/rd-animation` | ~$0.03–0.06/sheet |
| Multi-reference consistency (up to 14 input images) | `google/nano-banana-2` | ~$0.02–0.04/img |
| Character consistency across frames (1 reference) | `black-forest-labs/flux-kontext-pro` | ~$0.04/img |
| Background removal (transparent sprites) | `bria/remove-background` (RMBG 2.0) | ~$0.002/img |
| Quality upscaling (4M pixels) | `philz1337x/crystal-upscaler` | ~$0.02–0.04/img |

---

## Video / Animation Models

> Cost strategy: always start with `wan-2.1-fast` at low resolution for validation, then upgrade only approved sequences.

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Animated previews (5s, low res) | `wan-ai/wan-2.1-fast` | ~$0.10–0.20/vid |
| Character animations (I2V, 5–10s) | `kling-ai/kling-v2.6-pro` | ~$0.30–0.50/vid |
| Cutscenes / trailers (cinematic quality) | `google/veo-3.1` | ~$0.50–1.00/vid |
| Multi-reference control (image + video) | `bytedance/seedance-2.0` | ~$0.40–0.80/vid |
| Motion control (motion transfer) | `kling-ai/kling-3.0` | ~$0.40–0.70/vid |

---

## Audio Models

### Music / OST

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Short ambient loops (8–30s, prototyping) | `meta/musicgen` (melody) | ~$0.065/gen |
| Long themes (30s–3min, final quality) | `stability-ai/stable-audio` | ~$0.10–0.30/gen |
| Chiptune / 8-bit style OST | `meta/musicgen` (fine-tune video game) | ~$0.065/gen |
| Themes with continuation (>30s) | `meta/musicgen` large, windowing | ~$0.10/gen |

### SFX — Sound Effects

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Generic SFX (explosions, footsteps, UI clicks…) | `meta/audiogen` | ~$0.05/gen |
| SFX synchronized to video/animation | `zsxkib/mmaudio` (MMAudio V2) | ~$0.008/gen |
| SFX from GameAssetGenerator video | `mirelo/video-to-sfx-v1.5` | ~$0.01–0.03/gen |

### Ambiances / Soundscapes

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Long ambiances (forest, dungeon, space…) | `stability-ai/stable-audio` | ~$0.10–0.30/gen |
| Ambiance synchronized to video scene | `zsxkib/mmaudio` (MMAudio V2) | ~$0.008/gen |
| Short seamless loops | `meta/musicgen` | ~$0.065/gen |

### Voice / Dialogue / Narration

> Voice strategy: always validate tone and voice on a short excerpt (2–3 sentences) with `speech-02-turbo` before generating all dialogues in HD.

| Use Case | Model | Est. Cost |
| --- | --- | --- |
| Fast dialogue / prototyping | `minimax/speech-02-turbo` | ~$0.01–0.02/1k chars |
| Narration / voice-over final quality | `minimax/speech-02-hd` | ~$0.02–0.04/1k chars |
| Voice cloning (5–20s of reference) | `minimax/speech-02-hd` + voice cloning | ~$0.03–0.05/1k chars |
| Expressive character voices | `resemble-ai/chatterbox` | ~$0.02–0.04/gen |

---

## Accepted Visual Inputs

| Type | Formats | Model Parameter | Usage |
| --- | --- | --- | --- |
| Reference images (multi) | PNG, JPG, WEBP | `image_input` array (nano-banana-2, up to 14) | Global style, entire kit consistency |
| Reference image (single) | PNG, JPG, WEBP | `input_image` (flux-kontext-pro) | Strict 1→1 shape consistency |
| Moodboard / screenshots | PNG, JPG, PDF | Text prompt refinement | Artistic direction, palette |
| Reference videos | MP4, MOV, WEBM | `video` (seedance-2.0), motion ref (kling-3.0) | Movement, rhythm |
| Existing sprite sheets | PNG (grid) | `reference_image` (rd-animation, flux-kontext-pro) | Style consistency |

## Accepted Audio Inputs

| Type | Formats | Model Parameter | Usage |
| --- | --- | --- | --- |
| Reference melody / theme | MP3, WAV, FLAC | `melody_input` (musicgen) | Continue or guide a theme |
| Reference voice | MP3, WAV (5–20s, clean) | `reference_audio` (minimax, chatterbox) | Voice cloning |
| Reference ambiance | MP3, WAV | `audio_input` (stable-audio) | Target sound tone |
| Source video | MP4, MOV | `video` (mmaudio, video-to-sfx) | Synchronized SFX/ambiance |

---

## Negative Prompts by Asset Type

### Visuals

| Asset Type | Negative Prompt |
| --- | --- |
| Characters / sprites | `blurry, deformed hands, extra limbs, watermark, text, signature, low quality, jpeg artifacts` |
| Backgrounds / backdrops | `blurry, overexposed, watermark, text, people, characters, low quality` |
| Pixel art | `smooth, anti-aliased, photorealistic, blurry, gradient, 3D render, high resolution` |
| UI / mockups | `blurry, distorted text, watermark, low contrast, illegible` |
| Video / animations | `jittery, flickering, morphing faces, duplicate characters, watermark, low framerate` |

### Audio

| Asset Type | Negative Prompt |
| --- | --- |
| Music / OST | `vocals, singing, spoken word, noise, distortion, abrupt ending, silence gaps` |
| SFX | `music, melody, background ambiance, reverb, echo, muffled, low quality` |
| Ambiances / soundscapes | `music, melody, vocals, abrupt changes, distortion, noise artifacts` |
| Voice / dialogue | `robotic, monotone, background noise, echo, distortion, unnatural pauses` |

---

## Accepted Visual Inputs

Users can provide references at any stage. Detect, catalog, and map them to the correct Replicate input parameter.

| Type | Formats | Model Parameter | Usage |
| --- | --- | --- | --- |
| Reference images (multi) | PNG, JPG, WEBP | `image_input` array (nano-banana-2, up to 14) | Global style, entire kit consistency |
| Reference image (single) | PNG, JPG, WEBP | `input_image` (flux-kontext-pro) | Strict 1→1 shape consistency |
| Moodboard / screenshots | PNG, JPG, PDF | Text prompt refinement | Artistic direction, palette |
| Reference videos | MP4, MOV, WEBM | `video` (seedance-2.0), motion ref (kling-3.0) | Movement, rhythm |
| Existing sprite sheets | PNG (grid) | `reference_image` (rd-animation, flux-kontext-pro) | Style consistency |

## Visual Negative Prompts

Include systematically in calls that support this parameter.

| Asset Type | Negative Prompt |
| --- | --- |
| Characters / sprites | `blurry, deformed hands, extra limbs, watermark, text, signature, low quality, jpeg artifacts` |
| Backgrounds / backdrops | `blurry, overexposed, watermark, text, people, characters, low quality` |
| Pixel art | `smooth, anti-aliased, photorealistic, blurry, gradient, 3D render, high resolution` |
| UI / mockups | `blurry, distorted text, watermark, low contrast, illegible` |
| Video / animations | `jittery, flickering, morphing faces, duplicate characters, watermark, low framerate` |

---

## Accepted Audio Inputs

Users can provide references at any stage. Detect, catalog, and map them to the correct Replicate input parameter.

| Type | Formats | Model Parameter | Usage |
| --- | --- | --- | --- |
| Reference melody / theme | MP3, WAV, FLAC | `melody_input` (musicgen) | Continue or guide a theme |
| Reference voice | MP3, WAV (5–20s, clean) | `reference_audio` (minimax, chatterbox) | Voice cloning |
| Reference ambiance | MP3, WAV | `audio_input` (stable-audio) | Target sound tone |
| Source video | MP4, MOV | `video` (mmaudio, video-to-sfx) | Synchronized SFX/ambiance |

## Audio Negative Prompts

Include systematically in calls that support this parameter.

| Asset Type | Negative Prompt |
| --- | --- |
| Music / OST | `vocals, singing, spoken word, noise, distortion, abrupt ending, silence gaps` |
| SFX | `music, melody, background ambiance, reverb, echo, muffled, low quality` |
| Ambiances / soundscapes | `music, melody, vocals, abrupt changes, distortion, noise artifacts` |
| Voice / dialogue | `robotic, monotone, background noise, echo, distortion, unnatural pauses` |
