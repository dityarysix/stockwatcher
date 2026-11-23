"use strict";

const POS = [
  ["aset", "Total aset"],
  ["pendapatan", "Pendapatan"],
  ["beban_usaha", "Beban usaha"],
  ["laba_bersih", "Laba (rugi) bersih"],
  ["liabilitas", "Utang (total liabilitas)"],
];
const STATUS = {
  lengkap: "Lengkap",
  sebagian: "Sebagian",
  tidak_dapat_diakses: "Situs tidak dapat diakses",
  belum_dikumpulkan: "Belum dikumpulkan",
};

let DATA = null;
const app = document.getElementById("app");

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
const tgl = (iso) => {
  if (!iso) return "";
  const [y, m, d] = iso.split("-").map(Number);
  return d ? `${d} ${bulan[m - 1]} ${y}` : `${bulan[m - 1]} ${y}`;
};

/* Satuan laporan -> pengali dan mata uang */
function unit(satuan) {
  const s = (satuan || "").toLowerCase();
  const usd = /usd|dolar|dollar|us\$/.test(s);
  const mult = /triliun/.test(s) ? 1e12 : /miliar|billion/.test(s) ? 1e9 : /juta|million/.test(s) ? 1e6 : /ribu|thousand/.test(s) ? 1e3 : 1;
  return { usd, mult };
}
const fmtNum = (n, digits) => n.toLocaleString("id-ID", { minimumFractionDigits: digits, maximumFractionDigits: digits });
function money(v, satuan) {
  if (v === null || v === undefined) return "–";
  const { usd, mult } = unit(satuan);
  const x = v * mult;
  const a = Math.abs(x);
  const sign = x < 0 ? "−" : "";
  if (usd) {
    if (a >= 1e9) return `${sign}US$${fmtNum(a / 1e9, 2)} miliar`;
    if (a >= 1e6) return `${sign}US$${fmtNum(a / 1e6, 1)} juta`;
    return `${sign}US$${fmtNum(a / 1e3, 0)} ribu`;
  }
  if (a >= 1e12) return `${sign}Rp${fmtNum(a / 1e12, 2)} T`;
  if (a >= 1e9) return `${sign}Rp${fmtNum(a / 1e9, 1)} M`;
  return `${sign}Rp${fmtNum(a / 1e6, 0)} jt`;
}
function change(cur, prev, colored = true) {
  if (cur == null || prev == null || prev === 0) return "";
  const p = ((cur - prev) / Math.abs(prev)) * 100;
  const cls = !colored ? "flat" : p >= 0 ? "up" : "down";
  return `<span class="d ${cls}">${p >= 0 ? "+" : "−"}${fmtNum(Math.abs(p), 1)}%</span>`;
}
const sources = (arr) => !arr || !arr.length ? "" :
  `<ul class="src">${arr.map((s) => `<li>Sumber: <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.judul)}</a>, diakses ${esc(tgl(s.diakses))}</li>`).join("")}</ul>`;

function statusNote(e) {
  if (e.status_data === "lengkap") return "";
  const msg = {
    sebagian: e.situs_diblokir ? "Situs resmi emiten ini tidak dapat dibaca otomatis, jadi aksi korporasi dan perubahan manajemen belum tersedia." : "Data emiten ini belum lengkap.",
    tidak_dapat_diakses: "Situs resmi emiten ini tidak dapat dibaca otomatis saat pengumpulan data.",
    belum_dikumpulkan: "Data emiten ini belum dikumpulkan.",
  }[e.status_data] || "";
  return `<p class="notice">${esc(msg)}${e.catatan ? " " + esc(e.catatan) : ""}</p>`;
}

/* ---------- Views ---------- */

