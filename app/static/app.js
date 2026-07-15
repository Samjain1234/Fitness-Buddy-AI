/* ============================================================
   Fitness Buddy AI — Application JavaScript
   Handles SPA routing, API calls, chat, dashboard, and charts
   ============================================================ */

"use strict";

// ============================================================
// Global State
// ============================================================
const State = {
  userProfile: null,
  chatHistory: [],
  currentPage: "dashboard",
  workoutPlan: null,
  nutritionData: null,
  habitData: {},
  theme: localStorage.getItem("fb_theme") || "dark",
  isAITyping: false,
};

// ============================================================
// API Helpers
// ============================================================
const API = {
  base: "",

  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(this.base + path, opts);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.detail || err.error || "Request failed");
      }
      return res.json();
    } catch (e) {
      Toast.show(e.message, "error");
      throw e;
    }
  },

  get: (path) => API.request("GET", path),
  post: (path, body) => API.request("POST", path, body),
};

// ============================================================
// Toast Notifications
// ============================================================
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById("toastContainer");
  },

  show(message, type = "info", icon = null) {
    const icons = { success: "✅", error: "❌", info: "ℹ️" };
    const div = document.createElement("div");
    div.className = `toast-msg ${type}`;
    div.innerHTML = `<span>${icon || icons[type]}</span><span>${message}</span>`;
    this.container.appendChild(div);
    setTimeout(() => div.remove(), 3400);
  },
};

// ============================================================
// Theme Manager
// ============================================================
const ThemeManager = {
  apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    State.theme = theme;
    localStorage.setItem("fb_theme", theme);
    const btn = document.getElementById("themeToggle");
    if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
  },

  toggle() {
    this.apply(State.theme === "dark" ? "light" : "dark");
  },
};

// ============================================================
// SPA Router
// ============================================================
const Router = {
  pages: ["dashboard", "chat", "workout", "nutrition", "habits", "profile"],

  navigate(page) {
    if (!this.pages.includes(page)) return;
    document.querySelectorAll(".page-section").forEach((el) => el.classList.remove("active"));
    document.querySelectorAll(".nav-link").forEach((el) => el.classList.remove("active"));

    document.getElementById(`page-${page}`)?.classList.add("active");
    document.querySelector(`.nav-link[data-page="${page}"]`)?.classList.add("active");

    State.currentPage = page;

    // Load page-specific data
    const loaders = {
      dashboard: Dashboard.load,
      workout: Workout.maybeLoad,
      nutrition: Nutrition.maybeLoad,
      habits: Habits.load,
    };
    loaders[page]?.();
  },
};

