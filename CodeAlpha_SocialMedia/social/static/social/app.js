(function () {
  const csrf = () => document.getElementById("csrf").value;

  async function postJSON(url) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": csrf(), "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  }

  // Like / unlike without reloading the page
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".like-btn");
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    try {
      const data = await postJSON(btn.dataset.url);
      btn.classList.toggle("liked", data.liked);
      btn.setAttribute("aria-pressed", String(data.liked));
      btn.querySelector(".count").textContent = data.count;
      btn.classList.remove("pop");
      void btn.offsetWidth; // restart the animation
      if (data.liked) btn.classList.add("pop");
    } catch (err) {
      alert("Could not update like. Please try again.");
    } finally {
      btn.disabled = false;
    }
  });

  // Save / unsave a post
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".save-btn");
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    try {
      const data = await postJSON(btn.dataset.url);
      btn.classList.toggle("saved", data.saved);
      btn.setAttribute("aria-pressed", String(data.saved));
      btn.setAttribute("title", data.saved ? "Remove from saved" : "Save post");
    } catch (err) {
      alert("Could not save this post. Please try again.");
    } finally {
      btn.disabled = false;
    }
  });

  // Follow / unfollow
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".follow-btn");
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    try {
      const data = await postJSON(btn.dataset.url);
      btn.textContent = data.following ? "Following" : "Follow";
      btn.classList.toggle("following", data.following);
      if (btn.dataset.count) {
        const el = document.querySelector(btn.dataset.count);
        if (el) el.textContent = data.followers;
      }
    } catch (err) {
      alert("Could not update follow. Please try again.");
    } finally {
      btn.disabled = false;
    }
  });

  // Light / dark theme (initial value is set in <head> to avoid a flash)
  document.querySelectorAll(".js-theme").forEach((el) => {
    el.addEventListener("click", () => {
      const root = document.documentElement;
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  });

  // "More" dropdown: click to toggle, click outside or press Esc to close
  const moreBtn = document.getElementById("more-btn");
  const moreMenu = document.getElementById("more-menu");
  if (moreBtn && moreMenu) {
    const setOpen = (open) => {
      moreMenu.hidden = !open;
      moreBtn.setAttribute("aria-expanded", String(open));
    };
    moreBtn.addEventListener("click", (e) => { e.stopPropagation(); setOpen(moreMenu.hidden); });
    document.addEventListener("click", (e) => { if (!moreMenu.contains(e.target)) setOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
  }

  // "Create" focuses the post box (on the feed page it does not reload)
  const composer = document.querySelector(".composer textarea");
  const focusComposer = () => {
    if (!composer) return false;
    composer.scrollIntoView({ behavior: "smooth", block: "center" });
    composer.focus({ preventScroll: true });
    return true;
  };
  document.querySelectorAll("[data-compose]").forEach((a) =>
    a.addEventListener("click", (e) => { if (focusComposer()) e.preventDefault(); })
  );
  if (location.hash === "#composer") focusComposer();

  // Chat: start at the newest message
  const chat = document.querySelector(".thread");
  if (chat) chat.scrollTop = chat.scrollHeight;

  // Confirm before destructive actions
  document.addEventListener("submit", (e) => {
    const msg = e.target.dataset && e.target.dataset.confirm;
    if (msg && !confirm(msg)) e.preventDefault();
  });

  // Live character counter on the composer
  if (composer) {
    const counter = document.createElement("span");
    counter.className = "muted counter";
    composer.parentNode.querySelector(".composer-row").prepend(counter);
    const update = () => (counter.textContent = `${composer.value.length}/500`);
    composer.addEventListener("input", update);
    update();
  }
})();
