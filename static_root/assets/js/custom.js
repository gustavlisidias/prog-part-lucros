if (window.location.href.includes("entrar") || window.location.href.includes("forbidden")) {
    document.body.onload = function () {
        document.querySelector("body").setAttribute("class", "form-login");
    };
};

if (document.getElementById("search_painel")) {
    document.getElementById("search_painel").onclick = function () {
        document.getElementById("csrf_painel").remove();
        document.getElementById("form_painel").setAttribute("method", "GET");
        document.getElementById("form_painel").submit();
    };
};

if (document.getElementById("search_historico")) {
    document.getElementById("search_historico").onclick = function () {
        document.getElementById("csrf_painel").remove();
        document.getElementById("form_painel").setAttribute("method", "GET");
        document.getElementById("form_painel").submit();
    };
};

if (document.getElementById("search_regua")) {
    document.getElementById("search_regua").onclick = function () {
        document.getElementById("csrf_painel").remove();
        document.getElementById("form_painel").setAttribute("method", "GET");
        document.getElementById("form_painel").submit();
    };
};

if (document.getElementById("search_orcamento")) {
    document.getElementById("search_orcamento").onclick = function () {
        document.getElementById("csrf_orcamento").remove();
        document.getElementById("form_orcamento").setAttribute("method", "GET");
        document.getElementById("form_orcamento").submit();
    };

    document.getElementById("search_funcionario").onclick = function () {
        document.getElementById("csrf_funcionario").remove();
        document.getElementById("form_funcionario").setAttribute("method", "GET");
        document.getElementById("form_funcionario").submit();
    };
};