---
name: AWS Tech Dark
colors:
  primary: "#0F172A"       # Deep slate blue background
  on-primary: "#F8FAFC"    # Crisp off-white text
  accent-orange: "#FF9900" # AWS Orange for emphasis/branding
  accent-blue: "#00A1C9"   # AWS Blue for secondary elements
  accent-green: "#10B981"  # Emerald green for the correct option
  accent-red: "#EF4444"    # Crimson red for incorrect options
  surface: "#1E293B"       # Slate card/surface background
  muted: "#64748B"         # Muted steel grey for secondary labels
typography:
  headline:
    fontFamily: Space Grotesk
    fontSize: 4.5rem
    fontWeight: 700
  body:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: 400
  label:
    fontFamily: Inter
    fontSize: 1.25rem
    fontWeight: 600
rounded:
  none: 0px
  sm: 4px
  md: 12px
  lg: 24px
spacing:
  sm: 16px
  md: 32px
  lg: 64px
motion:
  energy: moderate
  easing:
    entry: "power3.out"
    exit: "power4.in"
    ambient: "sine.inOut"
  duration:
    entrance: 0.6
    hold: 2.0
    transition: 0.8
  atmosphere:
    - grid-lines
    - radial-glow
  transition: domain-warp
---

## Overview
A sleek, modern dark mode visual style designed for cloud architecture and AWS Certification tutorials. Deep slate tones provide a cinematic backdrop, while vibrant AWS Orange and Blue are used selectively to draw focus to critical architectural elements and SAA-C03 keywords.

## Colors
- **Primary Background**: `#0F172A` - A premium slate background that prevents the harshness of pure black and minimizes video compression artifacts (avoids H.264 banding).
- **On-Primary Text**: `#F8FAFC` - Bright off-white for body text and headers to maintain AAA accessibility contrast.
- **AWS Orange**: `#FF9900` - Used to highlight core keywords, S3 bucket symbols, and positive actions.
- **AWS Blue**: `#00A1C9` - Used for secondary cloud computing visual cues like EC2, EBS, and data flows.
- **Emerald Green**: `#10B981` - Specifically reserved to mark correct answers and pass requirements.

## Typography
- **Headlines**: Space Grotesk - A geometric, high-impact sans-serif font that conveys technical precision.
- **Body & Labels**: Inter - Clean, legible sans-serif font that stays readable even at smaller resolutions or inside diagram boxes.

## Elevation & Radii
- Medium rounding (`12px`) for content cards and code snippets to give a modern, friendly tech vibe.
- Light shadow elevation (`0 10px 30px rgba(0, 0, 0, 0.3)`) to separate cards from the background canvas.