// ============================================================
// Dashboard
// ============================================================
const Dashboard = {
  async load() {
    try {
      const stats = await API.get("/api/dashboard/stats");
      Dashboard.render(stats);
    } catch (e) {
      console.warn("Dashboard load failed:", e);
    }
  },

  render(stats) {
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    set("statStreak", stats.current_streak_days);
    set("statWorkouts", stats.total_workouts);
    set("statBMI", stats.bmi.toFixed(1));
    set("statBMILabel", stats.bmi_category);

    // BMI meter
    const bmiPct = Math.min(Math.max(((stats.bmi - 15) / (40 - 15)) * 100, 0), 100);
    const indicator = document.getElementById("bmiIndicator");
    if (indicator) indicator.style.left = bmiPct + "%";

    // Motivational quote
    if (stats.motivational_quote) {
      const [quote, ...authorParts] = stats.motivational_quote.split(" — ");
      const author = authorParts.join(" — ");
      const qEl = document.getElementById("dashQuote");
      const aEl = document.getElementById("dashQuoteAuthor");
      if (qEl) qEl.textContent = quote.replace(/^"|"$/g, "").replace(/^"/, "");
      if (aEl) aEl.textContent = "— " + (author || "Fitness Buddy");
    }

    // Weekly chart
    Dashboard.renderWeeklyChart(stats.weekly_progress || []);
    Dashboard.renderProgressRings(stats);
  },

  renderWeeklyChart(data) {
    const canvas = document.getElementById("weeklyChart");
    if (!canvas || !data.length) return;

    // Simple SVG bar chart (no external lib required)
    const svg = document.getElementById("weeklySVG");
    if (!svg) return;
    const W = svg.clientWidth || 400;
    const H = 100;
    const barW = Math.floor((W - 40) / 7) - 4;
    const maxSteps = Math.max(...data.map((d) => d.steps || 0), 1000);

    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.innerHTML = "";

    data.forEach((d, i) => {
      const x = 20 + i * (barW + 4);
      const pct = (d.steps || 0) / maxSteps;
      const barH = Math.max(4, pct * (H - 30));
      const y = H - barH - 20;
      const color = d.workout ? "#22c55e" : "#3b82f6";

      // Bar
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", x);
      rect.setAttribute("y", y);
      rect.setAttribute("width", barW);
      rect.setAttribute("height", barH);
      rect.setAttribute("rx", 3);
      rect.setAttribute("fill", color);
      rect.setAttribute("opacity", "0.8");
      svg.appendChild(rect);

      // Day label
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", x + barW / 2);
      text.setAttribute("y", H - 6);
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("font-size", "9");
      text.setAttribute("fill", "#64748b");
      const days = ["M", "T", "W", "T", "F", "S", "S"];
      text.textContent = days[i] || "";
      svg.appendChild(text);

      // Workout dot
      if (d.workout) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", x + barW / 2);
        circle.setAttribute("cy", y - 5);
        circle.setAttribute("r", 3);
        circle.setAttribute("fill", "#a855f7");
        svg.appendChild(circle);
      }
    });
  },

  renderProgressRings(stats) {
    const rings = [
      { id: "ringBMI", value: Math.min((stats.bmi / 30) * 100, 100), color: "#3b82f6" },
      { id: "ringStreak", value: Math.min((stats.current_streak_days / 30) * 100, 100), color: "#22c55e" },
      { id: "ringWorkouts", value: Math.min((stats.total_workouts / 50) * 100, 100), color: "#a855f7" },
    ];

    rings.forEach(({ id, value, color }) => {
      const el = document.getElementById(id);
      if (!el) return;
      const r = 40;
      const circ = 2 * Math.PI * r;
      el.style.strokeDasharray = circ;
      el.style.strokeDashoffset = circ - (value / 100) * circ;
      el.style.stroke = color;
    });
  },
};

