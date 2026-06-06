# AWS SAA-C03 Video Creation Guide (Vertical Mobile Template)

This guide provides the official specifications and workflow for generating consistent, high-quality AWS Solutions Architect Associate (SAA-C03) question-solving videos. All videos follow a vertical mobile aspect ratio (1080x1920), feature a persistent question context card, center-focused dynamic overlays, and a synchronized horizontal scrolling caption bar.

---

## 1. Project Directory Structure

Every question-solving project must contain the following file hierarchy:

```text
aws-saa-c03-q[number]/
├── fonts/
│   ├── space-grotesk-latin-400-normal.woff2
│   ├── space-grotesk-latin-700-normal.woff2
│   ├── space-mono-latin-400-normal.woff2
│   └── space-mono-latin-700-normal.woff2
├── assets/                  # Diagrams, images, or WebGL resources
├── index.html              # Core DOM structure, CSS styling, and GSAP timeline
├── script.txt              # Plaintext voiceover script
├── narration.wav           # Generated Kokoro TTS voiceover file
├── transcript.json         # Word-aligned timestamps from Whisper
├── hyperframes.json        # Composition metadata configuration
└── package.json            # Command hooks for previewing and rendering
```

> [!NOTE]
> All fonts must be stored locally in the `fonts/` subdirectory to guarantee offline rendering stability in the HyperFrames compiler.

---

## 2. Canvas Grid & Layout Specifications

The vertical canvas is strict **1080px wide by 1920px high**. To optimize space and visibility on mobile screens, the canvas is split into static context zones and a dynamic bottom workspace.

```mermaid
rect/anchor coordinates
+---------------------------------------------------+  Y: 0px
|                     HEADER ZONE                   |  Y: 120px - 220px
+---------------------------------------------------+
|                                                   |
|             PERSISTENT QUESTION CARD              |  Y: 260px - 700px
|                                                   |  (Height: 440px)
+---------------------------------------------------+
|                                                   |
|                                                   |
|                DYNAMIC WORKSPACE                  |  Y: 720px - 1670px
|             (Diagrams / Focused Cards)             |  (Height: 950px)
|                                                   |
|                                                   |
+---------------------------------------------------+
|                 SCROLLING CAPTIONS                |  Y: 1740px - 1840px
+---------------------------------------------------+  Y: 1920px
```

### Layout Coordinates
*   **Header Zone** (`Y: 120px - 220px`): Renders the exam name (e.g. AWS SAA-C03) and the Topic/Question identifier inside a pill-shaped badge.
*   **Persistent Question Card** (`Y: 260px - 700px`, Height: `440px`): Positioned absolutely as a global element. It must stay persistently visible during Scenes 2, 3, and 4 to ensure the user can read the context while evaluating choices.
*   **Dynamic Workspace** (`Y: 720px - 1670px`): Reserved for scene-specific content:
    *   *Scene 2*: Network or service flow architecture diagram.
    *   *Scene 3*: Centered, scaled option cards (one active at a time).
    *   *Scene 4*: Detailed technical justification cards with Correct/Incorrect status.
*   **Horizontal Caption Track** (`Y: 1740px - 1840px`, Height: `100px`): Center-scrolling word-by-word player.

---

## 3. Visual Styling & Design System

The layout adopts the **AWS Tech Dark** theme, optimized for contrast, readability, and modern aesthetics.

### Color Tokens
```css
:root {
  --primary: #0F172A;         /* Slate 900 (Canvas background) */
  --surface: #1E293B;         /* Slate 800 (Card background) */
  --on-primary: #F8FAFC;      /* Slate 50 (Primary high-contrast text) */
  --muted: #94A3B8;           /* Slate 400 (Secondary descriptive text) */
  --accent-orange: #FF9900;   /* AWS Orange (Highlighting and memory hooks) */
  --accent-blue: #00A1C9;     /* AWS Blue (Active borders and badges) */
  --accent-green: #10B981;    /* Success Green (Correct answer card) */
  --accent-red: #EF4444;      /* Error Red (Incorrect justifications) */
  --surface-border: rgba(255, 255, 255, 0.08);
}
```

### Typography Rules
*   **Headings & Accents**: Use `Space Grotesk` (weights 400, 700). Applicable to headers, scene titles, badges, and card option markers.
*   **Paragraphs, Code & Logs**: Use `Space Mono` (weights 400, 700). Applicable to the persistent question card, code/config snippets, and captions.

