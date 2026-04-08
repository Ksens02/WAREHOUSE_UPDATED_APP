const statusEl = document.getElementById("status");
const rowCountEl = document.getElementById("row-count");
const tbody = document.getElementById("inventory-body");
const searchInput = document.getElementById("search");
const footerInfo = document.getElementById("footer-info");
const modalOverlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const itemForm = document.getElementById("item-form");

let allItems = [];
let sortCol = null;
let sortDir = "asc";
let editingId = null; // null = creating, number = editing

// --- Fetch & render ---

async function fetchInventory() {
  try {
    const res = await fetch("/inventory");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allItems = await res.json();
    statusEl.textContent = "connected";
    statusEl.className = "connection-status connected";
    renderTable(allItems);
    footerInfo.textContent = `${allItems.length} rows returned from inventory`;
  } catch (err) {
    statusEl.textContent = "error";
    statusEl.className = "connection-status error";
    footerInfo.textContent = `Error: ${err.message}`;
    tbody.innerHTML = `<tr><td colspan="9" class="no-results">Failed to load inventory: ${err.message}</td></tr>`;
  }
}

function getFiltered() {
  const q = searchInput.value.toLowerCase().trim();
  if (!q) return [...allItems];
  return allItems.filter(item =>
    Object.values(item).some(v =>
      String(v).toLowerCase().includes(q)
    )
  );
}

function getSorted(items) {
  if (!sortCol) return items;
  return items.sort((a, b) => {
    let va = a[sortCol];
    let vb = b[sortCol];
    if (va == null) va = "";
    if (vb == null) vb = "";
    if (typeof va === "number" && typeof vb === "number") {
      return sortDir === "asc" ? va - vb : vb - va;
    }
    va = String(va).toLowerCase();
    vb = String(vb).toLowerCase();
    if (va < vb) return sortDir === "asc" ? -1 : 1;
    if (va > vb) return sortDir === "asc" ? 1 : -1;
    return 0;
  });
}

function renderTable(items) {
  const filtered = getSorted(getFiltered());
  rowCountEl.textContent = `${filtered.length} rows`;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="no-results">No matching rows</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const zeroClass = item.quantity === 0 ? ' class="zero-qty"' : "";
    const sizeVal = item.size ?? "\u2014";
    const colorVal = item.color ?? "\u2014";
    return `<tr${zeroClass}>
      <td class="id-cell">${item.id}</td>
      <td>${esc(item.name)}</td>
      <td>${esc(item.category)}</td>
      <td>${esc(item.brand)}</td>
      <td class="${item.size == null ? 'dim' : ''}">${esc(sizeVal)}</td>
      <td class="${item.color == null ? 'dim' : ''}">${esc(colorVal)}</td>
      <td class="num">${item.quantity}</td>
      <td class="num price">${item.price.toFixed(2)}</td>
      <td class="actions-cell">
        <button class="btn-icon btn-edit" title="Edit" onclick="openEdit(${item.id})">&#9998;</button>
        <button class="btn-icon btn-delete" title="Delete" onclick="deleteItem(${item.id})">&#128465;</button>
      </td>
    </tr>`;
  }).join("");
}

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

// --- Modal ---

function openModal() {
  modalOverlay.classList.add("active");
}

function closeModal() {
  modalOverlay.classList.remove("active");
  itemForm.reset();
  editingId = null;
}

document.getElementById("btn-add").addEventListener("click", () => {
  editingId = null;
  modalTitle.textContent = "Add Item";
  document.getElementById("btn-save").textContent = "Create";
  itemForm.reset();
  openModal();
});

document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("btn-cancel").addEventListener("click", closeModal);
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

function openEdit(id) {
  const item = allItems.find(i => i.id === id);
  if (!item) return;
  editingId = id;
  modalTitle.textContent = "Edit Item";
  document.getElementById("btn-save").textContent = "Update";
  document.getElementById("f-name").value = item.name;
  document.getElementById("f-category").value = item.category;
  document.getElementById("f-brand").value = item.brand;
  document.getElementById("f-size").value = item.size ?? "";
  document.getElementById("f-color").value = item.color ?? "";
  document.getElementById("f-quantity").value = item.quantity;
  document.getElementById("f-price").value = item.price;
  openModal();
}

// --- CRUD ---

itemForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById("f-name").value,
    category: document.getElementById("f-category").value,
    brand: document.getElementById("f-brand").value,
    size: document.getElementById("f-size").value || null,
    color: document.getElementById("f-color").value || null,
    quantity: parseInt(document.getElementById("f-quantity").value, 10),
    price: parseFloat(document.getElementById("f-price").value),
  };

  try {
    let res;
    if (editingId != null) {
      res = await fetch(`/update/${editingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      res = await fetch("/inventory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    closeModal();
    await fetchInventory();
    footerInfo.textContent = editingId != null
      ? `Updated item #${editingId}`
      : "New item created";
  } catch (err) {
    footerInfo.textContent = `Error: ${err.message}`;
  }
});

async function deleteItem(id) {
  if (!confirm(`Delete item #${id}?`)) return;
  try {
    const res = await fetch(`/inventory/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await fetchInventory();
    footerInfo.textContent = `Deleted item #${id}`;
  } catch (err) {
    footerInfo.textContent = `Error: ${err.message}`;
  }
}

// --- Column sorting ---
const columns = ["id", "name", "category", "brand", "size", "color", "quantity", "price"];
document.querySelectorAll("th").forEach((th, i) => {
  if (i >= columns.length) return; // skip actions column
  th.addEventListener("click", () => {
    const col = columns[i];
    if (sortCol === col) {
      sortDir = sortDir === "asc" ? "desc" : "asc";
    } else {
      sortCol = col;
      sortDir = "asc";
    }
    document.querySelectorAll("th").forEach(h => h.classList.remove("sorted-asc", "sorted-desc"));
    th.classList.add(sortDir === "asc" ? "sorted-asc" : "sorted-desc");
    renderTable(allItems);
  });
});

searchInput.addEventListener("input", () => renderTable(allItems));

fetchInventory();
