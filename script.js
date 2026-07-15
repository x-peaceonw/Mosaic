let allPosts = [];

const THUMB_CLASSES = ["thumb--a", "thumb--b", "thumb--c", "thumb--d", "thumb--e"];

function normalize(str) {
  return (str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
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
  const categories = ["All", ...new Set(posts.map(p => p.category || "Music"))];
  const list = document.getElementById("tabs-list");
  list.innerHTML = categories.map((cat, i) => `
    <li><button class="tab ${i === 0 ? "is-active" : ""}" data-cat="${cat}">${cat}</button></li>
  `).join("");

  list.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      list.querySelectorAll(".tab").forEach(t => t.classList.remove("is-active"));
      tab.classList.add("is-active");
      const cat = tab.dataset.cat;
      renderPosts(cat === "All" ? allPosts : allPosts.filter(p => (p.category || "Music") === cat));
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
    const thumbClass = THUMB_CLASSES[i % THUMB_CLASSES.length];
    const rotate = i % 5 === 1 ? "pin--rotate-l" : i % 5 === 3 ? "pin--rotate-r" : "";
    const tall = i % 3 === 0 ? " thumb--tall" : "";

    return `
      <article class="card card--pin pin ${rotate}" data-category="${post.category || "Music"}">
        <div class="card__thumb ${thumbClass}${tall}" style="background-image:url('${post.image}')">
          <span class="tape${i % 2 === 0 ? "" : " tape--right"}"></span>
          <a href="${post.spotify}" target="_blank"><button class="save-btn">Open</button></a>
          <span class="source-tag">${post.source}</span>
        </div>
        <h3 class="card__title">${post.title}</h3>
        <div class="card__meta">
          <span>${post.artist}</span>
          <span class="card__meta-dot">\u00b7</span>
          <span>${post.time}</span>
        </div>
      </article>
    `;
  }).join("");
}

document.getElementById("search").addEventListener("input", (e) => {
  const term = normalize(e.target.value);
  const filtered = allPosts.filter(post =>
    normalize(post.title).includes(term) ||
    normalize(post.artist).includes(term)
  );
  renderPosts(filtered);
});
