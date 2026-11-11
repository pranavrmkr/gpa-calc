function activateTab(name, updateHash = false) {
    const panels = [...document.querySelectorAll("[data-panel]")];
    if (!panels.some(panel => panel.id === name)) name = "subjects";
    for (const panel of panels) panel.hidden = panel.id !== name;
    for (const link of document.querySelectorAll(".menu [data-tab]")) {
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
window.addEventListener("hashchange", () => activateTab(location.hash.slice(1)));
activateTab(location.hash.slice(1));