---

## 4. Scripting & Audio Generation

To retain viewer retention, narration must be extremely concise and free of greeting/outro fluff.

### Script Formatting Rules
1.  **Opening**: Avoid introductory greetings ("Hello everyone", "Welcome back"). Begin immediately with the exam title:
    *   *Correct*: `"AWS Certified Solutions Architect Associate, question one..."`
2.  **Options**: List options directly using: `"Option A: ... Option B: ..."`
3.  **Explanations**: Focus on *why* the correct answer aligns with the prompt, then quickly state why other options fail. Keep explanations under two sentences per choice.
4.  **Closing**: Conclude directly after the memory hook. Do not include wishing phrases ("Good luck on your exam", "Don't forget to subscribe").

### Audio Pipeline Commands
Generate speech audio locally using Kokoro-82M, then transcribe the audio with Whisper to generate timestamps:

```bash
# 1. Generate Voiceover using the "am_adam" voice (standard, clear tutorial voice)
npx hyperframes tts script.txt --voice am_adam --output narration.wav

# 2. Transcribe voiceover to generate word-level timings
npx hyperframes transcribe narration.wav --model small.en
```

This generates `transcript.json` mapping each word to precise millisecond boundaries.

---

## 5. Animation & GSAP Timeline Choreography

Transitions are managed by a centralized, scrubbable GSAP timeline. Avoid ad-hoc transition handlers.

```javascript
const tl = gsap.timeline({ paused: true });
window.__timelines["main"] = tl;
```

### Global Element Controls
*   **Ambient Glows**: Slow drifting backgrounds running on infinite loops to keep the canvas feeling active:
    ```javascript
    tl.to(".bg-glow-1", { x: 100, y: 50, duration: 20, repeat: 6, yoyo: true, ease: "sine.inOut" }, 0);
    ```
*   **Persistent Card**: Fades in at the start of Scene 2 and fades out before the Memory Hook:
    ```javascript
    tl.to("#global-question-card", { opacity: 1, duration: 0.8, ease: "power2.out" }, 4.2);
    tl.to("#global-question-card", { opacity: 0, duration: 0.8, ease: "power2.in" }, 113.6);
    ```

### Option Transition (Scene 3 & 4 Stacked Card Overlay)
Because space is limited on vertical mobile screens, only **one card is visible and focused** at any given time. Cards are stacked absolutely in the workspace container.

When transition occurs:
1.  Scale down and fade out the current active card.
2.  Set the class list on the old card to default.
3.  Scale up and fade in the new card.
4.  Add `.active-focus` to highlight its borders and cast a glow.

```javascript
// Fade out Option A
tl.to("#s3-optA", { scale: 0.9, opacity: 0, duration: 0.4, ease: "power2.in" }, 32.9);
tl.set("#s3-optA", { className: "option-card-vertical" }, 33.3);

// Fade in Option B and apply focus highlight
tl.to("#s3-optB", { scale: 1.1, opacity: 1, duration: 0.5, ease: "back.out(1.2)" }, 33.3);
tl.set("#s3-optB", { className: "option-card-vertical active-focus" }, 33.3);
```

#### Card Highlight Styling Classes:
*   `.option-card-vertical.active-focus`: `border-color: var(--accent-blue)`, `box-shadow: 0 25px 60px rgba(0, 161, 201, 0.25)`
*   `.dive-card-vertical.correct-card.active-focus`: `border-color: var(--accent-green)`, `box-shadow: 0 25px 60px rgba(16, 185, 129, 0.2)`
*   `.dive-card-vertical.incorrect-card.active-focus`: `border-color: var(--accent-red)`, `box-shadow: 0 25px 60px rgba(239, 68, 68, 0.2)`

---

## 6. Horizontal Scrolling Caption System

Captions are styled as a unified horizontal strip at the bottom of the screen. Instead of wrapping text, words are laid out in a single horizontal row, sliding dynamically so that the active word is centered.

### DOM Setup
```html
<div id="caption-wrapper">
  <div id="caption-box"></div>
</div>
```