function filtersHTML(withKind) {
  const sektor = [...new Set(DATA.emiten.map((e) => e.sektor))].sort();
  const kinds = withKind ? [...new Set(DATA.emiten.flatMap((e) => (e[withKind] || []).map((x) => x.jenis)))].sort() : [];
  return `<div class="filters" role="search">
    <input type="search" id="q" placeholder="Cari kode atau nama emiten" aria-label="Cari kode atau nama emiten">
    <select id="sektor" aria-label="Sektor"><option value="">Semua sektor</option>${sektor.map((s) => `<option>${esc(s)}</option>`).join("")}</select>
    ${withKind ? `<select id="jenis" aria-label="Jenis"><option value="">Semua jenis</option>${kinds.map((s) => `<option>${esc(s)}</option>`).join("")}</select>` : ""}
  </div>`;
}
function bindFilters(render) {
  ["q", "sektor", "jenis"].forEach((id) => { const el = document.getElementById(id); if (el) el.addEventListener("input", render); });
}
function matches(e) {
  const q = (document.getElementById("q")?.value || "").trim().toLowerCase();
  const s = document.getElementById("sektor")?.value || "";
  return (!q || e.kode.toLowerCase().includes(q) || e.nama.toLowerCase().includes(q)) && (!s || e.sektor === s);
}

function viewRingkasan() {
  const done = DATA.emiten.filter((e) => e.status_data !== "belum_dikumpulkan").length;
  app.innerHTML = `<h1>Ringkasan per emiten</h1>
    <p class="intro">${done} dari ${DATA.emiten.length} emiten sudah dikumpulkan datanya. Pilih kode emiten untuk melihat rincian dan sumbernya.</p>
    ${filtersHTML()}
    <table class="board"><thead><tr>
      <th scope="col">Emiten</th>
      <th scope="col" class="h-aksi">Aksi korporasi</th>
      <th scope="col" class="h-keu">Laba bersih (YoY)</th>
      <th scope="col" class="h-man">Perubahan manajemen</th>
    </tr></thead><tbody id="rows"></tbody></table>`;
  const render = () => {
    document.getElementById("rows").innerHTML = DATA.emiten.filter(matches).map((e) => {
      if (e.status_data === "belum_dikumpulkan") {
        return `<tr><td><a class="ticker" href="#/emiten/${e.kode}">${e.kode}</a><span class="co">${esc(e.nama)}</span></td>
          <td colspan="3" class="pending">Belum dikumpulkan</td></tr>`;
      }
      const ak = e.aksi_korporasi || [];
      const last = [...ak].sort((a, b) => (b.tanggal || "").localeCompare(a.tanggal || ""))[0];
      const lk = e.laporan_keuangan;
      const lb = lk?.pos?.laba_bersih;
      const mn = e.perubahan_manajemen || [];
      const blocked = e.status_data === "tidak_dapat_diakses" || e.situs_diblokir;
      return `<tr>
        <td><a class="ticker" href="#/emiten/${e.kode}">${e.kode}</a><span class="co">${esc(e.nama)}</span></td>
        <td data-l="Aksi korporasi">${blocked && !ak.length ? `<span class="pending">Situs resmi tidak dapat diakses</span>` : `<span class="cell-count">${ak.length} entri</span>`}${last ? `<span class="cell-sub">Terbaru: ${esc(last.judul)} (${tgl(last.tanggal)})</span>` : ""}</td>
        <td data-l="Laba bersih (YoY)">${lb ? `<span class="cell-count">${money(lb[0], lk.satuan)}</span> ${change(lb[0], lb[1])}<span class="cell-sub">${esc(lk.periode)}</span>` : `<span class="pending">Tidak tersedia</span>`}</td>
        <td data-l="Perubahan manajemen">${blocked && !mn.length ? `<span class="pending">Situs resmi tidak dapat diakses</span>` : `<span class="cell-count">${mn.length} entri</span>`}${mn[0] ? `<span class="cell-sub">${esc(mn[0].nama)}: ${esc(mn[0].jenis.toLowerCase())}</span>` : ""}</td>
      </tr>`;
    }).join("") || `<tr><td colspan="4" class="pending">Tidak ada emiten yang cocok dengan filter.</td></tr>`;
  };
  bindFilters(render); render();
}

