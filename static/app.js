// EduGenie AI frontend interactions

const tools = document.querySelectorAll(".tool-tile");
const tips = document.querySelectorAll(".tip-pill");
const tipsCard = document.getElementById("tipsCard");
const modeContent = document.getElementById("modeContent");
const workspace = document.getElementById("workspace");
const getStartedBtn = document.getElementById("getStartedBtn");

const state = {
    mode: "study",
    feature: "Explain",
};

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderEmptyState() {
    return `
        <div class="empty-state">
            <div class="empty-icon">
                <i class="fa-solid fa-wand-magic-sparkles"></i>
            </div>
            <h2>Ready when you are</h2>
            <p>Select a tool, enter a topic, then generate your study output here.</p>
        </div>
    `;
}

function renderLoading(isReminder) {
    modeContent.innerHTML = `
        <div class="panel-inner">
            <div class="loading">
                <div class="loader"></div>
                <div>
                    <strong>${isReminder ? "Sending reminder to n8n" : "Generating your study material"}</strong>
                    <p>${isReminder ? "Handing off the reminder details for Gmail delivery..." : "Reading the prompt and preparing a structured answer..."}</p>
                </div>
            </div>
        </div>
    `;
}

function renderStudyView() {
    modeContent.innerHTML = `
        <div class="panel-head">
            <div>
                <p class="panel-label">Answer area</p>
                <h3 id="title">${escapeHtml(state.feature)}</h3>
            </div>
            <button id="copyBtn" class="icon-btn" title="Copy response">
                <i class="fa-regular fa-copy"></i>
            </button>
        </div>

        <div id="response" class="response-canvas">
            ${renderEmptyState()}
        </div>

        <div class="prompt-panel">
            <div class="prompt-head">
                <div>
                    <p class="panel-label">Question / topic</p>
                    <h4>Write what you want help with</h4>
                </div>
                <span class="keyboard-hint">Ctrl + Enter</span>
            </div>

            <div class="field-stack">
                <textarea id="prompt" placeholder="${escapeHtml(getPlaceholderForFeature(state.feature))}"></textarea>

                <div class="prompt-footer">
                    <select id="difficulty" aria-label="Difficulty">
                        <option>Beginner</option>
                        <option>Intermediate</option>
                        <option>Advanced</option>
                    </select>

                    <button id="generateBtn" class="primary-btn">
                        Generate
                    </button>
                </div>
            </div>
        </div>
    `;

    bindStudyHandlers();
}

function renderReminderView() {
    modeContent.innerHTML = `
        <div class="prompt-panel reminder-panel">
            <div class="prompt-head">
                <div>
                    <p class="panel-label">Reminder details</p>
                    <h4>Send a Gmail reminder</h4>
                </div>
            </div>

            <div class="reminder-grid">
                <div class="reminder-field">
                    <label for="email">Gmail address</label>
                    <input id="email" type="email" placeholder="Enter your Gmail address" autocomplete="email">
                </div>

                <div class="reminder-field">
                    <label for="reminderTime">Reminder time</label>
                    <input id="reminderTime" type="time">
                </div>

                <div class="reminder-field reminder-field--full">
                    <label for="reminder">What do you want to be reminded of?</label>
                    <textarea id="reminder" placeholder="Example: Remind me to revise biology chapter 4 before the test"></textarea>
                </div>

                <div class="prompt-footer reminder-footer reminder-field--full">
                    <button id="remindBtn" class="primary-btn">
                        Remind me
                    </button>
                </div>
            </div>
        </div>
    `;

    bindReminderHandlers();
}

function getPlaceholderForFeature(feature) {
    switch (feature) {
        case "Notes":
            return "Enter a chapter or subject for notes...";
        case "Quiz":
            return "Enter a topic for practice questions...";
        case "Flashcards":
            return "Enter a topic for flashcards...";
        case "Questions":
            return "Ask any academic question...";
        default:
            return "Enter a topic you want explained...";
    }
}

function setMode(mode, feature) {
    state.mode = mode;
    state.feature = feature;

    tipsCard.classList.toggle("hidden", mode === "reminder");
    workspace.classList.toggle("app-mode-reminder", mode === "reminder");
    workspace.classList.toggle("app-mode-study", mode !== "reminder");

    if (mode === "reminder") {
        renderReminderView();
    } else {
        renderStudyView();
    }
}

