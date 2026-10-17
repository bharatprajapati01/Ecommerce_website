// Add-to-cart without a page reload, with graceful fallback to a normal POST.
(function () {
  const toast = document.getElementById("toast");
  const countEl = document.getElementById("cart-count");
  let timer;

  function showToast(text, isError) {
    toast.textContent = text;
    toast.classList.toggle("error", !!isError);
    toast.classList.add("show");
    clearTimeout(timer);
    timer = setTimeout(() => toast.classList.remove("show"), 2200);
  }

  document.querySelectorAll("form.js-add").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      try {
        const res = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest" },
          credentials: "same-origin",
        });
        if (!res.ok) throw new Error("Request failed");
        const data = await res.json();
        countEl.textContent = data.count;
        countEl.classList.remove("pop");
        void countEl.offsetWidth; // restart animation
        countEl.classList.add("pop");
        showToast(data.message);
      } catch (err) {
        form.submit(); // fall back to a normal page post
      } finally {
        btn.disabled = false;
      }
    });
  });

  // Category menu: opens on hover (pure CSS) on desktop; tap-to-open on touch screens.
  const menuItems = document.querySelectorAll(".cat-menu > li.has-sub");
  const isTouchLike = () => window.matchMedia("(hover: none) and (min-width: 801px)").matches;
  menuItems.forEach((li) => {
    li.querySelector(":scope > a").addEventListener("click", (e) => {
      if (!isTouchLike()) return; // desktop: link navigates normally
      if (!li.classList.contains("open")) {
        e.preventDefault(); // first tap opens the submenu
        menuItems.forEach((o) => o.classList.remove("open"));
        li.classList.add("open");
      }
    });
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".cat-menu")) menuItems.forEach((o) => o.classList.remove("open"));
  });

  // Themed dropdown: replaces the browser's native <select> popup (which can't be
  // styled) with a custom listbox. The real <select> stays in the DOM, so the form
  // still works, and the native control is the fallback if JS is unavailable.
  document.querySelectorAll("select.js-select").forEach((select) => {
    const wrap = document.createElement("div");
    wrap.className = "dd";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dd-btn";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");
    if (select.id) btn.setAttribute("aria-labelledby", `${select.id}-label`);

    const list = document.createElement("ul");
    list.className = "dd-list";
    list.setAttribute("role", "listbox");

    const items = [...select.options].map((opt, i) => {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.textContent = opt.textContent;
      li.addEventListener("mousedown", (e) => e.preventDefault()); // keep focus on button
      li.addEventListener("click", () => choose(i));
      li.addEventListener("mouseenter", () => setActive(i));
      list.appendChild(li);
      return li;
    });

    let active = select.selectedIndex;

    function paint() {
      btn.textContent = select.options[select.selectedIndex].textContent;
      items.forEach((li, i) => {
        li.classList.toggle("selected", i === select.selectedIndex);
        li.setAttribute("aria-selected", i === select.selectedIndex ? "true" : "false");
        li.classList.toggle("active", i === active);
      });
    }
    function setActive(i) {
      active = Math.max(0, Math.min(items.length - 1, i));
      paint();
    }
    function open() {
      wrap.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
      setActive(select.selectedIndex);
    }
    function close() {
      wrap.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    }
    function choose(i) {
      close();
      if (i === select.selectedIndex) return;
      select.selectedIndex = i;
      paint();
      if (select.form) select.form.submit();
    }

    btn.addEventListener("click", () => (wrap.classList.contains("open") ? close() : open()));
    btn.addEventListener("keydown", (e) => {
      const isOpen = wrap.classList.contains("open");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!isOpen) return open();
        setActive(active + (e.key === "ArrowDown" ? 1 : -1));
      } else if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        isOpen ? choose(active) : open();
      } else if (e.key === "Escape" || e.key === "Tab") {
        close();
      }
    });
    document.addEventListener("click", (e) => {
      if (!wrap.contains(e.target)) close();
    });

    select.classList.add("dd-native");
    select.setAttribute("tabindex", "-1");
    select.setAttribute("aria-hidden", "true");
    wrap.append(btn, list);
    select.after(wrap);
    paint();
  });

  // For You page: auto-sliding offer banners with dots.
  const hero = document.getElementById("hero-track");
  const dotsBox = document.getElementById("hero-dots");
  if (hero && dotsBox && hero.children.length) {
    let stops = [], dots = [], current = 0, timer = null;

    function measure() {
      const max = hero.scrollWidth - hero.clientWidth;
      const raw = [...hero.children].map((s) => Math.min(s.offsetLeft, max));
      stops = raw.filter((v, i) => raw.findIndex((x) => Math.abs(x - v) < 4) === i);
      dotsBox.innerHTML = "";
      dots = stops.map((_, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", `Offer ${i + 1}`);
        b.addEventListener("click", () => { go(i); restart(); });
        dotsBox.appendChild(b);
        return b;
      });
      mark();
    }
    function mark() {
      let best = 0;
      stops.forEach((v, i) => { if (Math.abs(v - hero.scrollLeft) < Math.abs(stops[best] - hero.scrollLeft)) best = i; });
      current = best;
      dots.forEach((d, i) => d.classList.toggle("on", i === best));
    }
    function go(i) { hero.scrollTo({ left: stops[i], behavior: "smooth" }); }
    function restart() { clearInterval(timer); timer = setInterval(() => go((current + 1) % stops.length), 4500); }

    hero.addEventListener("scroll", () => requestAnimationFrame(mark));
    hero.addEventListener("mouseenter", () => clearInterval(timer));
    hero.addEventListener("mouseleave", restart);
    hero.addEventListener("touchstart", () => clearInterval(timer), { passive: true });
    window.addEventListener("resize", measure);
    measure();
    if (stops.length > 1) restart();
  }

  const strip = document.getElementById("strip-track");
  const stripNext = document.getElementById("strip-next");
  if (strip && stripNext) {
    stripNext.addEventListener("click", () => {
      const atEnd = strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 4;
      strip.scrollTo({ left: atEnd ? 0 : strip.scrollLeft + strip.clientWidth * 0.8, behavior: "smooth" });
    });
  }

  // Account dropdown: opens on hover (CSS); tap/click toggles it for touch screens and keyboards.
  const acct = document.querySelector(".acct");
  if (acct) {
    const btn = acct.querySelector(".acct-btn");
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = acct.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", (e) => {
      if (!acct.contains(e.target)) { acct.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }
    });
  }

  // Wishlist hearts: toggle without reloading the page.
  document.querySelectorAll("form.js-wish").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector(".wish-btn");
      try {
        const res = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest" },
          credentials: "same-origin",
        });
        if (!res.ok) throw new Error("Request failed");
        const data = await res.json();
        btn.classList.toggle("on", data.on);
        btn.classList.remove("pop"); void btn.offsetWidth; btn.classList.add("pop");
        showToast(data.message);
        // On the wishlist page, un-hearting removes the card.
        const card = form.closest(".card");
        if (!data.on && card && card.closest("[data-wishlist]")) card.remove();
      } catch (err) {
        form.submit(); // fall back to a normal page post
      }
    });
  });

  // Auto-dismiss flash messages
  document.querySelectorAll(".messages .msg").forEach((m) => {
    setTimeout(() => (m.style.display = "none"), 5000);
  });
})();
