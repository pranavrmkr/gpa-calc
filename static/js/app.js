function activateTab(name, updateHash = false) {
    const panels = [...document.querySelectorAll("[data-panel]")];
    if (!panels.some(panel => panel.id === name)) name = "subjects";
    document.querySelector(".menu")?.setAttribute("role", "tablist");
    for (const panel of panels) {
        panel.hidden = panel.id !== name;
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", `menu-${panel.id}`);
    }
    for (const link of document.querySelectorAll(".menu [data-tab]")) {
        link.id = `menu-${link.dataset.tab}`;
        link.setAttribute("role", "tab");
        link.setAttribute("aria-controls", link.dataset.tab);
        link.setAttribute("tabindex", link.dataset.tab === name ? "0" : "-1");
        link.setAttribute("aria-selected", String(link.dataset.tab === name));
        link.setAttribute("aria-current", link.dataset.tab === name ? "page" : "false");
    }
    if (updateHash) history.replaceState(null, "", `#${name}`);
}

document.addEventListener("click", event => {
    const link = event.target.closest("[data-tab]");
    if (!link) return;
    event.preventDefault();
    activateTab(link.dataset.tab, true);
});
document.addEventListener("keydown", event => {
    const link = event.target.closest(".menu [data-tab]");
    if (!link || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const links = [...document.querySelectorAll(".menu [data-tab]")];
    const index = links.indexOf(link);
    const next = event.key === "Home" ? 0 : event.key === "End" ? links.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + links.length) % links.length;
    activateTab(links[next].dataset.tab, true);
    links[next].focus({ preventScroll: true });
});
window.addEventListener("hashchange", () => activateTab(location.hash.slice(1)));
activateTab(location.hash.slice(1));

let saving = false;

function showStatus(message, isError = false) {
    let status = document.getElementById("save-status");
    if (!status) {
        status = document.createElement("div");
        status.id = "save-status";
        status.setAttribute("aria-live", "polite");
        document.body.append(status);
    }
    status.className = isError ? "save-status is-error" : "save-status";
    status.setAttribute("role", isError ? "alert" : "status");
    status.textContent = message;
}

function captureDrafts(excludeForm = null) {
    return [...document.querySelectorAll("form")].filter(form => form !== excludeForm).flatMap(form =>
        [...form.elements].filter(field => field.name && field.dataset.dirty === "true").map(field => ({
            action: form.getAttribute("action"), name: field.name, value: field.value,
        }))
    );
}

function restoreDrafts(drafts) {
    for (const draft of drafts) {
        const form = [...document.forms].find(form => form.getAttribute("action") === draft.action);
        const field = form?.elements.namedItem(draft.name);
        if (field && "value" in field) {
            field.value = draft.value;
            field.dataset.dirty = "true";
        }
    }
}

document.addEventListener("input", event => {
    if (event.target.form) event.target.dataset.dirty = "true";
});

document.addEventListener("submit", async event => {
    const form = event.target;
    if (form.method.toLowerCase() !== "post" || !form.closest("#calculator")) return;
    event.preventDefault();
    if (saving) return;
    saving = true;
    const data = new FormData(form);
    const submitter = event.submitter;
    const operation = submitter?.textContent.trim() || "Save";
    const action = form.getAttribute("action");
    const buttons = [...document.querySelectorAll("button")].map(button => [button, button.disabled]);
    const fields = [...form.elements].filter(field => field.tagName !== "BUTTON").map(field => [field, field.disabled]);
    for (const [button] of buttons) button.disabled = true;
    for (const [field] of fields) field.disabled = true;
    form.setAttribute("aria-busy", "true");
    showStatus("Saving...");
    try {
        const response = await fetch(form.action, {
            method: "POST", body: data, credentials: "same-origin", cache: "no-store",
        });
        const html = await response.text();
        const page = new DOMParser().parseFromString(html, "text/html");
        const next = page.getElementById("calculator");
        if (!response.ok || !next) {
            throw new Error(page.querySelector(".error-card p")?.textContent.trim() || "Couldn't save. Check your connection and try again.");
        }
        const error = next.querySelector(".error-card")?.textContent.trim();
        const activeTab = document.querySelector(".menu [aria-selected='true']")?.dataset.tab || "subjects";
        const details = new Map([...document.querySelectorAll("details")].map(detail => [detail.id, detail.open]));
        const anchor = form.closest(".subject-card, article[id], [data-panel]");
        const anchorId = anchor?.id;
        const anchorTop = anchor?.getBoundingClientRect().top;
        const oldScroll = window.scrollY;
        const focused = document.activeElement;
        const focusAction = focused?.form?.getAttribute("action") || action;
        const focusedName = focused?.name;
        const drafts = action === "/clear" && !error ? [] : captureDrafts(error ? null : form);
        document.getElementById("calculator").replaceWith(next);
        for (const detail of document.querySelectorAll("details")) {
            if (details.has(detail.id)) detail.open = details.get(detail.id);
        }
        restoreDrafts(drafts);
        activateTab(activeTab);
        const updatedForm = [...document.forms].find(item => item.getAttribute("action") === focusAction);
        const focusTarget = focusedName ? updatedForm?.elements.namedItem(focusedName) : updatedForm?.querySelector("button");
        focusTarget?.focus({ preventScroll: true });
        const updatedAnchor = anchorId ? document.getElementById(anchorId) : null;
        const offset = updatedAnchor ? updatedAnchor.getBoundingClientRect().top - anchorTop : 0;
        window.scrollTo({ top: oldScroll + offset, behavior: "instant" });
        const notice = next.querySelector(".notice-card")?.textContent.trim();
        showStatus(error || notice || (operation.includes("Delete") ? "Deleted." : operation.includes("Calculate") ? "GPA updated." : "Saved."), Boolean(error));
    } catch (error) {
        showStatus(error.message || "Couldn't confirm the save. Your input is still here; check your connection before trying again.", true);
    } finally {
        for (const [button, disabled] of buttons) button.disabled = disabled;
        for (const [field, disabled] of fields) field.disabled = disabled;
        form.removeAttribute("aria-busy");
        saving = false;
    }
});