function bindStudyHandlers() {
    const response = document.getElementById("response");
    const title = document.getElementById("title");
    const prompt = document.getElementById("prompt");
    const difficulty = document.getElementById("difficulty");
    const generateBtn = document.getElementById("generateBtn");
    const copyBtn = document.getElementById("copyBtn");

    title.innerText = state.feature;

    generateBtn.onclick = async () => {
        const text = prompt.value.trim();

        if (!text) {
            alert("Enter a topic or question.");
            return;
        }

        const currentFeature = state.feature;
        renderLoading(false);

        const backendFeature = currentFeature === "Questions" ? "Explain" : currentFeature;

        try {
            const res = await fetch("/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    feature: backendFeature,
                    prompt: text,
                    difficulty: difficulty.value,
                }),
            });

            if (!res.ok) {
                throw new Error(`Request failed with ${res.status}`);
            }

            const data = await res.json();
            renderStudyView();
            const response = document.getElementById("response");
            response.innerHTML = marked.parse(data.response || "No response returned.");
        } catch (err) {
            renderStudyView();
            const response = document.getElementById("response");
            response.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                    </div>
                    <h2>Backend not responding</h2>
                    <p>Check whether the FastAPI server is running, then try again.</p>
                </div>
            `;
            console.log(err);
        }
    };

    copyBtn.onclick = async () => {
        try {
            await navigator.clipboard.writeText(response.innerText.trim());
        } catch (err) {
            console.log(err);
        }
    };

    prompt.addEventListener("keydown", e => {
        if (e.ctrlKey && e.key === "Enter") {
            generateBtn.click();
        }
    });
}

function bindReminderHandlers() {
    const email = document.getElementById("email");
    const reminderTime = document.getElementById("reminderTime");
    const reminder = document.getElementById("reminder");
    const remindBtn = document.getElementById("remindBtn");

    remindBtn.onclick = async () => {
        const emailValue = email.value.trim();
        const timeValue = reminderTime.value.trim();
        const reminderValue = reminder.value.trim();

        if (!emailValue) {
            alert("Enter your Gmail address.");
            return;
        }

        if (!timeValue) {
            alert("Choose a reminder time.");
            return;
        }

        if (!reminderValue) {
            alert("Tell us what you want to be reminded about.");
            return;
        }

        renderLoading(true);

        try {
            const res = await fetch("/remind", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: emailValue,
                    time: timeValue,
                    reminder: reminderValue,
                }),
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || `Request failed with ${res.status}`);
            }

            const data = await res.json();
            modeContent.innerHTML = `
                <div class="prompt-panel reminder-panel">
                    <div class="reminder-success">
                        <div class="empty-icon">
                            <i class="fa-solid fa-circle-check"></i>
                        </div>
                        <h2>${data.delivered ? "Reminder queued" : "Reminder captured"}</h2>
                        <p>${escapeHtml(data.response || "Reminder payload sent.")}</p>
                    </div>
                </div>
            `;
        } catch (err) {
            modeContent.innerHTML = `
                <div class="prompt-panel reminder-panel">
                    <div class="reminder-success">
                        <div class="empty-icon">
                            <i class="fa-solid fa-triangle-exclamation"></i>
                        </div>
                        <h2>Reminder flow failed</h2>
                        <p>${escapeHtml(err.message || "Check the backend and n8n webhook, then try again.")}</p>
                    </div>
                </div>
            `;
            console.log(err);
        }
    };

    reminder.addEventListener("keydown", e => {
        if (e.ctrlKey && e.key === "Enter") {
            remindBtn.click();
        }
    });
}

getStartedBtn.onclick = () => {
    document.getElementById("workspace").scrollIntoView({
        behavior: "smooth",
    });
};

tools.forEach(tool => {
    tool.onclick = () => {
        tools.forEach(item => item.classList.remove("active"));
        tool.classList.add("active");
        setMode(tool.dataset.mode || "study", tool.dataset.feature || "Explain");
    };
});

tips.forEach(tip => {
    tip.onclick = () => {
        const prompt = document.getElementById("prompt");
        if (prompt) {
            prompt.value = tip.dataset.tip;
            prompt.focus();
        }
    };
});

setMode("study", "Explain");