// ============================================================
// Chat
// ============================================================
const Chat = {
  messagesEl: null,
  inputEl: null,
  typingEl: null,

  init() {
    this.messagesEl = document.getElementById("chatMessages");
    this.inputEl = document.getElementById("chatInput");
    this.typingEl = document.getElementById("typingIndicator");
    this.inputEl?.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        Chat.send();
      }
    });
    this.inputEl?.addEventListener("input", () => {
      this.inputEl.style.height = "auto";
      this.inputEl.style.height = this.inputEl.scrollHeight + "px";
    });
    document.querySelectorAll(".quick-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        this.inputEl.value = chip.textContent.trim();
        this.inputEl.focus();
      });
    });
  },

  addMessage(role, content) {
    const isUser = role === "user";
    const msg = { role, content, timestamp: new Date().toISOString() };
    State.chatHistory.push(msg);

    const div = document.createElement("div");
    div.className = `chat-message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = `message-avatar ${isUser ? "avatar-user" : "avatar-ai"}`;
    avatar.textContent = isUser ? "👤" : "🏋️";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = Chat.formatMarkdown(content);

    div.appendChild(avatar);
    div.appendChild(bubble);
    this.messagesEl.appendChild(div);
    this.scrollToBottom();
    return div;
  },

  formatMarkdown(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
      .replace(/^### (.*?)$/gm, "<h6>$1</h6>")
      .replace(/^## (.*?)$/gm, "<h5>$1</h5>")
      .replace(/^# (.*?)$/gm, "<h4>$1</h4>")
      .replace(/^[-*] (.*?)$/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul class="mb-1 ps-3">${m}</ul>`)
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");
  },

  showTyping() {
    this.typingEl.style.display = "flex";
    State.isAITyping = true;
    this.scrollToBottom();
  },

  hideTyping() {
    this.typingEl.style.display = "none";
    State.isAITyping = false;
  },

  scrollToBottom() {
    setTimeout(() => {
      this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }, 50);
  },

  async send() {
    const msg = this.inputEl?.value.trim();
    if (!msg || State.isAITyping) return;

    this.inputEl.value = "";
    this.inputEl.style.height = "auto";

    this.addMessage("user", msg);
    this.showTyping();

    const sendBtn = document.getElementById("sendBtn");
    if (sendBtn) sendBtn.disabled = true;

    try {
      const body = {
        message: msg,
        conversation_history: State.chatHistory.slice(-10),
        user_profile: State.userProfile || null,
      };
      const data = await API.post("/api/chat", body);
      this.hideTyping();
      this.addMessage("assistant", data.reply);
    } catch (e) {
      this.hideTyping();
      this.addMessage("assistant", "Sorry, I'm having trouble right now. Please try again. 💪");
    } finally {
      if (sendBtn) sendBtn.disabled = false;
    }
  },
};

// ============================================================
// Profile
// ============================================================
const Profile = {
  async load() {
    try {
      const data = await API.get("/api/profile");
      State.userProfile = data;
      Profile.render(data);
    } catch (e) {}
  },

  render(data) {
    const fields = [
      "name", "age", "gender", "height_cm", "weight_kg",
      "fitness_level", "fitness_goal", "diet_preference",
      "available_days_per_week", "available_minutes_per_session",
      "medical_conditions",
    ];
    fields.forEach((f) => {
      const el = document.getElementById(`pf_${f}`);
      if (el) el.value = data[f] ?? "";
    });

    // BMI display
    const bmiEl = document.getElementById("profileBMI");
    if (bmiEl && data.bmi) {
      bmiEl.textContent = `BMI: ${data.bmi.toFixed(1)} (${data.bmi_category})`;
    }
    const tdeeEl = document.getElementById("profileTDEE");
    if (tdeeEl && data.tdee) {
      tdeeEl.textContent = `TDEE: ~${Math.round(data.tdee)} kcal/day`;
    }
  },

  async save() {
    const body = {};
    ["name", "age", "gender", "height_cm", "weight_kg",
     "fitness_level", "fitness_goal", "diet_preference",
     "available_days_per_week", "available_minutes_per_session",
     "medical_conditions"].forEach((f) => {
      const el = document.getElementById(`pf_${f}`);
      if (!el) return;
      const numFields = ["age", "height_cm", "weight_kg", "available_days_per_week", "available_minutes_per_session"];
      body[f] = numFields.includes(f) ? parseFloat(el.value) : el.value;
    });

    try {
      const data = await API.post("/api/profile", body);
      State.userProfile = data;
      Profile.render(data);
      Toast.show("Profile saved successfully! 🎉", "success");
    } catch (e) {}
  },
};

