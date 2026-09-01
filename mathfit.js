// Hors de la Caverne — les formules en ligne trop larges pour leur colonne.
//
// Une seule formule plus large que la colonne fait déborder toute la page vers la
// droite sur un téléphone. Le CSS ne peut pas la reconnaître : cela dépend de sa
// largeur rendue. On mesure donc, après KaTeX, et seules celles-là deviennent des
// boîtes défilantes. `overflow` sur un bloc en ligne place sa ligne de base sur
// son bord inférieur : appliqué sans discernement, il remonterait visiblement
// *toutes* les formules du site (5 px mesurés). Réservé à celles qui débordent,
// l'effet ne se voit pas.
//
// Chargé partout où KaTeX l'est — y compris worksheet.html, dont les problèmes
// sont écrits après coup.
function hdlcFlagWideMath() {
  var list = Array.prototype.filter.call(
    document.querySelectorAll(".katex"),
    function (k) { return !k.closest(".katex-display"); });

  // Une formule masquée par un filtre mesure zéro : on ne sait rien d'elle. On
  // laisse alors son marquage tel quel plutôt que de l'effacer à tort — effacé,
  // il ne reviendrait qu'au prochain redimensionnement, et la page se remettrait
  // à déborder une fois le filtre levé.
  var live = [];
  list.forEach(function (k) {
    var block = k.closest("p, li, h3, div.statement, div.printhead");
    if (block && block.clientWidth) live.push([k, block]);
  });

  live.forEach(function (e) { e[0].classList.remove("wide-math"); });   // écritures
  var wide = live.filter(function (e) {                                 // puis lectures
    return e[0].getBoundingClientRect().width > e[1].clientWidth;
  });
  wide.forEach(function (e) { e[0].classList.add("wide-math"); });
}

// Version différée, appelée aussi par site.js quand un filtre vient de réafficher
// des problèmes jamais mesurés.
var hdlcRemeasureMath;

(function () {
  var t;
  hdlcRemeasureMath = function () {
    clearTimeout(t);
    t = setTimeout(hdlcFlagWideMath, 200);
  };
  function start() {
    hdlcFlagWideMath();
    window.addEventListener("resize", hdlcRemeasureMath);
  }
  window.addEventListener("load", function () {
    // Les polices de KaTeX peuvent manquer encore à « load » : mesurer avant
    // qu'elles arrivent donnerait les largeurs de la police de repli.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(start);
    else start();
  });
})();
