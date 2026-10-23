// Suppress browser asset dragging without interfering with pointer-based game controls.
document.addEventListener("dragstart", (event) => event.preventDefault());

// Trackpads expose browser pinch as Ctrl+wheel. Cancel only its browser
// default: the event still reaches the scene's own zoom controller.
document.addEventListener("wheel", (event) => {
  if (event.ctrlKey) event.preventDefault();
}, { passive: false, capture: true });

// Safari also exposes native pinch through gesture events.
for (const type of ["gesturestart", "gesturechange"]) {
  document.addEventListener(type, (event) => event.preventDefault(), { passive: false });
}
