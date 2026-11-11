const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const vm = require("node:vm");
const source = readFileSync(require("node:path").join(__dirname, "../static/js/app.js"), "utf8");

function environment({ error = null, fail = false, wait = null } = {}) {
    const events = {};
    const requests = [];
    let state;
    let status;
    let replaced = false;
    const element = props => Object.assign({
        dataset: {}, disabled: false, attributes: {}, setAttribute(k, v) { this.attributes[k] = v; },
        removeAttribute(k) { delete this.attributes[k]; }, focus() { document.activeElement = this; },
    }, props);
    function page(saved = false) {
        const panels = ["subjects", "targets", "gpa", "settings"].map(id => element({ id }));
        const links = panels.map(panel => element({ dataset: { tab: panel.id } }));
        const detail = element({ id: "subject-1", open: !saved,
            getBoundingClientRect() { return { top: saved ? -240 : -250 }; } });
        const root = {
            id: "calculator", replaceWith(next) { state = next.state; replaced = true; },
            querySelector(selector) { return selector === ".error-card" && error ? { textContent: error } : null; },
        };
        const forms = ["/save", "/other"].map(action => {
            const form = element({ action, method: "post", getAttribute() { return action; },
                closest(selector) { return selector === "#calculator" ? root : detail; } });
            const field = element({ name: "score", tagName: "INPUT", value: saved ? "70" : "14/20", form });
            const button = element({ tagName: "BUTTON", textContent: "Save", form });
            form.elements = [field, button];
            form.elements.namedItem = name => form.elements.find(field => field.name === name);
            form.querySelector = () => button;
            return form;
        });
        const result = { root, panels, links, forms, detail };
        root.state = result;
        return result;
    }
    const old = page();
    const next = page(true);
    state = old;
    const document = {
        get forms() { return state.forms; },
        activeElement: old.forms[1].elements[0],
        addEventListener(name, fn) { events[name] = fn; },
        createElement() { return element({}); },
        body: { append(node) { status = node; } },
        getElementById(id) {
            if (id === "save-status") return status;
            if (id === "calculator") return state.root;
            if (id === "subject-1") return state.detail;
            return state.panels.find(panel => panel.id === id);
        },
        querySelector(selector) {
            if (selector.startsWith(".menu")) return state.links.find(link => link.attributes["aria-selected"] === "true");
        },
        querySelectorAll(selector) {
            if (selector === "[data-panel]") return state.panels;
            if (selector === ".menu [data-tab]") return state.links;
            if (selector === "form") return state.forms;
            if (selector === "details") return [state.detail];
            if (selector === "button") return state.forms.map(form => form.elements[1]);
            return [];
        },
    };
    const window = { scrollY: 600, addEventListener() {}, scrollTo(options) { this.scrollY = options.top; } };
    const context = vm.createContext({ document, window, location: { hash: "#targets" },
        history: { replaceState() {} },
        FormData: class { constructor(form) { this.values = form.elements.filter(f => f.name && !f.disabled).map(f => [f.name, f.value]); } },
        DOMParser: class { parseFromString() { return { getElementById: () => next.root }; } },
        fetch: async (url, options) => {
            requests.push({ url, options });
            if (wait) await wait;
            if (fail) throw new Error("Network unavailable");
            return { ok: true, text: async () => "rendered page" };
        },
    });
    vm.runInContext(source, context);
    for (const form of old.forms) events.input({ target: form.elements[0] });
    return { old, next, context, requests, document, window,
        get status() { return status; }, get replaced() { return replaced; },
        submit() { return events.submit({ target: old.forms[0], submitter: old.forms[0].elements[1], preventDefault() {} }); },
    };
}

test("save updates in place and keeps the tab, scroll, open card and another form's draft", async () => {
    const env = environment();
    await env.submit();
    assert.equal(env.replaced, true);
    assert.equal(env.requests.length, 1);
    assert.equal(env.requests[0].options.method, "POST");
    assert.deepEqual(env.requests[0].options.body.values, [["score", "14/20"]]);
    assert.equal(env.next.forms[0].elements[0].value, "70");
    assert.equal(env.next.forms[1].elements[0].value, "14/20");
    assert.equal(env.next.forms[1].elements[0].dataset.dirty, "true");
    assert.equal(env.next.panels.find(panel => !panel.hidden).id, "targets");
    assert.equal(env.next.detail.open, true);
    assert.equal(env.window.scrollY, 610);
    assert.equal(env.status.textContent, "Saved.");
});

test("validation errors keep the submitted input editable", async () => {
    const env = environment({ error: "Invalid marks" });
    await env.submit();
    assert.equal(env.next.forms[0].elements[0].value, "14/20");
    assert.equal(env.next.forms[0].elements[0].disabled, false);
    assert.equal(env.status.textContent, "Invalid marks");
    assert.equal(env.status.attributes.role, "alert");
});

test("network failure leaves the original forms and reenables controls", async () => {
    const env = environment({ fail: true });
    await env.submit();
    assert.equal(env.replaced, false);
    assert.equal(env.old.forms[0].elements[0].value, "14/20");
    assert.equal(env.old.forms[0].elements[0].disabled, false);
    assert.equal(env.old.forms[0].elements[1].disabled, false);
    assert.equal(env.status.textContent, "Network unavailable");
});

test("double submits send only one request", async () => {
    let release;
    const wait = new Promise(resolve => { release = resolve; });
    const env = environment({ wait });
    const first = env.submit();
    await env.submit();
    assert.equal(env.requests.length, 1);
    release();
    await first;
});

test("delete removes a row without leaving the current menu or losing drafts", async () => {
    const env = environment();
    env.old.forms[0].elements[1].textContent = "Delete";
    env.next.forms.shift();
    await env.submit();
    assert.equal(env.next.forms.length, 1);
    assert.equal(env.next.forms[0].elements[0].value, "14/20");
    assert.equal(env.next.panels.find(panel => !panel.hidden).id, "targets");
    assert.equal(env.status.textContent, "Deleted.");
});

test("clear discards other forms' unsaved drafts", async () => {
    const env = environment();
    env.old.forms[0].getAttribute = () => "/clear";
    await env.submit();
    assert.equal(env.next.forms[1].elements[0].value, "70");
});
