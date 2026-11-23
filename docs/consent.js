/* Google Analytics 4 dengan Consent Mode: tidak ada cookie analitik/iklan sebelum pengunjung setuju. */
(function () {
  var GA_ID = "G-2FW0MRB4H6";
  var KEY = "ceksaham-consent";
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  var granted = saved === "setuju";
  gtag("consent", "default", {
    ad_storage: granted ? "granted" : "denied",
    ad_user_data: granted ? "granted" : "denied",
    ad_personalization: granted ? "granted" : "denied",
    analytics_storage: granted ? "granted" : "denied",
  });
  gtag("js", new Date());
  gtag("config", GA_ID);

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
  document.head.appendChild(s);

  function choose(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
    var v = value === "setuju" ? "granted" : "denied";
    gtag("consent", "update", { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
    var b = document.getElementById("consent");
    if (b) b.remove();
  }

  function showBanner() {
    if (document.getElementById("consent")) return;
    var b = document.createElement("div");
    b.id = "consent";
    b.className = "consent";
    b.setAttribute("role", "dialog");
    b.setAttribute("aria-label", "Persetujuan cookie");
    b.innerHTML =
      '<p>Cek Saham memakai cookie Google Analytics untuk menghitung kunjungan dan, jika ada, cookie iklan Google. ' +
      'Cookie hanya dipasang jika Anda setuju. <a href="/kebijakan-privasi/">Baca kebijakan privasi</a>.</p>' +
      '<div class="consent-actions"><button type="button" data-v="tolak">Tolak</button>' +
      '<button type="button" data-v="setuju" class="primary">Setuju</button></div>';
    b.addEventListener("click", function (ev) {
      var v = ev.target && ev.target.getAttribute("data-v");
      if (v) choose(v);
    });
    document.body.appendChild(b);
  }

  window.cekSahamCookieSettings = showBanner;
  if (!saved) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", showBanner);
    else showBanner();
  }
})();
