let allPosts = [];

const THUMB_CLASSES = ["thumb--a", "thumb--b", "thumb--c", "thumb--d", "thumb--e"];
const SAVED_KEY = "mosaic_saved_urls";

function normalize(str) {
  return (str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function isRecent(dateStr) {
  const posted = new Date(dateStr);
  const hoursAgo = (Date.now() - posted.getTime()) / 36e5;
  return hoursAgo >= 0 && hoursAgo <= 24;
}

function getSaved() {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || "[]");
  } catch {
    return [];
  }
}

function isSaved(url) {
  return getSaved().includes(url);
}

function toggleSaved(url) {
  const saved = getSaved();
  const next = saved.includes(url) ? saved.filter(u => u !== url) : [...saved, url];
  localStorage.setItem(SAVED_KEY, JSON.stringify(next));
}

document.getElementById("today-date").textContent =
  new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" }).toUpperCase();

fetch("data/music.json")
  .then(response => response.json())
  .then(posts => {
    allPosts = posts;
    buildTabs(posts);
    buildTicker(posts);
    renderPosts(posts);
  })
  .catch(err => console.error("Failed to load feed:", err));

function buildTicker(posts) {
  const track = document.getElementById("ticker-track");
  if (!posts.length) {
    track.innerHTML = "<span>NO NEW RELEASES YET</span><span>\u00b7</span>";
    return;
  }
  const items = posts.map(p => `<span>${p.artist.toUpperCase()} \u2014 ${p.title.toUpperCase()}</span><span>\u00b7</span>`);
  track.innerHTML = items.join("") + items.join("");
}

function buildTabs(posts) {
  const categories = ["All", ...new Set(posts.map(p => p.category || "Music")), "Saved"];
  const list = document.getElementById("tabs-list");
  list.innerHTML = categories.map((cat, i) => `
    <li><button class="tab ${i === 0 ? "is-active" : ""}" data-cat="${cat}">${cat}</button></li>
  `).join("");

  list.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      list.querySelectorAll(".tab").forEach(t => t.classList.remove("is-active"));
      tab.classList.add("is-active");
      const cat = tab.dataset.cat;
      if (cat === "All") {
        renderPosts(allPosts);
      } else if (cat === "Saved") {
        const saved = getSaved();
        renderPosts(allPosts.filter(p => saved.includes(p.spotify)));
      } else {
        renderPosts(allPosts.filter(p => (p.category || "Music") === cat));
      }
    });
  });
}

function renderPosts(posts) {
  const feed = document.getElementById("feed");

  if (!posts.length) {
    feed.innerHTML = `<p class="empty-state">Nothing here yet \u2014 check back after the next update.</p>`;
    return;
  }

  feed.innerHTML = posts.map((post, i) => {
    const saved = isSaved(post.spotify);
    const saveLabel = saved ? "Saved \u2713" : "Save";
    const saveClass = saved ? "save-btn is-saved" : "save-btn";

    // No image -> compact text-only card instead of a big photo card
    if (!post.image) {
      return `
        <article class="card card--newstext" data-category="${post.category || "Music"}">
          <p class="card__eyebrow">${post.source}</p>
          <h3 class="card__title"><a href="${post.spotify}" target="_blank">${post.title}</a></h3>
          <div class="card__meta">
            <span>${post.artist}</span>
            <span class="card__meta-dot">\u00b7</span>
            <span>${post.time}</span>
          </div>
          <button class="${saveClass}" data-url="${post.spotify}">${saveLabel}</button>
        </article>
      `;
    }

    const thumbClass = THUMB_CLASSES[i % THUMB_CLASSES.length];
    const rotate = i % 5 === 1 ? "pin--rotate-l" : i % 5 === 3 ? "pin--rotate-r" : "";
    const tall = i % 3 === 0 ? " thumb--tall" : "";

    return `
      <article class="card card--pin pin ${rotate}" data-category="${post.category || "Music"}">
        <div class="card__thumb ${thumbClass}${tall}" style="background-image:url('${post.image}')">
          <span class="tape${i % 2 === 0 ? "" : " tape--right"}"></span>
          ${isRecent(post.time) ? '<span class="new-badge">NEW</span>' : ""}
          <button class="${saveClass}" data-url="${post.spotify}">${saveLabel}</button>
          <span class="source-tag">${post.source}</span>
        </div>
        <h3 class="card__title"><a href="${post.spotify}" target="_blank">${post.title}</a></h3>
        <div class="card__meta">
          <span>${post.artist}</span>
          <span class="card__meta-dot">\u00b7</span>
          <span>${post.time}</span>
        </div>
      </article>
    `;
  }).join("");

  feed.querySelectorAll(".save-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const url = btn.dataset.url;
      toggleSaved(url);
      const nowSaved = isSaved(url);
      btn.textContent = nowSaved ? "Saved \u2713" : "Save";
      btn.classList.toggle("is-saved", nowSaved);
    });
  });
}

document.getElementById("search").addEventListener("input", (e) => {
  const term = normalize(e.target.value);
  const filtered = allPosts.filter(post =>
    normalize(post.title).includes(term) ||
    normalize(post.artist).includes(term)
  );
  renderPosts(filtered);
});