```css
#caption-wrapper {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 920px;
  height: 100px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 0 40px;
  z-index: 100;
  display: flex;
  align-items: center;
  overflow: hidden;
}

#caption-box {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  white-space: nowrap;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translate3d(460px, -50%, 0); /* Center offsets first word initially */
  transition: transform 0.25s cubic-bezier(0.25, 1, 0.5, 1);
  will-change: transform;
}

.caption-word {
  font-family: 'Space Mono', monospace;
  font-size: 38px;
  font-weight: 500;
  opacity: 0.3;
  color: var(--on-primary);
  transition: opacity 0.2s, color 0.2s, transform 0.2s;
  flex-shrink: 0;
  display: inline-block;
}

.caption-word.active {
  opacity: 1;
  color: var(--accent-orange);
  font-weight: 700;
  transform: scale(1.15);
}
```

### Caption Alignment Logic
During the GSAP timeline update callback, the playhead time checks the `TRANSCRIPT` timestamps to assign classes and slide the text:

```javascript
tl.eventCallback("onUpdate", () => {
  const t = tl.time();
  if (typeof TRANSCRIPT === 'undefined' || TRANSCRIPT.length === 0) return;

  let activeIdx = -1;

  // 1. Loop through transcript to toggle the active highlight
  TRANSCRIPT.forEach((wordObj, idx) => {
    const span = document.getElementById(`w-${idx}`);
    if (!span) return;

    if (t >= wordObj.start && t <= wordObj.end) {
      span.className = "caption-word active";
      activeIdx = idx;
    } else {
      span.className = "caption-word";
    }
  });

  // 2. Slide the caption container to center the active word horizontally
  if (activeIdx !== -1) {
    const activeSpan = document.getElementById(`w-${activeIdx}`);
    const box = document.getElementById("caption-box");
    const wrapper = document.getElementById("caption-wrapper");
    if (activeSpan && box && wrapper) {
      const wrapperCenter = wrapper.offsetWidth / 2;
      const activeCenter = activeSpan.offsetLeft + activeSpan.offsetWidth / 2;
      const shift = wrapperCenter - activeCenter;
      box.style.transform = `translate3d(${shift}px, -50%, 0)`;
    }
  }
});
```

---

## 7. Transcript Inlining Pipeline Automation

To automatically merge Whisper's timing results into `index.html` without manual code editing, use the following automation script:

`inline_transcript.py`:
```python
import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python inline_transcript.py <project_directory>")
        sys.exit(1)

    project_dir = sys.argv[1]
    transcript_path = os.path.join(project_dir, "transcript.json")
    index_path = os.path.join(project_dir, "index.html")

    if not os.path.exists(transcript_path):
        print(f"Error: transcript.json not found in {project_dir}")
        sys.exit(1)

    if not os.path.exists(index_path):
        print(f"Error: index.html not found in {project_dir}")
        sys.exit(1)

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    # Convert to minified JSON string
    transcript_str = json.dumps(transcript_data)

    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    placeholder = "/* TRANSCRIPT_PLACEHOLDER */"
    
    if placeholder in index_content:
        new_content = index_content.replace(placeholder, f"var TRANSCRIPT = {transcript_str};")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Success: Transcript successfully inlined!")
    elif "var TRANSCRIPT = " in index_content:
        # If already inlined, warn user
        print("Notice: var TRANSCRIPT is already inlined in index.html. Revert index.html first to re-run.")
    else:
        print("Error: Neither placeholder nor TRANSCRIPT array variable found in index.html")

if __name__ == "__main__":
    main()
```

### Automation Step-by-Step
1.  Verify the `index.html` template includes the placeholder script comment:
    ```html
    <!-- Dynamic Synced Captions Box -->
    <div id="caption-wrapper" data-layout-allow-overflow>
      <div id="caption-box">Loading captions...</div>
    </div>
    
    <script>
      /* TRANSCRIPT_PLACEHOLDER */
      // ... Caption DOM and timeline updates code ...
    </script>
    ```
2.  Run the generation commands in sequence:
    ```bash
    # Step A: Voice generation
    npx hyperframes tts script.txt --voice am_adam --output narration.wav
    
    # Step B: Time alignment transcription
    npx hyperframes transcribe narration.wav --model small.en
    
    # Step C: Inline transcript variables
    python3 inline_transcript.py .
    ```
3.  Execute local checks to ensure valid HTML and CSS constraints:
    ```bash
    npm run check
    ```
4.  Render the final production video:
    ```bash
    npm run render
    ```