function entryList(key, cls) {
  const kindSel = document.getElementById("jenis")?.value || "";
  const items = DATA.emiten.filter(matches).flatMap((e) => (e[key] || []).map((x) => ({ ...x, e })))
    .filter((x) => !kindSel || x.jenis === kindSel)
    .sort((a, b) => (b.tanggal || "").localeCompare(a.tanggal || "") || a.e.kode.localeCompare(b.e.kode));
  if (!items.length) return `<p class="empty">Belum ada entri yang cocok dengan filter ini.</p>`;
  return `<ol class="entries">${items.map((x) => `<li class="entry">
      <time datetime="${esc(x.tanggal)}">${tgl(x.tanggal)}</time>
      <div>
        <a class="who" href="#/emiten/${x.e.kode}">${x.e.kode}</a><span class="kind ${cls}">${esc(x.jenis)}</span>
        <h3>${esc(key === "perubahan_manajemen" ? `${x.nama}, ${x.jabatan}` : x.judul)}</h3>
        <p>${esc(x.ringkasan)}</p>
        ${sources(x.sumber)}
      </div></li>`).join("")}</ol>`;
}

function viewAksi() {
  app.innerHTML = `<h1>Aksi korporasi</h1>
    <p class="intro">Dividen, pembelian kembali saham, akuisisi, rights issue, dan aksi lain sejak 1 Januari 2026. Diurutkan dari yang terbaru.</p>
    ${filtersHTML("aksi_korporasi")}<div id="list"></div>`;
  const render = () => { document.getElementById("list").innerHTML = entryList("aksi_korporasi", "k-aksi"); };
  bindFilters(render); render();
}

function viewManajemen() {
  app.innerHTML = `<h1>Perubahan manajemen</h1>
    <p class="intro">Pengangkatan, pengunduran diri, dan pergantian direksi atau komisaris sejak 1 Januari 2026.</p>
    ${filtersHTML("perubahan_manajemen")}<div id="list"></div>`;
  const render = () => { document.getElementById("list").innerHTML = entryList("perubahan_manajemen", "k-man"); };
  bindFilters(render); render();
}

function viewKeuangan() {
  app.innerHTML = `<h1>Laporan keuangan</h1>
    <p class="intro">Laporan keuangan terbaru tiap emiten. Laba rugi dibandingkan dengan periode yang sama tahun lalu. Aset dan utang dibandingkan dengan akhir tahun buku sebelumnya. Untuk bank, pendapatan berarti pendapatan bunga dan beban usaha berarti beban operasional.</p>
    ${filtersHTML()}<div class="fin-wrap"><table class="fin"><thead><tr>
      <th scope="col">Emiten</th><th scope="col">Periode</th>
      ${POS.map(([, l]) => `<th scope="col" class="num">${l}</th>`).join("")}
    </tr></thead><tbody id="rows"></tbody></table></div>`;
  const render = () => {
    const rows = DATA.emiten.filter(matches).filter((e) => e.laporan_keuangan);
    document.getElementById("rows").innerHTML = rows.map((e) => {
      const lk = e.laporan_keuangan;
      return `<tr><td><a class="ticker" href="#/emiten/${e.kode}">${e.kode}</a><span class="co">${lk.format === "bank" ? "Format bank" : esc(e.sektor)}</span></td>
        <td>${esc(lk.periode)}<span class="co">${esc(lk.audit || "")}</span></td>
        ${POS.map(([k]) => { const v = lk.pos?.[k]; return `<td class="num">${v ? `<span class="v">${money(v[0], lk.satuan)}</span>${change(v[0], v[1], ["laba_bersih","pendapatan"].includes(k))}` : "–"}</td>`; }).join("")}
      </tr>`;
    }).join("") || `<tr><td colspan="7" class="pending">Belum ada laporan keuangan yang cocok dengan filter.</td></tr>`;
  };
  bindFilters(render); render();
}

