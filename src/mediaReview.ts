// Local review only: reveal unused media space without changing the artwork.
if (import.meta.env.DEV && new URLSearchParams(window.location.search).get("media-review") === "gaps") {
  const style = document.createElement("style");
  style.dataset.mediaReview = "gaps";
  style.textContent = `
    :is([data-result-art], [data-outcome-scene], [data-world-scene]),
    :is([data-result-art], [data-outcome-scene], [data-world-scene]) picture,
    :is([data-result-art], [data-outcome-scene], [data-world-scene]) picture > img {
      background: #ff5252 !important;
    }
  `;
  document.head.append(style);
}
