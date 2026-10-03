// Python Notatki: rzeczywista wysokość belki nagłówka jako zmienna CSS
// --pn-naglowek (extra.css, sekcja 7a: margines przewijania do kotwic).
// Skrypt działa tylko wtedy, gdy belka zawiera menu części (klasa
// pn-naglowek-czesci). Nawigacja natychmiastowa nie podmienia belki,
// a skrypty z extra_javascript wykonują się raz, więc wystarcza jeden
// obserwator zmian rozmiaru.
(function () {
  var belka = document.querySelector(".md-header.pn-naglowek-czesci");
  if (!belka || !("ResizeObserver" in window)) return;
  var ustaw = function () {
    document.documentElement.style.setProperty(
      "--pn-naglowek", belka.getBoundingClientRect().height + "px");
  };
  ustaw();
  new ResizeObserver(ustaw).observe(belka);
})();