function viewEmiten(kode) {
  const e = DATA.emiten.find((x) => x.kode === kode);
  if (!e) { app.innerHTML = `<p class="empty">Kode emiten ${esc(kode)} tidak ada di daftar. <a href="#/">Kembali ke ringkasan</a>.</p>`; return; }
  const lk = e.laporan_keuangan;
  const listOrEmpty = (arr, key, cls, empty) => arr && arr.length
    ? entryListFor(e, key, cls) : `<p class="empty">${empty}</p>`;
  app.innerHTML = `<div class="detail-head"><span class="big">${e.kode}</span><h1>${esc(e.nama)}</h1></div>
    <p class="detail-meta">${esc(e.sektor)}. Status data: ${STATUS[e.status_data] || e.status_data}.
      ${e.situs_resmi ? `Situs resmi: <a href="${esc(e.situs_resmi)}" target="_blank" rel="noopener">${esc(new URL(e.situs_resmi).hostname)}</a>` : ""}</p>
    ${statusNote(e)}
    <section class="section s-aksi"><h2>Aksi korporasi</h2>${listOrEmpty(e.aksi_korporasi, "aksi_korporasi", "k-aksi", "Tidak ada aksi korporasi yang ditemukan di situs resmi sejak 1 Januari 2026.")}</section>
    <section class="section s-keu"><h2>Laporan keuangan</h2>${lk ? `
      <table class="kv"><thead><tr><th scope="col">Pos</th><th scope="col" class="num">${esc(lk.periode)}</th><th scope="col" class="num">Pembanding</th><th scope="col" class="num">Perubahan</th></tr></thead><tbody>
      ${POS.map(([k, l]) => { const v = lk.pos?.[k]; const lab = lk.label?.[k] || l;
        const cmp = ["aset", "liabilitas"].includes(k) ? lk.pembanding_neraca : lk.pembanding_lr;
        return `<tr><th scope="row">${esc(lab)}</th><td class="num">${v ? money(v[0], lk.satuan) : "–"}</td>
          <td class="num">${v ? money(v[1], lk.satuan) : "–"}<span class="co">${esc(cmp || "")}</span></td><td class="num">${v ? change(v[0], v[1], ["laba_bersih","pendapatan"].includes(k)) : ""}</td></tr>`; }).join("")}
      </tbody></table>
      <p class="unit-note">${esc(lk.audit || "")}. Satuan di laporan asli: ${esc(lk.satuan)}. ${esc(lk.catatan || "")}</p>
      ${sources(lk.sumber)}` : `<p class="empty">Laporan keuangan terbaru belum ditemukan di situs resmi.</p>`}</section>
    <section class="section s-man"><h2>Perubahan manajemen</h2>${listOrEmpty(e.perubahan_manajemen, "perubahan_manajemen", "k-man", "Tidak ada perubahan manajemen yang ditemukan di situs resmi sejak 1 Januari 2026.")}</section>`;
}
function entryListFor(e, key, cls) {
  const items = [...e[key]].sort((a, b) => (b.tanggal || "").localeCompare(a.tanggal || ""));
  return `<ol class="entries">${items.map((x) => `<li class="entry">
    <time datetime="${esc(x.tanggal)}">${tgl(x.tanggal)}</time>
    <div><span class="kind ${cls}">${esc(x.jenis)}</span>
      <h3>${esc(key === "perubahan_manajemen" ? `${x.nama}, ${x.jabatan}` : x.judul)}</h3>
      <p>${esc(x.ringkasan)}</p>${sources(x.sumber)}</div></li>`).join("")}</ol>`;
}

/* ---------- Router ---------- */
function route() {
  const h = location.hash.replace(/^#\/?/, "");
  const [page, arg] = h.split("/");
  const tab = { "": "ringkasan", aksi: "aksi", keuangan: "keuangan", manajemen: "manajemen" }[page] ?? "";
  document.querySelectorAll(".tabs a").forEach((a) => { if (a.dataset.tab === tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  if (page === "emiten") viewEmiten((arg || "").toUpperCase());
  else if (page === "aksi") viewAksi();
  else if (page === "keuangan") viewKeuangan();
  else if (page === "manajemen") viewManajemen();
  else viewRingkasan();
  window.scrollTo(0, 0);
}

fetch("data/semua.json")
  .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then((d) => {
    DATA = d;
    document.getElementById("built").textContent = `Data terakhir dibangun ${tgl(d.dibangun)}.`;
    window.addEventListener("hashchange", route);
    route();
  })
  .catch(() => { app.innerHTML = `<p class="empty">Data gagal dimuat. Muat ulang halaman; jika masih gagal, periksa apakah file data/semua.json ada di repo.</p>`; });
