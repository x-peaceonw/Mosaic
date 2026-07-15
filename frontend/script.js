let allPosts = [];

fetch("data/music.json")
  .then(response => response.json())
  .then(posts => {
    allPosts = posts;
    renderPosts(posts);
  })
  .catch(err => console.error("Failed to load feed:", err));

function renderPosts(posts) {
  const feed = document.getElementById("feed");
  feed.innerHTML = "";

  posts.forEach(post => {
    feed.innerHTML += `
      <div class="card" data-category="${post.category || "Music"}">
        <div class="card__thumb" style="background-image:url('${post.image}')">
          <span class="source-tag">${post.source}</span>
          <button class="save-btn">📌 Save</button>
        </div>
        <h2 class="card__title">${post.title}</h2>
        <p class="card__meta">
          <span>${post.artist}</span>
          <span class="card__meta-dot">•</span>
          <span>${post.time}</span>
        </p>
        <div class="actions">
          <a href="${post.spotify}" target="_blank"><button>▶ Spotify</button></a>
          <button>✕</button>
        </div>
      </div>
    `;
  });
}

// Called by the category tabs in index.html (onclick="filterPosts('Music')")
function filterPosts(category) {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.classList.toggle("is-active", tab.textContent.trim() === category);
  });

  const cards = document.querySelectorAll("#feed .card");
  cards.forEach(card => {
    const matches = category === "All" || card.dataset.category === category;
    card.style.display = matches ? "" : "none";
  });
}

// Wire up the search box
const searchInput = document.getElementById("search");
if (searchInput) {
  searchInput.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allPosts.filter(post =>
      post.title.toLowerCase().includes(term) ||
      post.artist.toLowerCase().includes(term)
    );
    renderPosts(filtered);
  });
}