// Seleção de permissões: busca por texto e botão "Marcar todas" em cada módulo.
function iniciarPermissoes() {
  var grade = document.querySelector(".permissoes-grid");
  if (!grade) return;

  var busca = document.createElement("input");
  busca.type = "search";
  busca.placeholder = "Filtrar permissões...";
  busca.className = "permissoes-busca";
  grade.parentNode.insertBefore(busca, grade);

  busca.addEventListener("input", function () {
    var termo = busca.value.trim().toLowerCase();
    grade.querySelectorAll(".opcao").forEach(function (opcao) {
      var combina = opcao.textContent.toLowerCase().indexOf(termo) !== -1;
      opcao.style.display = combina ? "" : "none";
    });
  });

  // Atalhos: marcam exatamente o conjunto de permissões do perfil escolhido.
  document.querySelectorAll(".perfil").forEach(function (perfil) {
    perfil.addEventListener("click", function () {
      var ids = perfil.dataset.ids ? perfil.dataset.ids.split(",") : [];
      grade.querySelectorAll("input[type=checkbox]").forEach(function (caixa) {
        caixa.checked = ids.indexOf(caixa.value) !== -1;
      });
    });
  });

  grade.querySelectorAll("fieldset.grupo-permissoes").forEach(function (modulo) {
    var botao = document.createElement("button");
    botao.type = "button";
    botao.className = "marcar-grupo";
    botao.textContent = "Marcar todas";

    botao.addEventListener("click", function () {
      var caixas = modulo.querySelectorAll("input[type=checkbox]");
      var todasMarcadas = Array.prototype.every.call(caixas, function (c) { return c.checked; });
      caixas.forEach(function (c) { c.checked = !todasMarcadas; });
      botao.textContent = todasMarcadas ? "Marcar todas" : "Desmarcar todas";
    });

    modulo.querySelector("legend").appendChild(botao);
  });
}

// O script é carregado no cabeçalho, então espera a página montar a grade.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciarPermissoes);
} else {
  iniciarPermissoes();
}