// ============================================================
// Workout
// ============================================================
const Workout = {
  loaded: false,

  maybeLoad() {
    if (!Workout.loaded) Workout.load();
  },

  async load() {
    const btn = document.getElementById("generateWorkoutBtn");
    if (btn) btn.disabled = true;

    const workoutType = document.getElementById("wk_type")?.value || "home";
    const duration = parseInt(document.getElementById("wk_duration")?.value || "30");
    const level = document.getElementById("wk_level")?.value || "beginner";
    const goal = document.getElementById("wk_goal")?.value || "general_fitness";

    try {
      const data = await API.post("/api/workout/plan", {
        workout_type: workoutType,
        duration_minutes: duration,
        fitness_level: level,
        goal: goal,
      });
      State.workoutPlan = data;
      Workout.render(data);
      Workout.loaded = true;
    } catch (e) {
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  render(data) {
    const container = document.getElementById("workoutPlanContainer");
    const overview = document.getElementById("workoutOverview");
    const tips = document.getElementById("workoutTips");
    if (!container) return;

    if (overview) {
      overview.innerHTML = `<p class="mb-0">${Chat.formatMarkdown(data.weekly_overview || "")}</p>`;
    }

    if (tips) {
      tips.innerHTML = data.tips?.map((t) => `<li class="mb-1">${t}</li>`).join("") || "";
    }

    container.innerHTML = data.plan?.map((day) => Workout.renderDay(day)).join("") || "<p class='text-muted'>No plan generated.</p>";
  },

  renderDay(day) {
    const exercises = day.exercises
      .map(
        (ex) => `
        <div class="exercise-item">
          <div>
            <div class="exercise-name">${ex.name}</div>
            <div class="exercise-details">${ex.instructions}</div>
            ${ex.muscles_targeted?.length ? `<div class="mt-1">${ex.muscles_targeted.map((m) => `<span class="pill pill-blue me-1">${m}</span>`).join("")}</div>` : ""}
            ${ex.modifications ? `<div class="mt-1 fs-sm text-muted"><em>Modification: ${ex.modifications}</em></div>` : ""}
          </div>
          <div class="text-end">
            ${ex.sets ? `<div class="exercise-badge">${ex.sets} sets</div>` : ""}
            ${ex.reps ? `<div class="exercise-badge mt-1">${ex.reps} reps</div>` : ""}
            ${ex.duration_seconds ? `<div class="exercise-badge mt-1">${ex.duration_seconds}s</div>` : ""}
          </div>
        </div>`
      )
      .join("");

    return `
      <div class="workout-day-card glass-card">
        <div class="workout-day-header">
          <span>💪 ${day.day}</span>
          <span>${day.workout_type} · ${day.duration_minutes} min</span>
        </div>
        <div class="p-3">
          ${day.warm_up?.length ? `<div class="mb-3"><strong class="fs-sm text-muted text-uppercase">🔥 Warm-Up</strong><ul class="mt-1 ps-3 mb-0 fs-sm">${day.warm_up.map((w) => `<li>${w}</li>`).join("")}</ul></div>` : ""}
          <div class="mb-3">${exercises}</div>
          ${day.cool_down?.length ? `<div><strong class="fs-sm text-muted text-uppercase">❄️ Cool-Down</strong><ul class="mt-1 ps-3 mb-0 fs-sm">${day.cool_down.map((c) => `<li>${c}</li>`).join("")}</ul></div>` : ""}
          ${day.notes ? `<div class="mt-2 quote-card">${day.notes}</div>` : ""}
        </div>
      </div>`;
  },
};

// ============================================================
// Nutrition
// ============================================================
const Nutrition = {
  loaded: false,

  maybeLoad() {
    if (!Nutrition.loaded) Nutrition.load();
  },

  async load() {
    const btn = document.getElementById("generateNutritionBtn");
    if (btn) btn.disabled = true;

    const profile = State.userProfile;
    const body = {
      weight_kg: parseFloat(document.getElementById("nt_weight")?.value || profile?.weight_kg || 70),
      height_cm: parseFloat(document.getElementById("nt_height")?.value || profile?.height_cm || 170),
      age: parseInt(document.getElementById("nt_age")?.value || profile?.age || 25),
      gender: document.getElementById("nt_gender")?.value || profile?.gender || "other",
      activity_level: document.getElementById("nt_activity")?.value || "moderate",
      goal: document.getElementById("nt_goal")?.value || "general_fitness",
      diet_preference: document.getElementById("nt_diet")?.value || "vegetarian",
    };

    try {
      const data = await API.post("/api/nutrition/plan", body);
      State.nutritionData = data;
      Nutrition.render(data);
      Nutrition.loaded = true;
    } catch (e) {
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  render(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };

    set("ntCalories", Math.round(data.daily_calories));
    set("ntProtein",  `${data.macros.protein_g}g`);
    set("ntCarbs",    `${data.macros.carbs_g}g`);
    set("ntFat",      `${data.macros.fat_g}g`);
    set("ntWater",    `${(data.hydration_ml / 1000).toFixed(1)}L`);

    const total = data.macros.protein_g * 4 + data.macros.carbs_g * 4 + data.macros.fat_g * 9;
    const setWidth = (id, grams, cal_per_g) => {
      const el = document.getElementById(id);
      if (el) el.style.width = `${Math.round((grams * cal_per_g / total) * 100)}%`;
    };
    setWidth("macroProteinBar", data.macros.protein_g, 4);
    setWidth("macroCarbsBar", data.macros.carbs_g, 4);
    setWidth("macroFatBar", data.macros.fat_g, 9);

    // Meal plan
    const mealPlanEl = document.getElementById("mealPlanContainer");
    if (mealPlanEl && data.meal_plan) {
      const icons = { breakfast: "🌅", mid_morning: "🍎", lunch: "🍱", snack: "🥜", dinner: "🌙" };
      mealPlanEl.innerHTML = Object.entries(data.meal_plan).map(([meal, items]) => `
        <div class="mb-3">
          <div class="fw-600 mb-1">${icons[meal] || "🍽️"} ${meal.replace("_", " ").replace(/^\w/, (c) => c.toUpperCase())}</div>
          <ul class="ps-3 mb-0 fs-sm">${items.map((i) => `<li>${i}</li>`).join("")}</ul>
        </div>`).join("");
    }

    // Tips
    const tipsEl = document.getElementById("nutritionTips");
    if (tipsEl) {
      tipsEl.innerHTML = data.tips?.map((t) => `<li class="mb-1">💡 ${t}</li>`).join("") || "";
    }

    // Disclaimer
    const discEl = document.getElementById("nutritionDisclaimer");
    if (discEl) discEl.textContent = data.disclaimer;
  },
};

// ============================================================
// Habits Tracker
// ============================================================
const Habits = {
  async load() {
    try {
      const today = await API.get("/api/habits/today");
      const history = await API.get("/api/habits/history");
      Habits.renderForm(today);
      Habits.renderHistory(history.logs || []);
    } catch (e) {}
  },

  renderForm(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    set("hb_water", data.water_glasses || 0);
    set("hb_sleep", data.sleep_hours || 0);
    set("hb_steps", data.steps || 0);
    set("hb_mood", data.mood || 5);
    const wd = document.getElementById("hb_workout");
    if (wd) wd.checked = data.workout_done;
    const notesEl = document.getElementById("hb_notes");
    if (notesEl) notesEl.value = data.notes || "";

    Habits.updateMoodEmoji(data.mood || 5);
  },

  updateMoodEmoji(val) {
    const moods = ["😔", "😞", "😐", "🙂", "😊", "😄", "😁", "🤩", "💪", "🔥"];
    const el = document.getElementById("moodEmoji");
    if (el) el.textContent = moods[Math.min(Math.max(val - 1, 0), 9)];
    const lbl = document.getElementById("moodValue");
    if (lbl) lbl.textContent = val;
  },

  renderHistory(logs) {
    const container = document.getElementById("habitHistory");
    if (!container) return;
    if (!logs.length) {
      container.innerHTML = `<p class="text-muted fs-sm">No habit logs yet. Start tracking today!</p>`;
      return;
    }
    container.innerHTML = logs.slice(0, 14).map((log) => `
      <div class="d-flex justify-content-between align-items-center py-2 border-bottom" style="border-color:var(--border-glass)!important">
        <div>
          <span class="fw-600">${log.date}</span>
          <span class="pill pill-${log.workout_done ? "green" : "orange"} ms-2">${log.workout_done ? "Workout ✓" : "No Workout"}</span>
        </div>
        <div class="d-flex gap-3 fs-sm text-muted">
          <span>💧 ${log.water_glasses}x</span>
          <span>😴 ${log.sleep_hours}h</span>
          <span>👟 ${log.steps.toLocaleString()}</span>
          <span>${["😔","😞","😐","🙂","😊","😄","😁","🤩","💪","🔥"][Math.min(log.mood-1,9)]}</span>
        </div>
      </div>`).join("");
  },

  async save() {
    const body = {
      water_glasses: parseInt(document.getElementById("hb_water")?.value || 0),
      sleep_hours: parseFloat(document.getElementById("hb_sleep")?.value || 0),
      steps: parseInt(document.getElementById("hb_steps")?.value || 0),
      workout_done: document.getElementById("hb_workout")?.checked || false,
      mood: parseInt(document.getElementById("hb_mood")?.value || 5),
      notes: document.getElementById("hb_notes")?.value || "",
      date: new Date().toISOString().split("T")[0],
    };

    try {
      const data = await API.post("/api/habits/log", body);
      Toast.show(`Wellness score: ${data.wellness_score}/100 — ${data.feedback}`, "success", "🌟");
      await Habits.load();
    } catch (e) {}
  },
};

// ============================================================
// App Init
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  // Init
  Toast.init();
  ThemeManager.apply(State.theme);
  Chat.init();

  // Theme toggle
  document.getElementById("themeToggle")?.addEventListener("click", () => ThemeManager.toggle());

  // Nav links
  document.querySelectorAll(".nav-link[data-page]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      Router.navigate(link.dataset.page);
    });
  });

  // Quick prompts
  document.querySelectorAll(".quick-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const inputEl = document.getElementById("chatInput");
      if (inputEl) {
        inputEl.value = chip.textContent.trim();
        inputEl.focus();
      }
    });
  });

  // Send button
  document.getElementById("sendBtn")?.addEventListener("click", () => Chat.send());

  // Profile save
  document.getElementById("saveProfileBtn")?.addEventListener("click", () => Profile.save());

  // Workout generate
  document.getElementById("generateWorkoutBtn")?.addEventListener("click", () => {
    Workout.loaded = false;
    Workout.load();
  });

  // Nutrition generate
  document.getElementById("generateNutritionBtn")?.addEventListener("click", () => {
    Nutrition.loaded = false;
    Nutrition.load();
  });

  // Habit save
  document.getElementById("saveHabitsBtn")?.addEventListener("click", () => Habits.save());

  // Mood range input
  document.getElementById("hb_mood")?.addEventListener("input", (e) => {
    Habits.updateMoodEmoji(parseInt(e.target.value));
  });

  // Inline tab buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const group = btn.dataset.group;
      document.querySelectorAll(`.tab-btn[data-group="${group}"]`).forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(`.tab-content[data-group="${group}"]`).forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.target)?.classList.add("active");
    });
  });

  // Load initial data
  Profile.load().then(() => {
    Router.navigate("dashboard");
    // Send welcome message to chat
    setTimeout(() => {
      const name = State.userProfile?.name || "there";
      Chat.addMessage(
        "assistant",
        `👋 **Hey ${name}! Welcome to Fitness Buddy!**\n\nI'm your AI-powered personal fitness coach powered by **IBM Watsonx.ai Granite**. I'm here to help you with:\n\n- 💪 **Personalised Workout Plans** — home workouts, HIIT, yoga & more\n- 🥗 **Nutrition Guidance** — macro targets, Indian & international meal plans\n- 📊 **Progress Tracking** — stay consistent with habit tracking\n- 🎯 **Goal Setting** — build long-term healthy routines\n- 🧘 **Wellness Coaching** — stress relief, sleep, and mindfulness tips\n\nWhat fitness goal are we working on today? 🚀`
      );
    }, 500);
  });
});
